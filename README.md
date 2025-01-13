# PyPGN

This is a simple library capable of parsing chess PGNs, following the standard
definition. It includes classes that form an Abstract Syntax Tree, fully
representing the parsed PGN with code. These classes also include `__str__`
implementations that allow seamless conversion back to regular (normalized) PGN
strings.

A unique feature of this library is the `flatten` function for a list of moves.
This function allows for the flattening of a list of moves, recursively
stripping away all of the variations in a chess game and returning full
standalone lists for each variation.

The parsing is handled using the
[`Lark`](https://lark-parser.readthedocs.io/en/stable/index.html) library,
which is therefore a dependecy of this library. Lark allows specifying a formal
EBNF-like grammar definition, which it then uses to tokenize the given input.
This token tree is then used to produce the AST.
