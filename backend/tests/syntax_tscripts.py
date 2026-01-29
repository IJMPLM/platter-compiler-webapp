SYNTAX_TSCRIPTS = [
  {
    "number": 1,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of a = 5, b = 3;
    bill(tochars((a*a + b*b) > 30));
}
    """
  },
  {
    "number": 2,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of x = 4, y = 9;
    x = x + y;
    y = x - y;
    x = x - y;
    bill(tochars(x) + " " + tochars(y));
}
    """
  },
  {
    "number": 3,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of n = 12345, c = 0;
    repeat(n != 0){
        c += 1;
        n /= 10;
    }
    bill(tochars(c));
}
    """
  },
  {
    "number": 4,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """table of P = [
    piece of x;
    piece of y;
];
start(){
    P of p = [x = 3; y = 7;];
    bill(tochars(p:x + p:y));
}
    """
  },
  {
    "number": 5,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of n = 123, r = 0;
    repeat(n != 0){
        r = r * 10 + n % 10;
        n /= 10;
    }
    bill(tochars(r));
}
    """
  },
  {
    "number": 6,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of n = 11;
    check(n % 2 != 0){
        bill("odd");
    } instead {
        bill("even");
    }
}
    """
  },
  {
    "number": 7,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of a = 3, b = 9, c = 6, m;
    check(a > b){
        check(a > c){ m = a; } instead { m = c; }
    } instead {
        check(b > c){ m = b; } instead { m = c; }
    }
    bill(tochars(m));
}
    """
  },
  {
    "number": 8,
    "actual_output": "Syntax Error: Unexpected ';' at line 9, col 19. Expected ].",
    "expected_output": "Syntax OK",
    "code":
    """table of S = [ piece of v; ];
start(){
    S[] of s = [
        [v = 1;], 
        [v = 2;], 
        [v = 3;]
    ];
    chars of printing = tochars(s[0]:v + s[1]:v + s[2]:v);
    bill(printing);
}
    """
  },
  {
    "number": 9,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of i = 65;
    repeat(i <= 69){
        bill(tochars(i) + " ");
        i += 1;
    }
}
    """
  },
  {
    "number": 10,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of n = 5, f = 1;
    repeat(n > 0){
        f *= n;
        n -= 1;
    }
    bill(tochars(f));
}
    """
  },
  {
    "number": 11,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of n = 121, t = n, r = 0;
    repeat(t != 0){
        r = r * 10 + t % 10;
        t /= 10;
    }
    bill(tochars(r == n));
}
    """
  },
  {
    "number": 12,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of x = 10;
    piece of p = x;
    bill(tochars(p + 5));
}
    """
  },
  {
    "number": 13,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of n = 13, c = 0;
    repeat(n > 0){
        c += n % 2;
        n /= 2;
    }
    bill(tochars(c));
}
    """
  },
  {
    "number": 14,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """table of A = [ piece of a; piece of b; ];
prepare piece of sum(A of x){
    serve x:a + x:b;
}
start(){
    A of t = [a = 4; b = 6;];
    bill(tochars(sum(t)));
}
    """
  },
  {
    "number": 15,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """table of Dim = [ piece of w; ];
table of Box = [ Dim of d; ];
start(){
    Box of b = [d = [w = 15;];];
    bill(tochars(b:d:w + 5));
}
    """
  },
  {
    "number": 16,
    "actual_output": "Syntax Error: Unexpected '-' at line 6, col 22. Expected 'not', '(', 'piece_lit', 'sip_lit', 'flag_lit', 'chars_lit', 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', '[', ')'.",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece of x = 7;
    check(x > 0){
        bill(tochars(x * x));
    } instead {
        bill(tochars(-x));
    }
}
    """
  },
  {
    "number": 17,
    "actual_output": "Syntax Error: Unexpected ';' at line 4, col 30. Expected ].",
    "expected_output": "Syntax OK",
    "code":
    """table of Item = [ piece of id; ];
start(){
    Item[] of list = [[id=10;], [id=20;]];
    bill(tochars(list[1]:id));
}
    """
  },
  {
    "number": 18,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start(){
    piece[] of a = [1, 2, 3];
    piece of i = 2;
    repeat(i >= 0){
        bill(tochars(a[i]) + " ");
        i -= 1;
    }
}
    """
  },
  {
    "number": 19,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """table of T = [ piece of v; ];
start(){
    T of a = [v = 5;], b = [v = 8;];
    bill(tochars(a:v < b:v));
}
    """
  },
  {
    "number": 20,
    "actual_output": "Syntax Error: Unexpected ';' at line 4, col 31. Expected ].",
    "expected_output": "Syntax OK",
    "code":
    """table of Node = [ piece of v; ];
start(){
    Node[] of nodes = [[v=1;], [v=2;], [v=3;]];
    bill(tochars(size(nodes)));
}
    """
  },
  {
    "number": 21,
    "actual_output": "Syntax Error: Unexpected 'piece' at line 2, col 10. Expected 'id'.",
    "expected_output": "Syntax Error: Unexpected 'piece' at line 2, col 10. Expected 'id'.",
    "code":
    """start(){
    pass(piece of i = 0; i += 3; i > 0){
        serve i;
    }
}
    """
  },
  {
    "number": 22,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """piece[][] of grid = [1, 2];

start(){
    serve grid[0][0];
}
    """
  },
  {
    "number": 23,
    "actual_output": "Syntax Error: Unexpected 'id' at line 5, col 14. Expected (.",
    "expected_output": "Syntax Error: Unexpected 'id' at line 5, col 14. Expected (.",
    "code":
    """start(){
    piece of x = 0;
    order{
        x += 1;
    } repeat x < 5;
    serve x;
}
    """
  },
  {
    "number": 24,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """piece of x = 5;

start(){
    piece of x = topiece(rand() * 3) + 1;
    chars of s = copy("CompilerDesign", 0, 8);
    serve x * size(s);
}
    """
  },
  {
    "number": 25,
    "actual_output": "Syntax Error: Unexpected token 'piece' after start platter, Expected EOF (line 4, col 1)",
    "expected_output": "Syntax Error: Unexpected token 'piece' after start platter, Expected EOF (line 4, col 1)",
    "code":
    """start(){
    serve 0;
}
piece of x = 3;
    """
  },
  {
    "number": 26,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start(){
    repeat(not x < 5){
        serve x;
    }
}
    """
  },
  {
    "number": 27,
    "actual_output": "Syntax Error: Unexpected 'serve' at line 2, col 1. Expected 'piece', 'sip', 'flag', 'chars', 'table', 'id', 'prepare', 'start'.",
    "expected_output": "Syntax Error: Unexpected 'serve' at line 2, col 1. Expected 'piece', 'sip', 'flag', 'chars', 'table', 'id', 'prepare', 'start'.",
    "code":
    """piece of x = 3;
serve x;
    """
  },
  {
    "number": 28,
    "actual_output": "Syntax Error: Unexpected 'serve' at line 4, col 7. Expected repeat.",
    "expected_output": "Syntax Error: Unexpected 'serve' at line 4, col 7. Expected repeat.",
    "code":
    """start(){
    order{
        serve 1;
    } serve 2;
    repeat(x < 3);
}
    """
  },
  {
    "number": 29,
    "actual_output": "Syntax Error: Unexpected 'usual' at line 7, col 9. Expected choice.",
    "expected_output": "No Syntax Error",
    "code":
    """piece of x = 2;

start(){
    menu(x){
        choice 1: serve 10;
        choice 2: serve 20;
        usual: serve 0;
    }
}
    """
  },
  {
    "number": 30,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start(){
    serve (x + 1) * (y - 2);
}
    """
  },
  {
    "number": 31,
    "actual_output": "Syntax Error: Unexpected 'id' at line 1, col 16. Expected ',', ';'.",
    "expected_output": "Syntax Error: Unexpected 'id' at line 1, col 16. Expected ',', ';'.",
    "code":
    """piece of x = 5 y;
start(){
    serve x;
}
    """
  },
  {
    "number": 32,
    "actual_output": "Syntax Error: Unexpected ',' at line 1, col 21. Expected ).",
    "expected_output": "Syntax Error: Unexpected '(' at line 1, col 20. Expected '['.",
    "code":
    """piece[] of nums = (1, 2, 3);

start(){
    serve nums[0];
}
    """
  },
  {
    "number": 33,
    "actual_output": "yntax Error: Unexpected 'stop' at line 3, col 5. Expected 'choice', 'usual', '}'.",
    "expected_output": "yntax Error: Unexpected 'stop' at line 3, col 5. Expected 'choice', 'usual', '}'.",
    "code":
    """start(){
    menu(x + 1){
    stop;
    }
}
    """
  },
  {
    "number": 34,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start(){
    pass(i = 0; i += 1; i < 3){
        serve i;
    }
}
    """
  },
  {
    "number": 35,
    "actual_output": "Syntax Error: Unexpected '{' at line 4, col 18. Expected '[', ':', '*', '/', '%', '+', '-', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', ',', ';', ')', '=', '+=', '-=', '*=', '/=', '%=', ']'.",
    "expected_output": "Syntax Error: Unexpected \"[\" at line 4, col 11. Expected '('.",
    "code":
    """piece of x = 3;

start(){
    repeat[x < 5]{
        serve x;
    }
}
    """
  },
  {
    "number": 36,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """table of Item = [
    piece of price;
];

Item of i = [
    price = 50;
];

start(){
    serve i:price + 10;
}
    """
  },
  {
    "number": 37,
    "actual_output": "Syntax Error: Unexpected '{' at line 1, col 8. Expected '[', 'of'.",
    "expected_output": "Syntax Error: Unexpected '[' at line 1, col 6. Expected '('.",
    "code":
    """start[]{
    serve 0;
}
    """
  },
  {
    "number": 38,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """prepare piece of inc(piece of x){
    serve x + 1;
}

start(){
    serve inc(3);
}
    """
  },
  {
    "number": 39,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """piece of x = 5;
sip of y = 2.5;

prepare chars of makeText(piece of a, sip of b){
    serve tochars(a + topiece(b));
}

start(){
    serve makeText(x, y);
}
    """
  },
  {
    "number": 40,
    "actual_output": "Syntax Error: Unexpected ':' at line 2, col 16. Expected ;.",
    "expected_output": "Syntax Error: Unexpected ':' at line 2, col 17. Expected '+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=', 'and', 'or', ')', ']', ';'.\n",
    "code":
    """start(){
    serve x + 1: 2;
}
    """
  },
  {
    "number": 41,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """piece[] of array = [0,1,2];
piece[] of integers = [1,2,3];
flag of enabled = up;
start(){
bill("flag is: " + tochars(2 - size(array) > integers[0] and enabled == up));
}
    """
  },
  {
    "number": 42,
    "actual_output": "Syntax Error: Unexpected 'piece_lit' at line 1, col 25. Expected 'id'.",
    "expected_output": "Syntax Error: Unexpected 'piece_lit' at line 1, col 25. Expected 'id'.",
    "code":
    """piece[] of integers = 1,2,3];
start(){
}
    """
  },
  {
    "number": 43,
    "actual_output": "Syntax Error: Unexpected 'tochars' at line 2, col 19. Expected ',', ')'.",
    "expected_output": "Follow set ng <primary_val>",
    "code":
    """start(){
bill("flag is: "  tochars(2));
}
    """
  },
  {
    "number": 44,
    "actual_output": "Syntax Error: Unexpected '+=' at line 2, col 19. Expected ;.",
    "expected_output": "Follow set ng <call_tail>",
    "code":
    """start(){
another = bill() += 23;
}
    """
  },
  {
    "number": 45,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start(){
bill(0-array + 2); # ganito lang pwede magnegative gg
}
    """
  },
  {
    "number": 46,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start(){
bill(tochars(topiece("32")-topiece(cut(12.56,2.0))));
}
    """
  },
  {
    "number": 47,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start(){
pass(a = 3; a-=1; a and 0){
}
}
    """
  },
  {
    "number": 48,
    "actual_output": "Syntax Error: Unexpected '}' at line 5, col 3. Expected choice.",
    "expected_output": "No Syntax Error",
    "code":
    """start() {
  menu(1) { 
    choice 1: rand(); stop; 
    choice 2: size(a); stop;
  }
}
    """
  },
  {
    "number": 49,
    "actual_output": "Syntax Error: Unexpected 'piece_lit' at line 1, col 33. Expected ',', ';'.",
    "expected_output": "Follow set ng <primary_val>",
    "code":
    """start() { piece of exprInit = 1 2; }
    """
  },
  {
    "number": 50,
    "actual_output": "Syntax Error: Unexpected ';' at line 1, col 35. Expected id.",
    "expected_output": "Syntax Error: Unexpected ';' at line 1, col 35. Expected id.",
    "code":
    """start() { tableType of m = field: ; }
    """
  },
  {
    "number": 51,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start() { piece[] of arr = [5,3,8,4,2]; piece of n = size(arr); pass(i=0; i+=1; i<n) { pass(j=0; j+=1; j<n-(1)) { check(arr[j] > arr[j+1]) { piece of temp = arr[j]; arr[j] = arr[j+1]; arr[j+1] = temp; } } } serve [arr]; }
    """
  },
  {
    "number": 52,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start() {
    piece[] of arr = [64,25,12,22,11];
    piece of n = size(arr);

    pass(i=0; i+=1; i<n-(1)) {
        piece of minIndex = i;
        piece of temp;
        pass(j=i+1; j+=1; j<n) {
            check(arr[j] < arr[minIndex]) {
                minIndex = j;
            }
        }
        temp = arr[minIndex];
        arr[minIndex] = arr[i];
        arr[i] = temp;
    }
    serve [arr];
}
    """
  },
  {
    "number": 53,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start() {
    piece[] of arr = [12,11,13,5,6];
    piece of n = size(arr);

    pass(i=1; i+=1; i<n) {
        piece of key = arr[i];
        piece of j = i-(1);

        repeat(j>=0 and arr[j] > key) {
            arr[j+1] = arr[j];
            j -= 1;
        }
        arr[j+1] = key;
    }
    serve [arr];
}
    """
  },
  {
    "number": 54,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start() {
    piece[] of arr = [2,4,6,8,10];
    piece of target = 6;
    piece of n = size(arr);

    pass(i=0; i+=1; i<n) {
        check(arr[i] == target) {
            serve [i];
            stop;
        }
    }
    serve [-1]; # not found
}
    """
  },
  {
    "number": 55,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start() {
    piece[] of arr = [1,2,3,4,5,6,7,8,9];
    piece of target = 7;
    piece of low = 0;
    piece of high = size(arr)-(1);

    repeat(low <= high) {
        piece of mid = (low + high) / 2;
        check(arr[mid] == target) {
            serve [mid];
            stop;
        }
        alt(arr[mid] < target) {
            low = mid + 1;
        }
        instead {
            high = mid - 1;
        }
    }
    serve [-1];
}
    """
  },
  {
    "number": 56,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start() {
    piece of n = 5;
    piece of result = 1;

    pass(i=1; i+=1; i<=n) {
        result *= i;
    }
    serve [result];
}
    """
  },
  {
    "number": 57,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start() {
    piece of n = 10;
    piece[] of fib = [0,1];

    pass(i=2; i+=1; i<n) {
        fib[i] = fib[i-(1)] + fib[i-(2)];
    }
    serve [fib];
}
    """
  },
  {
    "number": 58,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start() {
    piece of a = 48;
    piece of b = 18;

    repeat(b != 0) {
        piece of temp = b;
        b = a % b;
        a = temp;
    }
    serve [a];
}
    """
  },
  {
    "number": 59,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start() {
    piece of n = 29;
    flag of isPrime = up;

    pass(i=2; i+=1; i*i <= n) {
        check(n % i == 0) {
            isPrime = down;
            stop;
        }
    }
    serve [isPrime];
}
    """
  },
  {
    "number": 60,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """prepare piece[] of mergeSort(piece[] of arr) {
    piece of n;
    piece of mid;
    piece of i;
    piece[] of left;
    piece[] of right;
    piece[] of sortedLeft;
    piece[] of sortedRight;
    piece[] of result;

    n = size(arr);

    check(n <= (1)) {
        serve [arr];
    }

    mid = n / (2);
    left = [];
    right = [];

    # copy left half
    pass(i=0; i+=1; i<mid) {
        append(left, arr[i]);
    }

    # copy right half
    pass(i=mid; i+=1; i<n) {
        append(right, arr[i]);
    }

    sortedLeft = mergeSort(left);
    sortedRight = mergeSort(right);

    result = merge(sortedLeft, sortedRight);
    serve [result];
}

prepare piece[] of merge(piece[] of left, piece[] of right) {
    piece of i;
    piece of j;
    piece[] of merged;

    i = (0);
    j = (0);
    merged = [];

    pass(k=0; k+=1; k<size(left)+size(right)) {
        check(i < size(left) and (j >= size(right) or left[i] <= right[j])) {
            append(merged, left[i]);
            i += (1);
        }
        alt(j < size(right)) {
            append(merged, right[j]);
            j += (1);
        }
    }
    serve [merged];
}

start() {
    piece[] of arr;
    piece[] of sorted;

    arr = [38,27,43,3,9,82,10];
    sorted = mergeSort(arr);
    serve [sorted];
}
    """
  },
  {
    "number": 61,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected ';' at line 6, col 22. Expected ',', '=', ']'.",
    "code":
    """piece of x = 2;

table of Food = [piece of qty;];

start(){
  Food of hotdog = [a;];
    
  bill();
}
    """
  },
  {
    "number": 62,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected ';' at line 2, col 10. Expected 'of', '[', ':', '=', '+=', '-=', '*=', '/=', '%=', '('.",
    "code":
    """start(){
  prepare;){}
}
    """
  },
  {
    "number": 63,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected ';' at line 1, col 6. Expected '[', 'of'.",
    "code":
    """prepare(){}
start(){}
    """
  },
  {
    "number": 64,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected ';' at line 1, col 13. Expected 'not', '(', 'piece_lit', 'sip_lit', 'flag_lit', 'chars_lit', 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', '['.",
    "code":
    """iwag of a = ;
start(){}
    """
  },
  {
    "number": 65,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected ')' at line 2, col 25. Expected 'not', '(', 'piece_lit', 'sip_lit', 'flag_lit', 'chars_lit', 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip'.",
    "code":
    """piece of a; 
sip of b = ((3+5*2) and ) 5>10);
table of a = [
  piece of x;
];
start(){} 
}
    """
  },
  {
    "number": 66,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected 'piece' at line 1, col 14. Expected 'not', '(', 'piece_lit', 'sip_lit', 'flag_lit', 'chars_lit', 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip'.",
    "code":
    """piece of a = piece
start(){}
    """
  },
  {
    "number": 67,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected ':' at line 1, col 10. Expected 'not', '(', 'piece_lit', 'sip_lit', 'flag_lit', 'chars_lit', 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', '['.",
    "code":
    """a of a = :
start(){}
    """
  },
  {
    "number": 68,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected 'id' at line 3, col 12. Expected 'piece_lit', 'chars_lit'.",
    "code":
    """start(){
  menu(a){
    choice a:a:a:a:
  }
}
    """
  },
  {
    "number": 69,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected ':' at line 22, col 34. Expected ',', '=', ']'.",
    "code":
    """  
table of Student = [
  piece of Name;
    chars of Age;
];

start() {
  Student of Student1 = [
      Name = 1;
        Age = "Hello";
    ];
    
    Student of Student2 = [
      Name = 2;
        Age = "World";
    ];
    
  Student[] of Class = [
    
    ];
    
    chars[] of Class1 = [Student1:Name, Student1:Age];
    
  serve 0;
}
    """
  },
  {
    "number": 70,
    "actual_output": "",
    "expected_output": "Syntax OK",
    "code":
    """start() {
  piece of a = 5/2 + 13;
}
    """
  },
  {
    "number": 71,
    "actual_output": "",
    "expected_output": "Syntax OK",
    "code":
    """start() {
  piece of a = ((1.2/6) + bill());
}
    """
  },
  {
    "number": 72,
    "actual_output": "",
    "expected_output": "Syntax OK",
    "code":
    """piece[] of array = [0,1,2];
piece[] of integers = [1,2,3];
flag of enabled = up;
start(){
bill("flag is: " + tochars(2 - size(array) > integers[0] and enabled == up));
}
    """
  },
  {
    "number": 73,
    "actual_output": "",
    "expected_output": "Syntax OK",
    "code":
    """start() {
piece of x = 5;
piece of y = (x + 3);
ans = tochars(y);
bill(ans);
}
    """
  },
  {
    "number": 74,
    "actual_output": "",
    "expected_output": "Syntax OK",
    "code":
    """sip of pi = 3.14;

prepare sip of circumference(piece of r){
        serve 2*pi*r;
}

start(){
        sip of c = circumference(3);
        chars of ans = tochars(c);
        bill("The answer is: " + ans);
}
    """
  },
  {
    "number": 75,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected 'piece_lit' at line 3, col 25. Expected '(', '[', ':', '*', '/', '%', '+', '-', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', ',', ';', ')', ']'.",
    "code":
    """start(){
	sip of c = ((x*(x+1)*(x-2) - (3*x-5)*(x+4))*(x*x - 1)) / (((x-1)*(x-1) + (x+1)*(x+1))*(x*x + 1));
}
    """
  },
  {
    "number": 76,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected 'piece_lit' at line 1, col 27. Expected '(', '[', ':', '*', '/', '%', '+', '-', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', ',', ';', ')', ']'.",
    "code":
    """sip of a = (((x*(x+2) - (x-1)*(x-1))*(x*(x-3) + 5) + (2*x+1)*(x+4)) /
 ((x*(x-2) + (x+1)*(x+1))*(x+3)));
start(){}
    """
  },
  {
    "number": 77,
    "actual_output": "",
    "expected_output": "Syntax OK",
    "code":
    """sip of a = (pow(x+3,2)+sqrt(cut(y,1,5)+4)-fact(cut(n,1,6)))/(1+pow(copy(x,2)-rand(),2))
+sqrt(pow(cut(z,0,3),2)+copy(rand(),3));
start(){}
    """
  },
  {
    "number": 78,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected 'piece_lit' at line 1, col 18. Expected '(', '[', ':', '*', '/', '%', '+', '-', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', ',', ';', ')', ']'.",
    "code":
    """sip of a = (pow(x-1,2) + sqrt(cut(y,0,4)) - fact(cut(n,1,5))) / (1 + copy(rand(),2))
start(){}
    """
  },
  {
    "number": 79,
    "actual_output": "",
    "expected_output": "Syntax Error: Unexpected 'piece_lit' at line 1, col 23. Expected '(', '[', ':', '*', '/', '%', '+', '-', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', ',', ';', ')', ']'.",
    "code":
    """sip of a = ((x + pow(y-2,2))*(sqrt(cut(z,1,4)) - 1))
/
(1 + copy(rand(),2))
- fact(cut(n,1,4));

start(){}
    """
  },
  {
    "number": 80,
    "actual_output": "",
    "expected_output": "Syntax OK",
    "code":
    """sip of a = pow(x,2)/sqrt(cut(y,1,3)) + fact(n);
start(){}
    """
  },
  {
    "number": 81,
    "actual_output": "Syntax Error: Unexpected '}' at line 5, col 1. Expected ;.",
    "expected_output": "Syntax Error: Unexpected 'piece_lit' at line 5, col 1. Expected '(', '[', ':', '*', '/', '%', '+', '-', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', ',', ';', ')', ']'.",
    "code":
    """start() {
        piece of x = 12  + 13 ;
    sip of y = 123;
    serve 0
}
    """
  },
  {
    "number": 82,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """prepare piece of add2(piece of y) {
    serve y+2;
}

start() {
        piece of xd = add2(12) + add2(13);
    bill(tochars(xd));
}
    """
  },
  {
    "number": 83,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start() {
  repeat(x < 10) {
    x = x + 1;
    next;
    x = x + 999;  
    # comment ko
  }
}
    """
  },
  {
    "number": 84,
    "actual_output": "Syntax Error: Unexpected '=' at line 2, col 7. Expected ].",
    "expected_output": "Syntax Error: Unexpected '=' at line 2, col 7. Expected ].",
    "code":
    """start() {
  a[0 = 1;
}
    """
  },
  {
    "number": 85,
    "actual_output": "Syntax Error: Unexpected ';' at line 2, col 27. Expected 'of', '[', ':', '=', '+=', '-=', '*=', '/=', '%=', '('.",
    "expected_output": "Syntax Error: Unexpected ';' at line 2, col 27. Expected 'of', '[', ':', '=', '+=', '-=', '*=', '/=', '%=', '('.",
    "code":
    """prepare piece of serving () {
	serving of server; server; }

start() {
}
    """
  },
  {
    "number": 86,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start() {
  person:age = 19;
  person:name = "Floyd";
}
    """
  },
  {
    "number": 87,
    "actual_output": "Syntax Error: Unexpected 'start' at line 8, col 1. Expected ;.",
    "expected_output": "Syntax Error: Unexpected 'start' at line 8, col 1. Expected ;.",
    "code":
    """table of person = [
	piece of age;
    chars of name;

]


start() {}
    """
  },
  {
    "number": 88,
    "actual_output": "Syntax Error: Unexpected 'id' at line 2, col 23. Expected '(', '[', ':', '*', '/', '%', '+', '-', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', ',', ';', ')', ']'.",
    "expected_output": "Syntax Error: Unexpected 'id' at line 2, col 23. Expected ',', ';'.",
    "code":
    """start() {
  piece of badval = 1 value;
}
    """
  },
  {
    "number": 89,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start() {
  flag of expr = 1 - 23 > 12  and (up and down) * 12 * 1 * 2 % 12 / (1/2);
}
    """
  },
  {
    "number": 90,
    "actual_output": "Syntax Error: Unexpected ';' at line 2, col 27. Expected 'not', '(', 'piece_lit', 'sip_lit', 'flag_lit', 'chars_lit', 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip'.",
    "expected_output": "Syntax Error: Unexpected ';' at line 2, col 27. Expected 'not', '(', 'piece_lit', 'sip_lit', 'flag_lit', 'chars_lit', 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip'.",
    "code":
    """start() {
  piece of badexpr = 1 -  ;
}
    """
  },
  {
    "number": 91,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """prepare piece of add1() {
  x = x + 1;
}

prepare piece of add2() {
  add1();
  add1();
}

start() {
  x = 0;
  add2();
}
    """
  },
  {
    "number": 92,
    "actual_output": "Syntax Error: Unexpected '{' at line 3, col 3. Expected 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', 'check', 'menu', 'pass', 'repeat', 'order', 'next', 'stop', 'serve', '}', 'choice', 'usual'.",
    "expected_output": "Syntax Error: Unexpected '{' at line 3, col 3. Expected 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', 'check', 'menu', 'pass', 'repeat', 'order', 'next', 'stop', 'serve', '}', 'choice', 'usual'.",
    "code":
    """start() {
  x = 1;
  {
    y = x + 2;
  }
}
    """
  },
  {
    "number": 93,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start() {
  flag of ok = (a + b * 2) >= (c - 1) and not (d == 0) or e < 5;
}
    """
  },
  {
    "number": 94,
    "actual_output": "Syntax Error: Unexpected 'chars' at line 5, col 3. Expected 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', 'check', 'menu', 'pass', 'repeat', 'order', 'next', 'stop', 'serve', '}', 'choice', 'usual'.",
    "expected_output": "Syntax Error: Unexpected 'chars' at line 5, col 3. Expected 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', 'check', 'menu', 'pass', 'repeat', 'order', 'next', 'stop', 'serve', '}', 'choice', 'usual'.",
    "code":
    """start() {
  person of floy;
  floy:age = 19;
  floy:age = floy:age + 1;
  isAdult = floy:age >= 18;
  chars of x = tochars(isAdult); 
  bill(x);
}
    """
  },
  {
    "number": 95,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start() {
  pass( x = 0; x+=1 ; x>1) {
    sum = x + y + z;
  }
}
    """
  },
  {
    "number": 96,
    "actual_output": "Syntax Error: Unexpected 'flag_lit' at line 4, col 10. Expected 'id'.",
    "expected_output": "Syntax Error: Unexpected 'flag_lit' at line 4, col 10. Expected 'id'.",
    "code":
    """start() {
  repeat(true) {
    x = x + 1;
    pass(up) { stop; }
  }
}
    """
  },
  {
    "number": 97,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start() {
  x = 0;
  order {
    x = x + 2;
    y = x * 3;
    x+=1;
  } repeat(x < 6);
}
    """
  },
  {
    "number": 98,
    "actual_output": "Syntax Error: Unexpected 'id' at line 5, col 12. Expected (.",
    "expected_output": "Syntax Error: Unexpected 'id' at line 5, col 12. Expected (.",
    "code":
    """start() {
  order {
          piece of x = 1;
    x = x + 1;
  } repeat x < 3;
}
    """
  },
  {
    "number": 99,
    "actual_output": "Syntax OK",
    "expected_output": "Syntax OK",
    "code":
    """start() {
  sip of r = sqrt(9),  p = pow(2, 8);
  sip of n = rand();
}
    """
  },
  {
    "number": 100,
    "actual_output": "Syntax Error: Unexpected 'id' at line 6, col 23. Expected ;.",
    "expected_output": "Syntax Error: Unexpected 'id' at line 6, col 23. Expected '(', '[', ':', '*', '/', '%', '+', '-', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', ',', ';', ')', ']'.",
    "code":
    """table of animal = [ chars of sound; ];

start() {
        animal of pig;
    chars of cat = "meow";
    pig:sound = "cat" cat;
}
    """
  },
  {
    "number": 101,
    "actual_output": "Syntax Error: Unexpected '}' at line 3, col 1. Expected '[', ':', '*', '/', '%', '+', '-', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', ',', ';', ')', '=', '+=', '-=', '*=', '/=', '%=', ']'.\r",
    "expected_output": "Syntax Error: Unexpected '}' at line 3, col 1. Expected '[', ':', '*', '/', '%', '+', '-', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', ',', ';', ')', '=', '+=', '-=', '*=', '/=', '%=', ']'.\r",
    "code":
    """start(){
      bill("Hello World")
}
    """
  },
  {
    "number": 102,
    "actual_output": "Syntax Error: Unexpected 'piece_lit' at line 2, col 13. Expected '=', ',', ';'.",
    "expected_output": "Syntax Error: Unexpected 'piece_lit' at line 2, col 13. Expected '=', ',', ';'.",
    "code":
    """start(){
	piece of x 10;
}
    """
  },
  {
    "number": 103,
    "actual_output": "Syntax Error: Unexpected 'piece_lit' at line 2, col 17. Expected ',', ';'.",
    "expected_output": "Follow set ng <primary_val>",
    "code":
    """start(){
	piece of z = 5 10;
}
    """
  },
  {
    "number": 104,
    "actual_output": "Syntax Error: Unexpected 'id' at line 2, col 9. Expected 'of', '[', ':', '=', '+=', '-=', '*=', '/=', '%=', '('.",
    "expected_output": "Syntax Error: Unexpected 'id' at line 2, col 9. Expected 'of', '[', ':', '=', '+=', '-=', '*=', '/=', '%=', '('.",
    "code":
    """start() {
    int sum = 24 + 26;
	bill(tochars(sum));
}
    """
  },
  {
    "number": 105,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start() {
piece of xx = 24 + 26;
	bill(tochars(sum));
}
    """
  },
  {
    "number": 106,
    "actual_output": "No Syntax Error",
    "expected_output": "No Syntax Error",
    "code":
    """start(){     
       check (input > 0){
            bill("Number is positive");
        } alt (input < 0){
            bill("Number is negative");
        } instead{
            bill("Number is zero");
        }
}
    """
  },
  {
    "number": 107,
    "actual_output": "Syntax Error: Unexpected 'EOF' at line 8, col 9. Expected 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', 'check', 'menu', 'pass', 'repeat', 'order', 'next', 'stop', 'serve', '}', 'choice', 'usual'.",
    "expected_output": "Syntax Error: Unexpected 'EOF' at line 8, col 9. Expected 'id', 'append', 'bill', 'copy', 'cut', 'fact', 'matches', 'pow', 'rand', 'remove', 'reverse', 'search', 'size', 'sort', 'sqrt', 'take', 'tochars', 'topiece', 'tosip', 'check', 'menu', 'pass', 'repeat', 'order', 'next', 'stop', 'serve', '}', 'choice', 'usual'.",
    "code":
    """start(){     
       check (input > 0){
            bill("Number is positive");
        } alt (input < 0){
            bill("Number is negative");
        } instead{
            bill("Number is zero");
        }
}
    """
  },
  {
    "number": 108,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 109,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 110,
    "actual_output": "Syntax Error: Unexpected 'remove' at line 5, col 1. Expected 'piece', 'sip', 'flag', 'chars', 'table', 'id', 'prepare', 'start'.",
    "expected_output": "Syntax Error: Unexpected 'remove' at line 5, col 1. Expected 'piece', 'sip', 'flag', 'chars', 'table', 'id', 'prepare', 'start'.",
    "code":
    """piece[] of nums = [1, 2, 3];
piece of num = 1;


remove([1, 2, 3], 1);
    """
  },
  {
    "number": 111,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 112,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 113,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 114,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 115,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 116,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 117,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 118,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 119,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
  {
    "number": 120,
    "actual_output": "",
    "expected_output": "",
    "code":
    """
    """
  },
]