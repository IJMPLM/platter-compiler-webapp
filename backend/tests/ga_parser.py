import logging
import unittest
from app.lexer.lexer import Lexer
from app.parser.parser import Parser
from tests.syntax_tscripts import SYNTAX_TSCRIPTS

class TestParser(unittest.TestCase):
    def test_syntax_scripts(self):
        logging.getLogger().setLevel(logging.CRITICAL)
        for script in SYNTAX_TSCRIPTS:
            lexer = Lexer(script["code"])
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            expected_output = script["expected_output"]
            try:
                result = parser.parse()
                self.assertEqual(
                    "Syntax OK",
                    "Syntax OK"
                )
            except SyntaxError as e:
                try:
                    self.assertEqual(
                        e.msg,
                        expected_output
                    )
                except AssertionError as ae:
                    RED = '\033[91m'
                    YELLOW = '\033[93m'
                    RESET = '\033[0m'
                    print(f"\n{YELLOW}Failed for CODE #{script['number']}\nCODE:{script['code']}{RESET}")
                    print(f"{RED}AssertionError: {ae}{RESET}")

if __name__ == "__main__":
    unittest.main()