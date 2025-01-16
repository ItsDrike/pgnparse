from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import cast, final, overload, override

from lark import Lark, ParseTree, Token, Tree

__all__ = [
    "PGN",
    "PGNBasicAnnotation",
    "PGNGameResult",
    "PGNTurn",
    "PGNTurnList",
    "PGNTurnMove",
]

# This grammar notation is based on the Extended Backus-Naur Form (EBNF) notation
# however, it is not 100% compatible with the EBNF standard, the lark parser makes
# some modifications to the notation to make it more user-friendly.
PGN_GRAMMAR = r"""
pgn: tag_section? comment? turn_section? result?

# Tags
tag_section: tag_line (NEWLINE tag_line)* NEWLINE?
tag_line: "[" tag_name WS_INLINE quoted_value "]"
tag_name: TAG_NAME
quoted_value: ESCAPED_STRING

# Game result
result: RESULT

# Turns
turn_section: turn (WS (turn | variant))*
turn: turn_number white_move (WS black_move)?
    | turn_number_continuation black_move
variant: "(" turn_section ")"
turn_number: INT "."
turn_number_continuation: INT "..."

# Moves
white_move: move
black_move: move
move: move_string annotation? numeric_annotation* block_comment?
move_string: MOVE_STRING

# Move metadata
annotation: ANNOTATION
numeric_annotation: "$" INT

# Comments
comment: line_comment | block_comment
block_comment: "{" BLOCK_COMMENT_TEXT "}"
line_comment: ";" LINE_COMMENT_TEXT NEWLINE

# Move types (tokens)
MOVE_STRING: (CASTLING | PIECE_MOVE | PAWN_MOVE) (CHECK | MATE)?
PIECE_MOVE: PIECE (FILE | RANK)? CAPTURE? SQUARE
PAWN_MOVE: FILE? CAPTURE? SQUARE PROMOTION?

# Move components (tokens)
SQUARE: FILE RANK
PROMOTION: "=" PIECE
CAPTURE: "x"
CHECK: "+"
MATE: "#"
CASTLING: /[Oo0]-[Oo0](-[Oo0])?/

# Tokens
ANNOTATION: "??" | "!!" | "?!" | "!?" | "!" | "?"
FILE: /[a-h]/
RANK: /[1-8]/
PIECE: "K" | "Q" | "R" | "B" | "N"
RESULT: "1-0" | "0-1" | "1/2-1/2" | "*"
BLOCK_COMMENT_TEXT: /[^}]+/
LINE_COMMENT_TEXT: /[^\n]+/
TAG_NAME: /[A-Za-z]([A-Za-z0-9-]*)/

# Token Imports
%import common.WS
%import common.WS_INLINE
%import common.NEWLINE
%import common.LETTER
%import common.DIGIT
%import common.INT
%import common.ESCAPED_STRING

%ignore WS
"""

PGN_PARSER = Lark(PGN_GRAMMAR, start="pgn")


class InvalidPGNTreeError(ValueError):
    """Raised when there is an issue with the PGN tree during AST construction.

    This is NOT raised when the PGN tree is invalid according to the grammar,
    rather, during the AST construction process, when the token tree is not in
    the expected format.
    """


@final
class PGNGameResult(StrEnum):
    """An enumeration of possible game results."""

    WHITE_WINS = "1-0"
    BLACK_WINS = "0-1"
    DRAW = "1/2-1/2"
    UNFINISHED = "*"
    UNSPECIFIED = ""


@final
class PGNBasicAnnotation(StrEnum):
    """An enumeration of basic move annotations that can be a part of PGN moves."""

    GOOD_MOVE = "!"
    MISTAKE = "?"
    BRILLIANT_MOVE = "!!"
    BLUNDER = "??"
    INTERESTING_MOVE = "!?"
    DUBIOUS_MOVE = "?!"


@final
@dataclass
class PGNTurnMove:
    """A PGN turn move object that represents a single move in a game."""

    move_string: str
    annotation: PGNBasicAnnotation | None = None
    numeric_annotations: list[int] = field(default_factory=list)
    comment: str | None = None

    @classmethod
    def from_tree(cls, tree: ParseTree) -> "PGNTurnMove":
        """Parse a Lark sub-tree from the PGN grammar and return a PGNTurnMove object.

        This expects a 'move' tree from the PGN grammar. A 'white-move' or 'black-move' tree
        are also valid, as they are just containers for 'move'.
        """
        if tree.data in ("white_move", "black_move"):
            if not isinstance(tree.children[0], Tree):
                raise InvalidPGNTreeError(f"Expected 'move' tree, found token: {tree.children[0]}")
            tree = tree.children[0]

        if tree.data != "move":
            raise InvalidPGNTreeError(f"Expected 'move' tree, found: {tree.data}")

        move_string = cast(Token, next(tree.find_data("move_string")).children[0]).value

        if (annotation := next(tree.find_data("annotation"), None)) is not None:
            annotation = PGNBasicAnnotation(cast(Token, annotation.children[0]).value)

        numeric_annotations = [int(cast(Token, el.children[0]).value) for el in tree.find_data("numeric_annotation")]
        if (comment := next(tree.find_data("block_comment"), None)) is not None:
            comment = cast(Token, comment.children[0]).value

        return cls(move_string, annotation, numeric_annotations, comment)

    @override
    def __str__(self) -> str:
        parts = [self.move_string]

        if self.annotation:
            parts.append(str(self.annotation))

        if self.numeric_annotations:
            parts.append(" ")
            num_ann_str = " ".join(f"${el}" for el in self.numeric_annotations)
            parts.append(num_ann_str)

        if self.comment:
            parts.append(" {" + self.comment + "}")

        return "".join(parts)

    @property
    def extra_annotations(self) -> list[int]:
        """Alias for the numeric_annotations attribute.

        This is a more user-friendly name for the numeric annotations.
        """
        return self.numeric_annotations


@final
@dataclass
class PGNTurn:
    """A PGN turn object that represents a single turn in a game."""

    turn_number: int
    white_move: PGNTurnMove | None
    black_move: PGNTurnMove | None

    def __post_init__(self):
        # If white move is None, this is a continuation move, and black move must be present
        # If black move is None, this is an incomplete turn; black hasn't yet played, but white must be present
        if self.white_move is None and self.black_move is None:
            raise ValueError("Both white_move and black_move cannot be None")

    @classmethod
    def from_tree(cls, tree: ParseTree) -> "PGNTurn":
        """Parse a Lark sub-tree from the PGN grammar and return a PGNTurn object.

        This expects a 'turn' tree from the PGN grammar.
        """
        if tree.data != "turn":
            raise InvalidPGNTreeError(f"Expected 'turn' tree, found: {tree.data}")

        try:
            turn_number = int(cast(Token, next(tree.find_data("turn_number")).children[0]).value)
        except StopIteration:
            turn_number = int(cast(Token, next(tree.find_data("turn_number_continuation")).children[0]).value)
            white_move = None
        else:
            white_move = PGNTurnMove.from_tree(next(tree.find_data("white_move")))

        try:
            black_move = PGNTurnMove.from_tree(next(tree.find_data("black_move")))
        except StopIteration:
            black_move = None

        return cls(turn_number, white_move, black_move)

    @override
    def __str__(self) -> str:
        parts = [f"{self.turn_number}."]

        if self.white_move is None:
            parts.append("..")
        else:
            parts.append(f" {self.white_move!s}")

        if self.black_move:
            parts.append(f" {self.black_move!s}")

        return "".join(parts)

    def is_continuation(self) -> bool:
        """Check if the turn is a continuation, i.e., the white move is omitted."""
        return self.white_move is None

    def finish_continuation(self, white_move: PGNTurnMove) -> "PGNTurn":
        """Finishes the continuation by providing the white move.

        Note that this returns a new PGNTurn object, and doesn't modify the current one.
        """
        return PGNTurn(self.turn_number, white_move, self.black_move)


@final
class PGNTurnList(Sequence["PGNTurn | PGNTurnList"]):
    """A sequence of PGNTurn and PGNTurnList objects.

    The sequence can contain variations, represented as the nested PGNTurnList objects.
    """

    def __init__(self, turns: Iterable["PGNTurn | PGNTurnList"]):
        self._turns = list(turns)

    @overload
    def __getitem__(self, index: int) -> "PGNTurn | PGNTurnList": ...

    @overload
    def __getitem__(self, index: slice) -> "PGNTurnList": ...

    @override
    def __getitem__(self, index: int | slice) -> "PGNTurn | PGNTurnList":
        if isinstance(index, slice):
            return PGNTurnList(self._turns[index])
        return self._turns[index]

    @override
    def __len__(self) -> int:
        return len(self._turns)

    @override
    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, PGNTurnList):
            return NotImplemented

        return list(self) == list(other)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._turns})"

    @classmethod
    def from_tree(cls, tree: ParseTree) -> "PGNTurnList":
        """Parse a Lark sub-tree from the PGN grammar and return a PGNTurnList object.

        This expects a 'turn_section' tree from the PGN grammar.
        """
        if tree.data != "turn_section":
            raise InvalidPGNTreeError(f"Expected 'turn_section' or 'variant' tree, found: {tree.data}")

        lst: list[PGNTurn | PGNTurnList] = []
        for el in tree.children:
            # Non-trees (tokens) are just whitespace
            if not isinstance(el, Tree):
                continue

            # If the element is a variant, parse the nested turn section
            if el.data == "variant":
                variant_turn_section = el.children[0]
                if not isinstance(variant_turn_section, Tree) or variant_turn_section.data != "turn_section":
                    raise InvalidPGNTreeError("Variant turn section not found")
                variant: PGNTurnList = cls.from_tree(variant_turn_section)
                lst.append(variant)
            # Otherwise, it should be a turn
            elif el.data == "turn":
                lst.append(PGNTurn.from_tree(el))
            else:
                raise InvalidPGNTreeError(f"Unexpected element {el.data}")

        return cls(lst)

    @override
    def __str__(self) -> str:
        parts: list[str] = []

        for turn in self:
            if isinstance(turn, PGNTurn):
                parts.append(f"{turn!s}")
            else:
                # Will recurse
                parts.append(f"({turn!s})")

        return " ".join(parts)

    def flatten(self) -> Iterator["PGNTurnList"]:
        """Generate a list of full game turn-lists without any variations.

        Each variation produces a separate games, starting from the same mainline moves up to the variation point.
        The games are returned in order, as the variations are encountered. The last game is the mainline.
        """
        return (PGNTurnList(game) for game in self._flatten(self, []))

    @classmethod
    def _flatten(
        cls,
        turns: Sequence["PGNTurn | PGNTurnList"],
        prefix: list[PGNTurn],
    ) -> Iterator[list[PGNTurn]]:
        for turn in turns:
            if isinstance(turn, PGNTurn):
                # Usually, this is a mainline move
                # Sometimes, this move overrides the previous one (in variations),
                # Sometimes, this move is a continuation to the previous one (same white move)
                if len(prefix) > 0 and prefix[-1].turn_number == turn.turn_number:
                    if turn.is_continuation():
                        if prefix[-1].white_move is None:
                            raise ValueError("Previous move to continuation doesn't contain a white move")
                        turn = turn.finish_continuation(prefix[-1].white_move)  # noqa: PLW2901
                    _ = prefix.pop()

                prefix.append(turn)

            elif isinstance(turn, PGNTurnList):  # pyright: ignore[reportUnnecessaryIsInstance]
                # Branch out for the variation, using a copy of the prefix
                variation_games = cls._flatten(turn._turns, prefix[:])
                yield from variation_games
            else:
                raise TypeError(f"Invalid turn type: {type(turn)}")

        # Yield the current state of the mainline after processing all turns
        yield prefix


@final
@dataclass
class PGN:
    """A PGN object that represents a full game in Portable Game Notation (PGN) format."""

    tags: dict[str, str] = field(default_factory=dict[str, str])
    turns: PGNTurnList = field(default_factory=lambda: PGNTurnList([]))
    result: PGNGameResult = PGNGameResult.UNSPECIFIED
    comment: str | None = None

    @classmethod
    def from_string(cls, pgn: str) -> "PGN":
        """Parse a PGN string and return a PGN object."""
        tree = PGN_PARSER.parse(pgn)
        return cls.from_tree(tree)

    @classmethod
    def from_tree(cls, tree: ParseTree) -> "PGN":
        """Parse a Lark tree from the PGN grammar and return a PGN object.

        This expects a 'pgn' tree from the PGN grammar.
        """
        if tree.data != "pgn":
            raise InvalidPGNTreeError(f"Expected 'pgn' tree, found: {tree.data}")

        # Collect tree children, skipping tokens (whitespace)
        subtrees = [el for el in tree.children if isinstance(el, Tree)]

        tags = {}
        comment = None
        result = PGNGameResult.UNSPECIFIED
        turns = PGNTurnList([])
        while len(subtrees) > 0:
            section = subtrees.pop(0)

            if section.data == "tag_section":
                tags = cls._parse_tags(section)
            elif section.data == "comment":
                comment = cast(Token, cast(ParseTree, section.children[0]).children[0]).value
            elif section.data == "turn_section":
                turns = PGNTurnList.from_tree(section)
            elif section.data == "result":
                result = PGNGameResult(cast(Token, section.children[0]).value)
            else:
                raise InvalidPGNTreeError(f"Unexpected section: {section.data}")

        return cls(tags, turns, result, comment)

    @staticmethod
    def _parse_tags(tree: ParseTree) -> dict[str, str]:
        """Parse the tags section of a PGN tree."""
        tags: dict[str, str] = {}
        for line in tree.find_data("tag_line"):
            tag_name: str = cast(Token, next(line.find_data("tag_name")).children[0]).value
            quoted_value: str = cast(Token, next(line.find_data("quoted_value")).children[0]).value
            value = quoted_value.removeprefix('"').removesuffix('"')

            if tag_name in tags:
                raise ValueError(f"Duplicate tag name: {tag_name}")

            tags[tag_name] = value
        return tags

    @override
    def __str__(self) -> str:
        parts: list[str] = []

        tag_parts = [f'[{key} "{value.replace('"', '\\"')}"]' for key, value in self.tags.items()]
        if tag_parts:
            parts.append("\n".join(tag_parts))

        # There should be an additional newline between tags and comment/turns/result
        # (unless it's just tags)
        if tag_parts and (self.comment or self.turns or self.result is not PGNGameResult.UNSPECIFIED):
            parts.append("\n\n")

        inner_parts: list[str] = []
        if self.turns:
            inner_parts.append(str(self.turns))
        if self.result:
            inner_parts.append(str(self.result))

        if self.comment:
            parts.append("{" + str(self.comment) + "}")
            if inner_parts:
                parts.append("\n")

        parts.append(" ".join(inner_parts))

        return "".join(parts)

    @property
    def metadata(self) -> dict[str, str]:
        """Alias for the tags attribute.

        Tags follow official spec naming, but metadata is more user-friendly.
        """
        return self.tags

    @property
    def movetext(self) -> PGNTurnList:
        """Alias for the turns attribute.

        Movetext follows the official terminology, but we used turns,
        so this is an alias.
        """
        return self.turns
