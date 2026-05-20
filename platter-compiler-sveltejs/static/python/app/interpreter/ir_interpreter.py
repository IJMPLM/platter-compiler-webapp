"""
TAC Interpreter for Platter Language

Executes optimized Three Address Code (TAC) instructions directly in Python.
No assembly or machine code generation needed — runs the IR as a tree-walking
interpreter over the flat TAC instruction list.
"""
import math
import copy

from typing import List, Dict, Any, Optional
from app.intermediate_code.tac import (
    TACInstruction, TACAssignment, TACBinaryOp, TACUnaryOp,
    TACArrayAccess, TACArrayAssign, TACTableAccess, TACTableAssign,
    TACLabel, TACGoto, TACConditionalGoto, TACFunctionCall, TACParam,
    TACReturn, TACFunctionBegin, TACFunctionEnd, TACComment, TACAllocate,
    TACCast, TACNop
)


class InterpreterError(Exception):
    pass


class InputPauseSignal(Exception):
    """Raised when take() needs more user input than currently provided."""
    def __init__(self, message: str):
        self.message = message


class Frame:
    """A single call-stack frame with its own variable store."""
    def __init__(self, func_name: str, parent: "Frame | None" = None):
        self.func_name = func_name
        self.vars: Dict[str, Any] = {}
        self.parent = parent  # access global frame for globals

    def get(self, name: str) -> Any:
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise InterpreterError(f"Undefined variable '{name}'")

    def set(self, name: str, value: Any):
        # Only mutable collection values should write back to an outer frame.
        # Scalar assignments must stay local so recipe-local variables and loop
        # counters do not clobber outer scope variables with the same name.
        if name in self.vars:
            self.vars[name] = value
            return

        if isinstance(value, (list, dict)):
            frame = self.parent
            while frame is not None:
                if name in frame.vars:
                    frame.vars[name] = value
                    return
                frame = frame.parent

        # Variable doesn't exist locally (or shouldn't escape); create it here.
        self.vars[name] = value


class TACInterpreter:
    """
    Interprets a flat list of optimized TAC instructions.

    Execution model:
    - A program counter (pc) walks through instructions sequentially.
    - Labels are pre-indexed for O(1) jumps.
    - Functions are stored as {name: start_pc} tables.
    - A call stack of Frame objects handles variable scoping.
    - A param_stack accumulates arguments before CALL.
    - Built-in functions (topiece, tosip, tochars, bill, take, pow, sqrt, rand, size, etc.) are handled natively.
    """

    # ── Built-in functions ─────────────────────────────────────────────────────
    # Keys must match the exact token/function names used in Platter source code.
    # Semantics follow the Platter Documentation specification exactly.
    BUILTINS: Dict[str, Any] = {
        # Type conversions
        "topiece": None,  # handled in _call_builtin
        "tosip":   None,  # handled in _call_builtin
        "tochars": lambda args: ("up" if args[0] is True else ("down" if args[0] is False else str(args[0]))) if args else "",

        # Math, Formatting, Random
        "pow":     lambda args: args[0] ** args[1],                        # pow(base, exp) → piece
        "sqrt":    lambda args: round(args[0] ** 0.5, 7),                  # sqrt(piece) → sip, 7 fractional digits
        "fact":    None,  # handled in _call_builtin (factorial)
        "cut":     None,  # handled in _call_builtin (numeric formatting)
        "rand":    lambda args: round(__import__('random').random(), 7),    # rand() → sip 0.0000000–0.9999999, no args

        # String operation
        "copy":    None,  # handled in _call_builtin (chars slicing)

        # Collection ops — all serve NEW arrays, never mutate originals
        "size":    lambda args: len(args[0]) if args else 0,               # size(array) → piece
        "sort":    lambda args: sorted(args[0]),                           # sort(array) → new sorted array
        "reverse": lambda args: list(reversed(args[0])),                   # reverse(array) → new reversed array
        "append":  lambda args: args[0] + [args[1]],                       # append(array, val) → new array with val added
        "remove":  None,  # handled in _call_builtin (remove by index)
        "search":  None,  # handled in _call_builtin (return first matching index)
        "matches": None,  # handled in _call_builtin (deep equality → flag)

        # I/O — bill = print/output, take = input (handled specially in _call_builtin)
        "bill":    None,
        "take":    None,
    }

    def __init__(self, instructions: List[TACInstruction],
                 stdin_lines: Optional[List[str]] = None):
        """
        Args:
            instructions: Optimized TAC instruction list from IRGenerator.
            stdin_lines:  Optional list of strings fed to scan() calls instead
                          of blocking on real stdin (useful for web/Pyodide).
        """
        self.instructions = instructions
        self.output_lines: List[str] = []          # captured stdout
        self.stdin_lines = list(stdin_lines or [])  # pre-fed input
        self._stdin_idx = 0

        # Pre-process: build label→pc and function→pc maps
        self.label_map: Dict[str, int] = {}        # label_name → instruction index
        self.func_map: Dict[str, int] = {}         # func_name  → instruction index of FUNC_BEGIN

        for i, instr in enumerate(self.instructions):
            if isinstance(instr, TACLabel):
                self.label_map[instr.label] = i
            elif isinstance(instr, TACFunctionBegin):
                self.func_map[instr.func_name] = i

        # Build FUNC_BEGIN → FUNC_END skip map so we can jump over recipe bodies
        self.func_skip_map: Dict[int, int] = {}  # pc of FUNC_BEGIN → pc after FUNC_END
        depth = 0
        begin_pc = -1
        for i, instr in enumerate(self.instructions):
            if isinstance(instr, TACFunctionBegin):
                depth += 1
                if depth == 1:
                    begin_pc = i
            elif isinstance(instr, TACFunctionEnd):
                depth -= 1
                if depth == 0 and begin_pc >= 0:
                    self.func_skip_map[begin_pc] = i + 1  # resume after FUNC_END
                    begin_pc = -1

        # Runtime state
        self.pc: int = 0
        self.call_stack: List[Dict] = []   # saved frames for call/return
        self.param_stack: List[Any] = []   # params pushed before a CALL
        self.global_frame = Frame("__global__")
        self.current_frame: Frame = self.global_frame
        self._evaluating_for_bill: bool = False  # Phase 1: skip overflow checks during bill evaluation
        self.exit_code: Any = 0                   # Phase 3: exit code from serve statements
        self.exit_code_type: str = "piece"

    # ── Public entry point ─────────────────────────────────────────────────────

    def run(self) -> Dict[str, Any]:
        """
        Execute the program starting from pc=0.
        Global inits run first, then recipe bodies are skipped until 'start' is reached
        and executed inline.  Recipe calls go through _call_function as normal.
        Returns a summary dict with output, final global vars, and status.
        """
        if self.pc == 0 and "start" not in self.func_map:
            raise InterpreterError("No 'start' function found in IR.")

        try:
            self._execute()
        except InputPauseSignal as p:
            self.pc -= 1
            return {
                "success": False,
                "paused": True,
                "error": p.message,
                "output": "".join(self.output_lines),
                "stdin_consumed": self._stdin_idx,
                "globals": {k: v for k, v in self.global_frame.vars.items()
                            if not k.startswith("t")},
            }
        except (ValueError, TypeError) as e:
            return {
                "success": False,
                "paused": False,
                "error": self._translate_error(str(e)),
                "output": "".join(self.output_lines),
                "terminate_message": "Program terminated with error",
                "stdin_consumed": self._stdin_idx,
            }
        except InterpreterError as e:
            return {
                "success": False,
                "paused": False,
                "error": self._translate_error(str(e)),
                "output": "".join(self.output_lines),
                "terminate_message": "Program terminated with error",
                "stdin_consumed": self._stdin_idx,
            }

        return {
            "success": True,
            "paused": False,
            "output": "".join(self.output_lines),
            "exit_message": f"\nProgram ended with exit code {self._format_exit_code_display()}",
            "stdin_consumed": self._stdin_idx,
            "globals": {k: v for k, v in self.global_frame.vars.items()
                        if not k.startswith("t")},  # hide temps
        }

    # ── Main execution loop ────────────────────────────────────────────────────

    def _execute(self):
        while self.pc < len(self.instructions):
            instr = self.instructions[self.pc]

            # When scanning the top-level (we are in the global frame), skip over
            # recipe bodies — they will be executed only when called via _call_function.
            # The 'start' body is NOT skipped; it executes inline.
            if (isinstance(instr, TACFunctionBegin)
                    and self.current_frame is self.global_frame
                    and instr.func_name != "start"):
                skip_to = self.func_skip_map.get(self.pc)
                if skip_to is not None:
                    self.pc = skip_to
                    continue

            self.pc += 1
            self._dispatch(instr)

    def _dispatch(self, instr: TACInstruction):
        t = type(instr)

        if t is TACComment or t is TACNop or t is TACFunctionBegin or t is TACFunctionEnd:
            return  # no-ops

        elif t is TACLabel:
            return  # labels are markers, not actions

        elif t is TACAssignment:
            self._store(instr.result, self._load(instr.arg1))

        elif t is TACBinaryOp:
            left  = self._load(instr.arg1)
            right = self._load(instr.arg2)
            self._store(instr.result, self._eval_binary(instr.operator, left, right))

        elif t is TACUnaryOp:
            val = self._load(instr.arg1)
            self._store(instr.result, self._eval_unary(instr.operator, val))

        elif t is TACCast:
            val = self._load(instr.arg)
            self._store(instr.result, self._eval_cast(instr.target_type, val))

        elif t is TACAllocate:
            if instr.alloc_type == "array":
                size = int(self._load(instr.size))
                self._store(instr.result, [None] * size)
            else:  # table
                self._store(instr.result, {})

        elif t is TACArrayAccess:
            arr   = self._load(instr.array)
            index = int(self._load(instr.index))
            if not isinstance(arr, list):
                raise InterpreterError(f"'{instr.array}' is not an array")
            self._store(instr.result, arr[index])

        elif t is TACArrayAssign:
            arr   = self._load(instr.array)
            index = int(self._load(instr.index))
            val   = self._load(instr.value)
            if not isinstance(arr, list):
                raise InterpreterError(f"'{instr.array}' is not an array")
            # Store by value when assigning collections into array slots
            if isinstance(val, (list, dict)):
                arr[index] = copy.deepcopy(val)
            else:
                arr[index] = val

        elif t is TACTableAccess:
            tbl = self._load(instr.table)
            if not isinstance(tbl, dict):
                raise InterpreterError(f"'{instr.table}' is not a table")
            self._store(instr.result, tbl.get(instr.field))

        elif t is TACTableAssign:
            tbl = self._load(instr.table)
            val = self._load(instr.value)
            if not isinstance(tbl, dict):
                raise InterpreterError(f"'{instr.table}' is not a table")
            # Store by value when assigning collections into table fields
            if isinstance(val, (list, dict)):
                tbl[instr.field] = copy.deepcopy(val)
            else:
                tbl[instr.field] = val

        elif t is TACParam:
            self.param_stack.append(self._load(instr.arg))

        elif t is TACFunctionCall:
            args = self.param_stack[-instr.num_params:] if instr.num_params else []
            self.param_stack = self.param_stack[:-instr.num_params] if instr.num_params else self.param_stack

            if instr.func_name in self.BUILTINS:
                result = self._call_builtin(instr.func_name, args)
                if instr.result:
                    self._store(instr.result, result)
            else:
                if instr.func_name not in self.func_map:
                    raise InterpreterError(f"Undefined function '{instr.func_name}'")

                # Save caller state
                saved = {
                    "pc": self.pc,
                    "frame": self.current_frame,
                    "result_var": instr.result
                }
                self.call_stack.append(saved)

                # New frame — child of global so recipes can't see start's locals
                new_frame = Frame(instr.func_name, parent=self.global_frame)
                for i, val in enumerate(args):
                    new_frame.set(f"p{i}", val)
                self.current_frame = new_frame

                # Jump to function body (one past FUNC_BEGIN)
                self.pc = self.func_map[instr.func_name] + 1

        elif t is TACGoto:
            self.pc = self._resolve_label(instr.label)

        elif t is TACConditionalGoto:
            cond = self._load(instr.condition)
            cond_bool = self._to_bool(cond)
            jump = (not cond_bool) if instr.negated else cond_bool
            if jump:
                self.pc = self._resolve_label(instr.label)

        elif t is TACReturn:
            val = self._load(instr.value) if instr.value else None

            if not self.call_stack:
                # Phase 3: returning from the outermost recipe — capture typed exit code
                if val is not None:
                    self.exit_code = val
                    self.exit_code_type = self._platter_type_descriptor(val)
                self.pc = len(self.instructions)
            else:
                saved = self.call_stack.pop()
                self.pc = saved["pc"]
                self.current_frame = saved["frame"]
                if saved.get("result_var"):
                    self._store(saved["result_var"], val)

        else:
            pass  # unknown instruction — skip silently

    # ── Built-in functions execution ───────────────────────────────────────────

    def _process_string_literal(self, text: str) -> str:
        """Process escape sequences and remove quotes from string literals."""
        # If text is a quoted string literal, remove quotes
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        
        # Process escape sequences
        text = text.replace('\\n', '\n')   # \n -> newline
        text = text.replace('\\t', '\t')   # \t -> tab
        text = text.replace('\\\\', '\\')  # \\ -> backslash
        text = text.replace('\\"', '"')   # \" -> quote
        
        return text

    def _call_builtin(self, name: str, args: List[Any]) -> Any:
        fn = self.BUILTINS[name]

        # ── Type conversions ─────────────────────────────────────────────
        if name == "topiece":
            if not args:
                return 0
            try:
                result = int(float(args[0]))
                return result
            except (ValueError, TypeError):
                raise InterpreterError(
                    f"topiece(): cannot convert {self._platter_type(args[0])} value '{args[0]}' to piece"
                )

        elif name == "tosip":
            if not args:
                return 0.0
            try:
                result = float(args[0])
                return result
            except (ValueError, TypeError):
                raise InterpreterError(
                    f"tosip(): cannot convert {self._platter_type(args[0])} value '{args[0]}' to sip"
                )

        # ── I/O ──────────────────────────────────────────────────────────
        elif name == "bill":
            # Phase 1: bill(chars_value) → outputs text, serves ""
            # Flag allows bill to print any value without overflow errors
            self._evaluating_for_bill = True
            try:
                text = str(args[0]) if args else ""
                # Process escape sequences and remove quotes
                text = self._process_string_literal(text)
                self.output_lines.append(text)
            finally:
                self._evaluating_for_bill = False
            return ""

        elif name == "take":
            # take() → no flavors, awaits input, serves chars
            if self._stdin_idx < len(self.stdin_lines):
                val = str(self.stdin_lines[self._stdin_idx])
                
                # Platter only allows basic ASCII characters (no emojis, extended Unicode, etc.)
                if not all(ord(c) == 9 or ord(c) == 10 or ord(c) == 13 or (32 <= ord(c) <= 126) for c in val):
                    raise InterpreterError("Invalid input: take() received characters not allowed in the Platter language")
                    
                self._stdin_idx += 1
                self.output_lines.append(val + "\n")
                return val
            else:
                raise InputPauseSignal(
                    "Execution paused at take(): provide more runtime input lines and run again."
                )

        # ── Math/Formatting ──────────────────────────────────────────────
        elif name == "fact":
            # fact(non-negative piece) → piece (factorial)
            n = int(args[0])
            if n < 0:
                raise InterpreterError("fact() requires a non-negative piece value")
            result = 1
            for i in range(2, n + 1):
                result *= i
            # No overflow check — limits enforced at ingredient storage time
            return result

        elif name == "cut":
            # cut(sip_value, format_sip) → chars
            # format X.Y : X = digits before decimal, Y = digits after
            value = float(args[0])
            fmt = float(args[1])
            before = int(fmt)
            after  = int(round((fmt - before) * 10))
            neg = value < 0
            abs_val = abs(value)
            int_part = int(abs_val)
            frac_part = abs_val - int_part
            int_str = str(int_part).zfill(before)
            frac_str = f"{frac_part:.{after}f}"[2:]  # strip "0."
            result = f"{int_str}.{frac_str}" if after > 0 else int_str
            if neg:
                result = "-" + result
            return result

        elif name == "copy":
            # copy(chars, start_pos, end_pos) → chars (1-based inclusive)
            text = str(args[0])
            start = int(args[1])
            end = int(args[2])
            if start < 1 or end < 1 or start > len(text) or end > len(text):
                return ""
            return text[start - 1:end]

        # ── Collection ops ───────────────────────────────────────────────
        elif name == "remove":
            # remove(array, index) → new array with element at index removed
            arr = list(args[0])   # copy
            idx = int(args[1])
            if idx < 0 or idx >= len(arr):
                raise InterpreterError(f"remove() index {idx} out of range")
            arr.pop(idx)
            return arr

        elif name == "search":
            # search(array, value) → piece (first matching index, or -1)
            arr = args[0]
            val = args[1]
            for i, elem in enumerate(arr):
                if elem == val:
                    return i
            return -1

        elif name == "matches":
            # matches(array|table, array|table) → flag (up/down as bool)
            return args[0] == args[1]

        # ── Math functions (no overflow check — limits enforced at storage time) ─
        elif name == "pow":
            # pow(base, exp) → piece
            result = args[0] ** args[1]
            return result

        elif name == "sqrt":
            # sqrt(piece) → sip, 7 fractional digits
            result = round(args[0] ** 0.5, 7)
            return result

        # ── Generic lambda-based builtins ────────────────────────────────
        else:
            if fn is None:
                raise InterpreterError(f"Built-in '{name}' has no implementation")
            return fn(args)

    # ── Type name helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _platter_type(val: Any) -> str:
        """Return the Platter type name for a Python value."""
        if isinstance(val, bool):
            return "flag"
        if isinstance(val, int):
            return "piece"
        if isinstance(val, float):
            return "sip"
        if isinstance(val, str):
            return "chars"
        if isinstance(val, list):
            return "array"
        if isinstance(val, dict):
            return "table"
        return type(val).__name__

    def _platter_type_descriptor(self, val: Any) -> str:
        """Return a richer Platter type descriptor for output formatting."""
        if isinstance(val, list):
            if not val:
                return "array[]"
            first_type = self._platter_type(val[0])
            if all(self._platter_type(item) == first_type for item in val):
                return f"{first_type}[]"
            return "array"
        if isinstance(val, dict):
            return "table(obj)"
        return self._platter_type(val)

    def _format_platter_value(self, val: Any) -> str:
        """Format a runtime value using Platter-native literals."""
        if isinstance(val, bool):
            return "up" if val else "down"
        if isinstance(val, list):
            return "[" + ", ".join(self._format_platter_value(item) for item in val) + "]"
        if isinstance(val, dict):
            parts = []
            for key, item in val.items():
                parts.append(f"{key}: {self._format_platter_value(item)}")
            return "{" + ", ".join(parts) + "}"
        if isinstance(val, str):
            return val
        return str(val)

    def _format_exit_code_display(self) -> str:
        """Format top-level serve output without coercing values to integers."""
        exit_type = self.exit_code_type or self._platter_type_descriptor(self.exit_code)
        formatted_value = self._format_platter_value(self.exit_code)
        if exit_type in ("piece", "sip"):
            return formatted_value
        if exit_type in ("flag", "chars"):
            return formatted_value
        if exit_type.endswith("[]") or exit_type.startswith("table") or exit_type == "array":
            return f"{exit_type} {formatted_value}"
        return f"{exit_type} {formatted_value}"

    @staticmethod
    def _translate_error(msg: str) -> str:
        """Replace Python type names with Platter equivalents in error messages."""
        msg = msg.replace("could not convert string to float", "cannot convert chars to sip")
        msg = msg.replace("could not convert string to int", "cannot convert chars to piece")
        msg = msg.replace("invalid literal for int", "invalid piece value")
        msg = msg.replace(" float ", " sip ")
        msg = msg.replace(" float'", " sip'")
        msg = msg.replace("'float'", "'sip'")
        msg = msg.replace(" int ", " piece ")
        msg = msg.replace(" int'", " piece'")
        msg = msg.replace("'int'", "'piece'")
        msg = msg.replace(" str ", " chars ")
        msg = msg.replace(" str'", " chars'")
        msg = msg.replace("'str'", "'chars'")
        msg = msg.replace(" bool ", " flag ")
        msg = msg.replace(" bool'", " flag'")
        msg = msg.replace("'bool'", "'flag'")
        msg = msg.replace("string", "chars")
        return msg

    # ── Variable load / store ──────────────────────────────────────────────────

    def _load(self, name: str) -> Any:
        """Resolve a name or literal to a Python value."""
        if name is None:
            return None
        # Platter boolean literals: up = true, down = false
        if name == "up":
            return True
        if name == "down":
            return False
        # Also accept Python-style booleans from IR (generated by optimizer)
        if name in ("true", "True"):
            return True
        if name in ("false", "False"):
            return False
        # Numeric literals
        try:
            return int(name)
        except (ValueError, TypeError):
            pass
        try:
            return float(name)
        except (ValueError, TypeError):
            pass
        # String literals  "hello"
        if isinstance(name, str) and name.startswith('"') and name.endswith('"'):
            return name[1:-1]
        if isinstance(name, str) and name.startswith("'") and name.endswith("'"):
            return name[1:-1]
        # Variable lookup
        return self.current_frame.get(name)

    def _store(self, name: str, value: Any):
        # Phase 2: validate numeric limits before storing to a named ingredient.
        # Skip internal temp variables (they begin with 't') to allow large
        # intermediate values to exist during expression evaluation.
        # Ensure collections are stored by value (deep copy) to preserve
        # Platter's pass-by-value semantics for arrays/tables.
        if isinstance(value, (list, dict)):
            value = copy.deepcopy(value)

        if not name.startswith("t"):
            if isinstance(value, int) and not isinstance(value, bool):
                self._validate_piece_storage(value, name)
            elif isinstance(value, float):
                self._validate_sip_storage(value, name)
        self.current_frame.set(name, value)

    # ── Operator evaluation ────────────────────────────────────────────────────

    def _eval_binary(self, op: str, left: Any, right: Any) -> Any:
        ops = {
            "+": lambda a, b: (
                round(a + b, 7)
                if not (isinstance(a, str) or isinstance(b, str))
                else a + b
            ),
            "-": lambda a, b: round(a - b, 7),
            "*": lambda a, b: round(a * b, 7),
            # piece/piece → integer division (truncate toward zero, C-style)
            "/": lambda a, b: (
                int(a / b)
                if (isinstance(a, int) and not isinstance(a, bool)
                    and isinstance(b, int) and not isinstance(b, bool))
                else round(a / b, 7)
            ),
            "%":   lambda a, b: a % b,
            "==":  lambda a, b: a == b,
            "!=":  lambda a, b: a != b,
            ">":   lambda a, b: a > b,
            "<":   lambda a, b: a < b,
            ">=":  lambda a, b: a >= b,
            "<=":  lambda a, b: a <= b,
            "and": lambda a, b: a and b,
            "or":  lambda a, b: a or b,
        }
        if op not in ops:
            raise InterpreterError(f"Unknown binary operator '{op}'")
        try:
            result = ops[op](left, right)
            # Overflow is NOT checked here — arithmetic results may be large
            # (e.g. for bill expressions). Limits are enforced in _store() when
            # the value is actually assigned to a named ingredient.
            return result
        except ZeroDivisionError:
            raise InterpreterError("Division by zero")

    def _check_numeric_overflow(self, result: Any, left: Any, right: Any, op: str):
        """
        Check if arithmetic operation result exceeds numeric limits.
        piece: max 15 digits (±999,999,999,999,999)
        sip: max 15 non-fractional digits + 7 fractional digits
        """
        # Phase 1: skip overflow checks when evaluating expressions for bill statements
        if self._evaluating_for_bill:
            return
        # Determine result type based on operands
        left_is_int = isinstance(left, int) and not isinstance(left, bool)
        right_is_int = isinstance(right, int) and not isinstance(right, bool)
        left_is_float = isinstance(left, float)
        right_is_float = isinstance(right, float)
        
        # If both operands are integers, result type is piece
        if left_is_int and right_is_int and isinstance(result, int):
            self._check_piece_overflow(result)
        # If either operand is float, result type is sip
        elif (left_is_float or right_is_float) and isinstance(result, float):
            self._check_sip_overflow(result)
        # Integer division of piece/piece produces piece
        elif op == "/" and left_is_int and right_is_int and isinstance(result, int):
            self._check_piece_overflow(result)
    
    def _check_piece_overflow(self, value: int):
        """Check if piece (integer) exceeds 15 digits"""
        # Max 15 digits: ±999,999,999,999,999
        PIECE_MAX = 999_999_999_999_999
        if abs(value) > PIECE_MAX:
            raise InterpreterError("piece overflow")
    
    def _check_sip_overflow(self, value: float):
        """Check if sip (float) exceeds 15 non-fractional + 7 fractional digits"""
        # Max non-fractional digits: 15 (±999,999,999,999,999)
        # Max fractional digits: 7
        # Due to floating-point precision issues, check digit count instead of magnitude
        
        # Format with 7 decimal places to get proper representation
        value_str = f"{abs(value):.7f}"
        
        # Count non-fractional digits
        if '.' in value_str:
            integer_part = value_str.split('.')[0]
        else:
            integer_part = value_str
        
        non_fractional_digits = len(integer_part)
        
        if non_fractional_digits > 15:
            raise InterpreterError("sip overflow")

    # ── Phase 2: Storage-time validation helpers ───────────────────────────────

    def _validate_piece_storage(self, value: int, var_name: str = ""):
        """Validate piece ingredient: max 15 digits (±999,999,999,999,999)"""
        PIECE_MAX = 999_999_999_999_999
        if abs(value) > PIECE_MAX:
            raise InterpreterError("Value exceeds range for type piece")

    def _validate_sip_storage(self, value: float, var_name: str = ""):
        """Validate sip ingredient: max 15 non-fractional + 7 fractional digits"""
        value_str = f"{abs(value):.7f}"
        if '.' in value_str:
            integer_part = value_str.split('.')[0]
        else:
            integer_part = value_str
        non_fractional_digits = len(integer_part)
        if non_fractional_digits > 15:
            raise InterpreterError("Value exceeds range for type sip")

    def _eval_unary(self, op: str, val: Any) -> Any:
        if op == "-":
            result = -val
            # No overflow check — limits enforced at ingredient storage time
            return result
        if op in ("not", "!"):
            return not self._to_bool(val)
        raise InterpreterError(f"Unknown unary operator '{op}'")

    def _eval_cast(self, target_type: str, val: Any) -> Any:
        casts = {
            "piece": lambda v: int(float(v)),
            "sip":   lambda v: float(v),
            "chars": lambda v: str(v),
            "flag":  lambda v: bool(v),
        }
        if target_type not in casts:
            raise InterpreterError(f"Unknown cast type '{target_type}'")
        
        result = casts[target_type](val)
        # No overflow check — limits enforced at ingredient storage time
        return result

    def _to_bool(self, val: Any) -> bool:
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            # Platter: "down" = false, "up" = true
            return val.lower() not in ("down", "false", "0", "")
        return bool(val)

    def _resolve_label(self, label: str) -> int:
        if label not in self.label_map:
            raise InterpreterError(f"Undefined label '{label}'")
        return self.label_map[label]


# ── Convenience function ───────────────────────────────────────────────────────

def run_tac(instructions: List[TACInstruction],
            stdin_lines: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run optimized TAC instructions and return execution result.

    Args:
        instructions: Optimized TAC from OptimizerManager.optimize_tac()
        stdin_lines:  Optional pre-fed input lines for scan() calls.

    Returns:
        {
            "success": bool,
            "output":  str,          # captured print output
            "globals": dict,         # final values of named variables
            "error":   str | None,   # error message if not success
        }
    """
    interpreter = TACInterpreter(instructions, stdin_lines=stdin_lines)
    return interpreter.run()
