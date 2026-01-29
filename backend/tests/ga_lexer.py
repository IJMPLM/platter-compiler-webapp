import json
import unittest
import os
from pprint import pformat
from app.lexer.lexer import Lexer
from app.lexer.token import Token

SAMPLES_DIR = "./tests/lexer_programs/"


class TestPlatterLexerStrings(unittest.TestCase):
    string_tests = [

        {
            "number": 1,
            "code": "copy ? 10;",
            "expected_types": [
                "copy",
                Token.InvalidCharacter,
                "piece_lit",
                ";"
            ]
        },
        {
            "number": 2,
            "code": "iwag = 6.0000007;",
            "expected_types": [
                "id",
                "=",
                "sip_lit",
                ";"
            ]
        },
        {
            "number": 3,
            "code": "john = \"john\"",
            "expected_types": [
                "id",
                "=",
                "chars_lit"
            ]
        },
        {
            "number": 4,
            "code": "piece_ _piece piece of ;",
            "expected_types": [
                "id", "id", "piece", "of", ";"
            ]
        },
        {
            "number": 5,
            "code": "0serve flag;",
            "expected_types": [
                Token.InvalidLexeme,
                "serve",
                "id",
                ";"
            ]
        },
        {
            "number": 6,
            "code": "john#0michael -\"true\"+=up",
            "expected_types": [
                "id",
                Token.InvalidLexeme,
                Token.InvalidLexeme,
                "id",
                "-",
                "chars_lit",
                "+=",
                Token.InvalidLexeme
            ]
        },
        {
            "number": 7,
            "code": "piece+jm ,,, ; : ' ` - --2 -(0.1",
            "expected_types": [
                "id",
                "+",
                "id",
                ",",
                ",",
                ",",
                ";",
                ":",
                Token.InvalidCharacter,
                Token.InvalidCharacter,
                "-",
                Token.InvalidLexeme,
                "piece_lit",
                "-",
                "(",
                Token.InvalidLexeme
            ]
        },
        {
            "number": 8,
            "code": "flag_ingr = !flag_ingr_2;",
            "expected_types": [
                "id",
                "=",
                Token.InvalidLexeme,
                "id",
                ";"
            ]
        },
        {
            "number": 9,
            "code": "flag Down = down + \"\"",
            "expected_types": [
                "flag",
                "id",
                "=",
                "flag_lit",
                "+",
                "chars_lit"
            ]
        },
        {
            "number": 10,
            "code": "12345678912345600.789;",
            "expected_types": [
                Token.InvalidLexemeExceeds,
                Token.InvalidLexeme,
                "sip_lit",
                ";"
            ]
        },
        {
            "number": 11,
            "code": "\"/n\"_michael = \"john\\\"\"john\"",
            "expected_types": [
                "chars_lit",
                "id",
                "=",
                "chars_lit",
                Token.InvalidLexeme,
                Token.InvalidLexeme
            ]
        },
        {
            "number": 12,
            "code": "for(i = 10; i<piece; i++)",
            "expected_types": [
                "id",
                "(",
                "id",
                "=",
                "piece_lit",
                ";",
                "id",
                "<",
                "id",
                ";",
                "id",
                Token.InvalidLexeme,
                Token.InvalidLexeme,
                ")"
            ]
        },
        {
            "number": 13,
            "code": "+-*/!@#$%^&*=0",
            "expected_types": [
                "+",
                Token.InvalidLexeme,
                Token.InvalidLexeme,
                Token.InvalidLexeme,
                Token.InvalidLexeme,
                Token.InvalidCharacter,
                Token.InvalidLexeme,
                Token.InvalidCharacter,
                Token.InvalidLexeme,
                Token.InvalidCharacter,
                Token.InvalidCharacter,
                "*=",
                Token.InvalidLexeme
            ]
        },
        {
            "number": 14,
            "code": "jm:field_one = 99;",
            "expected_types": [
                "id",
                ":",
                "id",
                "=",
                "piece_lit",
                ";"
            ]
        },
        {
            "number": 15,
            "code": "iwag[piece_ingr] = piece_ingr_2;",
            "expected_types": [
                "id",
                "[",
                "id",
                "]",
                "=",
                "id",
                ";"
            ]
        },
        {
            "number": 16,
            "code": "copy = piece_ingr * (sip_ingr / 2.0);",
            "expected_types": [
                "copy",
                "=",
                "id",
                "*",
                "(",
                "id",
                "/",
                "sip_lit",
                ")",
                ";"
            ]
        },
        {
            "number": 17,
            "code": "__ = piece_ingr % 2 == 0 && flag_ingr;",
            "expected_types": [
                "id",
                "=",
                "id",
                "%",
                "piece_lit",
                "==",
                "piece_lit",
                Token.InvalidCharacter,
                Token.InvalidCharacter,
                "id",
                ";"
            ]
        },
        {
            "number": 18,
            "code": "start(){ piece of globalVariable; }",
            "expected_types": [
                "start",
                "(",
                ")",
                "{",
                "piece",
                "of",
                "id",
                ";",
                "}"
            ]
        },
        {
            "number": 19,
            "code": "-[][] john:[][\"]\\\" 123 4 5 6   8 9 0 0 '",
            "expected_types": [
                Token.InvalidLexeme,
                "[",
                "]",
                "[",
                "]",
                "id",
                ":",
                "[",
                "]",
                "[",
                Token.InvalidLexeme,
            ]
        },
        {
            "number": 20,
            "code": "piece##this should still work # ##",
            "expected_types": [
                "id",
                "comment_multi"
            ]
        },
        {
            "number": 21,
            "code": "Student of normal = [ name = \"jm\"; age = 21; ];",
            "expected_types": [
                "id",
                "of",
                "id",
                "=",
                "[",
                "id",
                "=",
                "chars_lit",
                ";",
                "id",
                "=",
                "piece_lit",
                ";",
                "]",
                ";"
            ]
        },
        {
            "number": 22,
            "code": "prepare piece[] of getPiece() { serve [ \"Hello\", \"World\" ]; }",
            "expected_types": [
                "prepare",
                "piece",
                "[",
                "]",
                "of",
                "id",
                "(",
                ")",
                "{",
                "serve",
                "[",
                "chars_lit",
                ",",
                "chars_lit",
                "]",
                ";",
                "}"
            ]
        },
        {
            "number": 23,
            "code": "topiece(tosip(tochars(take(bill(",
            "expected_types": [
                "topiece",
                "(",
                "tosip",
                "(",
                "tochars",
                "(",
                "take",
                "(",
                "bill",
                "("
            ]
        },
        {
            "number": 24,
            "code": "check(alt(instead(pass(while(break(stop(serve",
            "expected_types": ["check", "(", "alt", "(", "id", "(", "pass", "(", "id", "(", "id", "(", "id", "(", "Invalid Lexeme"]
        },
        {
            "number": 25,
            "code": "012345678 +100",
            "expected_types": [
                Token.InvalidLexeme,
                "piece_lit",
                "+",
                Token.InvalidLexeme
            ]
        },
        {
            "number": 26,
            "code": "34.23f 1x10^-3 +100.000",
            "expected_types": [
                Token.InvalidLexeme,
                "id",
                Token.InvalidLexeme,
                Token.InvalidLexeme,
                Token.InvalidCharacter,
                "piece_lit",
                "+",
                Token.InvalidLexeme
            ]
        },
        {
            "number": 27,
            "code": "up/down, Down, DOWN;",
            "expected_types": [
                "id",
                "/",
                "id",
                ",",
                "id",
                ",",
                "id",
                ";"
            ]
        },
        {
            "number": 28,
            "code": "\"C:\\Users\\Is Still Allowed\"",
            "expected_types": [
                "chars_lit"
            ]
        },
        {
            "number": 29,
            "code": "\\n\\t\\\\\\\"\\n\\t\\\\\\\"\"",
            "expected_types": [
                Token.InvalidCharacter,
                Token.InvalidLexeme,
                Token.InvalidCharacter,
                Token.InvalidLexeme,
                Token.InvalidCharacter,
                Token.InvalidCharacter,
                Token.InvalidCharacter,
                "chars_lit"
            ]
        },
        {
            "number": 30,
            "code": "piece of x, y = 1, z = 2;",
            "expected_types": [
                "piece",
                "of",
                "id",
                ",",
                "id",
                "=",
                "piece_lit",
                ",",
                "id",
                "=",
                "piece_lit",
                ";"
            ]
        },
        {
            "number": 31,
            "code": "piece of start(){ serve 0; }",
            "expected_types": [
                "piece",
                "of",
                "start",
                "(",
                ")",
                "{",
                "serve",
                "piece_lit",
                ";",
                "}"
            ]
        },
        {
            "number": 32,
            "code": "copy(text, -9, 56);",
            "expected_types": [
                "copy",
                "(",
                "id",
                ",",
                "piece_lit",
                ",",
                "piece_lit",
                ")",
                ";"
            ]
        },
        {
            "number": 33,
            "code": "pow(2.0, 3);",
            "expected_types": [
                "pow",
                "(",
                "sip_lit",
                ",",
                "piece_lit",
                ")",
                ";"
            ]
        },
        {
            "number": 34,
            "code": "### Tripple Hash",
            "expected_types": [
                Token.InvalidLexeme
            ]
        },
        {
            "number": 35,
            "code": "a and b or c;",
            "expected_types": [
                "id",
                "and",
                "id",
                "or",
                "id",
                ";"
            ]
        },
        {
            "number": 36,
            "code": "piece of 0bad = 1;",
            "expected_types": [
                "piece",
                "of",
                Token.InvalidLexeme,
                "id",
                "=",
                "piece_lit",
                ";"
            ]
        },
        {
            "number": 37,
            "code": "unterminated = \"abc",
            "expected_types": [
                "id",
                "=",
                Token.InvalidLexeme,
            ]
        },
        {
            "number": 38,
            "code": "prepare piece of bad( piece of x, piece of y ) { serve x; }",
            "expected_types": [
                "prepare",
                "piece",
                "of",
                "id",
                "(",
                "piece",
                "of",
                "id",
                ",",
                "piece",
                "of",
                "id",
                ")",
                "{",
                "serve",
                "id",
                ";",
                "}"
            ]
        },
        {
            "number": 39,
            "code": "sip of x = ;",
            "expected_types": [
                "sip",
                "of",
                "id",
                "=",
                ";"
            ]
        },
        {
            "number": 40,
            "code": "rand(\"cake\");",
            "expected_types": [
                "rand",
                "(",
                "chars_lit",
                ")",
                ";"
            ]
        },
        {
            "number": 41,
            "code": "notnot = not not up;",
            "expected_types": [
                'id', '=', 'not', 'not', 'flag_lit', ';'
            ]
        },
        {
            "number": 42,
            "code": "sip invalid = 1.12345678;",
            "expected_types": [
                'sip', 'id', '=', 'Invalid Lexeme Exceeds', 'piece_lit', ';'
            ]
        },
        {
            "number": 43,
            "code": "weird = \"\\q\";",
            "expected_types": [
                "id", "=", "chars_lit", ";"
            ]
        },
        {
            "number": 44,
            "code": "fact(-1000);",
            "expected_types": [
                "fact", "(", "piece_lit", ")", ";"
            ]
        },
        {
            "number": 45,
            "code": "c = 'single quote';",
            "expected_types": [
                "id", "=", "Invalid Character", "id", "Invalid Lexeme", "Invalid Character", ";"
            ]
        },
        {
            "number": 46,
            "code": "tosip(\"8\");",
            "expected_types": [
                "tosip",
                "(",
                "chars_lit",
                ")",
                ";"
            ]
        },
        {
            "number": 47,
            "code": "#NoSpace",
            "expected_types": [
                "Invalid Lexeme", "Invalid Lexeme"
            ]
        },
        {
            "number": 48,
            "code": "a = b ** c;",
            "expected_types": [
                "id", "=", "id", "Invalid Lexeme", "*", "id", ";"
            ]
        },
        {
            "number": 49,
            "code": "bad_flag = True;",
            "expected_types": [
                "id", "=", "id", ";"
            ]
        },
        {
            "number": 50,
            "code": "sort(2, 4, 5);",
            "expected_types": [
                "sort", "(", "piece_lit", ",", "piece_lit", ",", "piece_lit", ")", ";"
            ]
        },
        {
            "number": 51,
            "code": "fact(6);",
            "expected_types": [
                "fact",
                "(",
                "piece_lit",
                ")",
                ";"
            ]
        },
        {
            "number": 52,
            "code": "check(a == b) { serve 0; }",
            "expected_types": [
                "check",
                "(",
                "id",
                "==",
                "id",
                ")",
                "{",
                "serve",
                "piece_lit",
                ";",
                "}"
            ]
        },
        {
            "number": 53,
            "code": "repeat(x < 10) { x += 1; }",
            "expected_types": [
                "repeat", "(", "id", "<", "piece_lit", ")", "{", "id", "+=", "piece_lit", ";", "}"
            ]
        },
        {
            "number": 54,
            "code": "x ==== y;",
            "expected_types": [
                "id", "Invalid Lexeme", "==", "id", ";"
            ]
        },
        {
            "number": 55,
            "code": "invalid_num = 100000000000000000000000;",
            "expected_types": [
                "id", "=", "Invalid Lexeme Exceeds", "Invalid Lexeme", "Invalid Lexeme", "Invalid Lexeme",
                "Invalid Lexeme", "Invalid Lexeme", "Invalid Lexeme", "Invalid Lexeme", "Invalid Lexeme", "piece_lit",
                ";"
            ]
        },
        {
            "number": 56,
            "code": "n = not up;",
            "expected_types": [
                "id", "=", "not", "flag_lit", ";"
            ]
        },
        {
            "number": 57,
            "code": "piece of x = 10; # This is a comment",
            "expected_types": [
                "piece", "of", "id", "=", "piece_lit", ";", "comment_single"
            ]
        },
        {
            "number": 58,
            "code": "x = !10;",
            "expected_types": [
                "id", "=", "Invalid Lexeme", "piece_lit", ";"
            ]
        },
        {
            "number": 59,
            "code": "piece of my_array[10];",
            "expected_types": [
                "piece", "of", "id", "[", "piece_lit", "]", ";"
            ]
        },
        {
            "number": 60,
            "code": "check;",
            "expected_types": [
                "id", ";"
            ]
        },
        {
            "number": 61,
            "code": "pass (){serve a;}",
            "expected_types": [
                "pass", "(", ")", "{", "serve", "id", ";", "}"
            ]
        },
        {
            "number": 62,
            "code": "x !- y;",
            "expected_types": [
                "id", "Invalid Lexeme", "-", "id", ";"
            ]
        },
        {
            "number": 63,
            "code": "\"hello world\nx = 10;",
            "expected_types": [
                "Invalid Lexeme", "id", "=", "piece_lit", ";"
            ]
        },
        {
            "number": 64,
            "code": "appendix = 3;",
            "expected_types": [
                "id", "=", "piece_lit", ";"
            ]
        },
        {
            "number": 65,
            "code": "Flag of a = up;",
            "expected_types": [
                "id", "of", "id", "=", "flag_lit", ";"
            ]
        },
        {
            "number": 66,
            "code": "altinstead;",
            "expected_types": [
                "id", ";"
            ]
        },
        {
            "number": 67,
            "code": "piece of a 4(3;",
            "expected_types": [
                "piece", "of", "id", "piece_lit", "(", "piece_lit", ";"
            ]
        },
        {
            "number": 68,
            "code": "chars[] of a = [instead];",
            "expected_types": [
                "chars", "[", "]", "of", "id", "=", "[", "id", "]", ";"
            ]
        },
        {
            "number": 69,
            "code": "copy():12;",
            "expected_types": [
                "copy",
                "(",
                ")",
                ":",
                "piece_lit",
                ";"
            ]
        },
        {
            "number": 70,
            "code": "append()[15];",
            "expected_types": [
                "append",
                "(",
                ")",
                "[",
                "piece_lit",
                "]",
                ";"
            ]
        },
        {
            "number": 71,
            "code": "checK (a){}",
            "expected_types": [
                "id", "(", "id", ")", "{", "}"
            ]
        },
        {
            "number": 72,
            "code": "x = -\" \"",
            "expected_types": [
                "id", "=", "-", "chars_lit"
            ]
        },
        {
            "number": 73,
            "code": "5..2\n.5.5 ",
            "expected_types": [
                "Invalid Lexeme", "Invalid Character", "piece_lit", "Invalid Character", "sip_lit"
            ]
        },
        {
            "number": 74,
            "code": "stop:",
            "expected_types": [
                "id", ":"
            ]
        },
        {
            "number": 75,
            "code": "x = 10 @ y;",
            "expected_types": [
                "id", "=", "piece_lit", "Invalid Character", "id", ";"
            ]
        },
        {
            "number": 76,
            "code": "x = --5;",
            "expected_types": [
                "id", "=", "Invalid Lexeme", "piece_lit", ";"
            ]
        },
        {
            "number": 77,
            "code": "x = -/3;",
            "expected_types": [
                "id", "=", "Invalid Lexeme", "/", "piece_lit", ";"
            ]
        },
        {
            "number": 78,
            "code": "prepare:",
            "expected_types": [
                "id", ":"
            ]
        },
        {
            "number": 79,
            "code": "choice(",
            "expected_types": [
                "id", "("
            ]
        },
        {
            "number": 80,
            "code": "x = 10 \\r y;",
            "expected_types": [
                "id", "=", "piece_lit", "Invalid Character", "id", "id", ";"
            ]
        },
        {
            "number": 81,
            "code": "x = 20 \\v z;",
            "expected_types": [
                "id", "=", "piece_lit", "Invalid Character", "id", "id", ";"
            ]
        },
        {
            "number": 82,
            "code": "x = 5 \\f a;",
            "expected_types": [
                "id", "=", "piece_lit", "Invalid Character", "id", "id", ";"
            ]
        },
        {
            "number": 83,
            "code": "\"test\"id;",
            "expected_types": [
                "chars_lit", "id", ";"
            ]
        },
        {
            "number": 84,
            "code": "(abc);",
            "expected_types": [
                "(", "id", ")", ";"
            ]
        },
        {
            "number": 85,
            "code": ",,,;",
            "expected_types": [
                ",",
                ",",
                ",",
                ";"
            ]
        },
        {
            "number": 86,
            "code": "===;",
            "expected_types": [
                "Invalid Lexeme", "Invalid Lexeme", ";"
            ]
        },
        {
            "number": 87,
            "code": "**;",
            "expected_types": [
                "Invalid Lexeme", "Invalid Lexeme", ";"
            ]
        },
        {
            "number": 88,
            "code": "flag down??;",
            "expected_types": [
                "flag", "Invalid Lexeme", "Invalid Character", "Invalid Character", ";"
            ]
        },
        {
            "number": 89,
            "code": "n e x t;",
            "expected_types": [
                "id", "id", "id", "id", ";"
            ]
        },
        {
            "number": 90,
            "code": "append5 \"unterminated start instead] #badcomment",
            "expected_types": [
                "id", "Invalid Lexeme"
            ]
        },
        {
            "number": 91,
            "code": "if i === j;",
            "expected_types": [
                "id", "id", "Invalid Lexeme", "=", "id", ";"
            ]
        },
        {
            "number": 92,
            "code": "piece of 12num;",
            "expected_types": [
                "piece", "of", "Invalid Lexeme", "id", ";"
            ]
        },
        {
            "number": 93,
            "code": "321123321123321123;",
            "expected_types": [
                "Invalid Lexeme Exceeds", "piece_lit", ";"
            ]
        },
        {
            "number": 94,
            "code": "a--5;",
            "expected_types": [
                "id", "Invalid Lexeme", "piece_lit", ";"
            ]
        },
        {
            "number": 95,
            "code": "bill(\"hello\")",
            "expected_types": [
                "bill", "(", "chars_lit", ")"
            ]
        },
        {
            "number": 96,
            "code": "5++i;",
            "expected_types": [
                "piece_lit", "Invalid Lexeme", "+", "id", ";"
            ]
        },
        {
            "number": 97,
            "code": "5 += piece;",
            "expected_types": [
                "piece_lit", "+=", "id", ";"
            ]
        },
        {
            "number": 98,
            "code": "check{}",
            "expected_types": [
                "Invalid Lexeme", "{", "}"
            ]
        },
        {
            "number": 99,
            "code": "1234554321..",
            "expected_types": [
                "Invalid Lexeme", "Invalid Character"
            ]
        },
        {
            "number": 100,
            "code": "down{}",
            "expected_types": [
                "Invalid Lexeme", "{", "}"
            ]
        },
        {
            "number": 101,
            "code": "\"\"\"Missing quote",
            "expected_types": [
                "chars_lit", "Invalid Lexeme"
            ]
        },
        {
            "number": 102,
            "code": "x && y;",
            "expected_types": [
                "id", "Invalid Character", "Invalid Character", "id", ";"
            ]
        },
        {
            "number": 103,
            "code": "Hello^World;",
            "expected_types": [
                "Invalid Lexeme", "Invalid Character", "id", ";"
            ]
        },
        {
            "number": 104,
            "code": "1221 + 1.3.2 ;",
            "expected_types": [
                "piece_lit", "+", "Invalid Lexeme", "Invalid Character", "piece_lit", ";"
            ]
        },
        {
            "number": 105,
            "code": "OneHundred + 12 -- 15 ;",
            "expected_types": [
                "id", "+", "piece_lit", "Invalid Lexeme", "-", "piece_lit", ";"
            ]
        },
        {
            "number": 106,
            "code": "\"25\"+\"25\";",
            "expected_types": [
                "chars_lit",
                "+",
                "chars_lit", ";"
            ]
        },
        {
            "number": 107,
            "code": "this_is_exactly_25_chars;",
            "expected_types": [
                "id", ";"
            ]
        },
        {
            "number": 108,
            "code": "pie##comment##ce;",
            "expected_types": [
                "id", "comment_multi", "id", ";"
            ]
        },
        {
            "number": 109,
            "code": "a:b;",
            "expected_types": [
                "id", ":", "id", ";"
            ]
        },
        {
            "number": 110,
            "code": "\"C:\\\\Users\\\\\";",
            "expected_types": [
                "chars_lit", ";"
            ]
        },
        {
            "number": 111,
            "code": "\"escape q \\q\";",
            "expected_types": [
                "chars_lit", ";"
            ]
        },
        {
            "number": 112,
            "code": "\"Hello \\t World\";",
            "expected_types": [
                "chars_lit", ";"
            ]
        },
        {
            "number": 113,
            "code": "bill(4);",
            "expected_types": [
                "bill", "(", "piece_lit", ")", ";"
            ]
        },
        {
            "number": 114,
            "code": "add(x + piece y);",
            "expected_types": [
                "id", "(", "id", "+", "piece", "id", ")", ";"
            ]
        },
        {
            "number": 115,
            "code": "xX_Goku_Xx;",
            "expected_types": [
                "id", ";"
            ]
        },
        {
            "number": 116,
            "code": "serve food;",
            "expected_types": [
                "serve", "id", ";"
            ]
        },
        {
            "number": 117,
            "code": "sub((5-1);",
            "expected_types": [
                "id", "(", "(", "piece_lit", "piece_lit", ")", ";"
            ]
        },
        {
            "number": 118,
            "code": "25+25;",
            "expected_types": [
                "piece_lit", "+", "piece_lit", ";"
            ]
        },
        {
            "number": 119,
            "code": "1234512345;",
            "expected_types": [
                "piece_lit", ";"
            ]
        },
        {
            "number": 120,
            "code": "12345.12345;",
            "expected_types": [
                "sip_lit", ";"
            ]
        },
        {
            "number": 121,
            "code": "5abc = 10;",
            "expected_types": [Token.InvalidLexeme, "id", "=", "piece_lit", ";"],
        },
        {
            "number": 122,
            "code": "na&me = 3;",
            "expected_types": ["Invalid Lexeme", "Invalid Character", "id", "=", "piece_lit", ";"],
        },
        {
            "number": 123,
            "code": "chars of a = \"hello;",
            "expected_types": ["chars", "of", "id", "=", "Invalid Lexeme"],
        },
        {
            "number": 124,
            "code": "x = \"hi\\qbye\";",
            "expected_types": ["id", "=", "chars_lit", ";"],
        },
        {
            "number": 125,
            "code": "x = .55;",
            "expected_types": ["id", "=", "Invalid Character", "piece_lit", ";"],
        },
        {
            "number": 126,
            "code": "x = 0123;",
            "expected_types": ["id", "=", "Invalid Lexeme", "piece_lit", ";"],
        },
        {
            "number": 127,
            "code": "y = 1.23e5;",
            "expected_types": ["id", "=", "Invalid Lexeme", "id", ";"],
        },
        {
            "number": 128,
            "code": "tricia = 10;",
            "expected_types": ["id", "=", "piece_lit", ";"],
        },
        {
            "number": 129,
            "code": "user#name = 10;",
            "expected_types": ["id", "Invalid Lexeme", "id", "=", "piece_lit", ";"],
        },
        {
            "number": 130,
            "code": "001value = 5;",
            "expected_types": ["Invalid Lexeme", "Invalid Lexeme", "Invalid Lexeme", "id", "=", "piece_lit", ";"],
        },
        {
            "number": 131,
            "code": "hello world = 3;",
            "expected_types": ["id", "id", "=", "piece_lit", ";"],
        },
        {
            "number": 132,
            "code": "x = \"unterminated;",
            "expected_types": ["id", "=", "Invalid Lexeme"],
        },
        {
            "number": 133,
            "code": "var = \"hello\\pworld\";",
            "expected_types": ["id", "=", "chars_lit", ";"],
        },
        {
            "number": 134,
            "code": "data[] of x = [1,,2];",
            "expected_types": ["id", "[", "]", "of", "id", "=", "[", "piece_lit", ",", ",", "piece_lit", "]", ";"],
        },
        {
            "number": 135,
            "code": "sample = 1.2.3;",
            "expected_types": ["id", "=", "Invalid Lexeme", "Invalid Character", "piece_lit", ";"],
        },
        {
            "number": 136,
            "code": "login()#comment;",
            "expected_types": ["id", "(", ")", "Invalid Lexeme", "id", ";"],
        },
        {
            "number": 137,
            "code": "copy = piece_lit;",
            "expected_types": ["copy", "=", "id", ";"],
        },
        {
            "number": 138,
            "code": "a = b ** c;",
            "expected_types": ["id", "=", "id", "Invalid Lexeme", "*", "id", ";"],
        },
        {
            "number": 139,
            "code": "#notacomment;",
            "expected_types": ["Invalid Lexeme", "id", ";"],
        },
        {
            "number": 140,
            "code": """m{ 
n}
o\"""",
            "expected_types": [Token.InvalidLexeme, "{", Token.InvalidLexeme, "}", Token.InvalidLexeme, Token.InvalidLexeme],
        },
        {
            "number": 141,
            "code": "B#",
            "expected_types": ["id", "Invalid Lexeme"],
        },
        {
            "number": 142,
            "code": "kjadhajksdhadkashdjaksdhakjdhasjkdhaskjdhasdaskdahdkjasdhak;",
            "expected_types": ["Invalid Lexeme Exceeds", "Invalid Lexeme Exceeds", "id", ";"],
        },
        {
            "number": 143,
            "code": """# awda
## adwa ##
# asd""",
            "expected_types": ["comment_single", "comment_multi", "comment_single"],
        },
        {
            "number": 144,
            "code": "chars #comment## of a = a;",
            "expected_types": ["chars", "Invalid Lexeme", "id", "Invalid Lexeme"],
        },
        {
            "number": 145,
            "code": "piece of & = a;",
            "expected_types": ["piece", "of", "Invalid Character", "=", "id", ";"],
        },
        {
            "number": 146,
            "code": "piece():1;",
            "expected_types": ["id", "(", ")", ":", "piece_lit", ";"],
        },
        {
            "number": 147,
            "code": "piece of x = 5;",
            "expected_types": ["piece", "of", "id", "=", "piece_lit", ";"],
        },
        {
            "number": 148,
            "code": "piece&",
            "expected_types": ["Invalid Lexeme", "Invalid Character"],
        },
        {
            "number": 149,
            "code": "piece_;",
            "expected_types": ["id", ";"],
        },
        {
            "number": 150,
            "code": "12;",
            "expected_types": ["piece_lit", ";"],
        },
    ]

    def test_strings(self):
        for i, case in enumerate(self.string_tests, 1):
            with self.subTest(case=i):
                lexer = Lexer(case["code"])
                tokens = [t for t in lexer.tokenize()
                          if t.type not in ("comment", "space", "newline", "tab")]
                actual_types = [t.type for t in tokens]

                msg = (
                    f"\n=== CASE {i} ===\n"
                    f"CODE:\n{case['code']}\n"
                    f"EXPECTED: {json.dumps(case['expected_types'])}\n"
                    f"ACTUAL:   {json.dumps(actual_types)}\n"
                    f"==============\n"
                )
                # print("'" + " ".join(f'"{x}"' for x in actual_types) )

                # self.addCleanup(print, msg)

                try:
                    self.assertEqual(
                        actual_types,
                        case["expected_types"],
                    )
                except:
                    print(msg)

    def test_all_files(self):
        self.maxDiff = None
        platter_files = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".platter")]
        for pf in platter_files:
            with self.subTest(platter_file=pf):
                filepath = os.path.join(SAMPLES_DIR, pf)
                with open(filepath, "r", encoding="utf-8") as f:
                    source = f.read()
                lexer = Lexer(source)
                tokens = "\n".join(t.type for t in lexer.tokenize())

                output_file = pf.replace(".platter", ".output")
                output_path = os.path.join(SAMPLES_DIR, output_file)
                if not os.path.exists(output_path):
                    self.fail(f"Missing output file for {pf}")

                with open(output_path, "r", encoding="utf-8") as f:
                    expected = f.read().strip()

                self.assertEqual(tokens, expected)


if __name__ == "__main__":
    unittest.main()
