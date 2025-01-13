import textwrap

import pytest

from pgnparse import PGN, PGNBasicAnnotation, PGNGameResult, PGNTurn, PGNTurnList, PGNTurnMove


@pytest.mark.parametrize(
    ("pgn", "expected_ast"),
    [
        (
            "1. e4",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), None)]),
            ),
        ),
        (
            "1. e4 e5",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))]),
            ),
        ),
        (
            "1. d4 d5 2. c4",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("d4"), PGNTurnMove("d5")),
                        PGNTurn(2, PGNTurnMove("c4"), None),
                    ],
                ),
            ),
        ),
        (
            "1. d4 d5 2. c4 {Queen's Gambit}",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("d4"), PGNTurnMove("d5")),
                        PGNTurn(2, PGNTurnMove("c4", comment="Queen's Gambit"), None),
                    ],
                ),
            ),
        ),
        (
            "1. d4 d5 2. c4 {Queen's Gambit} dxc4 {Queen's Gambit Accepted}",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("d4"), PGNTurnMove("d5")),
                        PGNTurn(
                            2,
                            PGNTurnMove("c4", comment="Queen's Gambit"),
                            PGNTurnMove("dxc4", comment="Queen's Gambit Accepted"),
                        ),
                    ],
                ),
            ),
        ),
        (
            "1. d4 d5 2. c4 2... dxc4",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("d4"), PGNTurnMove("d5")),
                        PGNTurn(2, PGNTurnMove("c4"), None),
                        PGNTurn(2, None, PGNTurnMove("dxc4")),
                    ],
                ),
            ),
        ),
        (
            "1. d4 d5 2. c4 {Queen's Gambit} 2... dxc4 {Queen's Gambit Accepted}",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("d4"), PGNTurnMove("d5")),
                        PGNTurn(
                            2,
                            PGNTurnMove("c4", comment="Queen's Gambit"),
                            None,
                        ),
                        PGNTurn(
                            2,
                            None,
                            PGNTurnMove("dxc4", comment="Queen's Gambit Accepted"),
                        ),
                    ],
                ),
            ),
        ),
        (
            "1. e4 *",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), None)]),
                result=PGNGameResult.UNFINISHED,
            ),
        ),
        (
            "1. e4 1-0",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), None)]),
                result=PGNGameResult.WHITE_WINS,
            ),
        ),
        (
            "1. e4 0-1",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), None)]),
                result=PGNGameResult.BLACK_WINS,
            ),
        ),
        (
            "1. e4 1/2-1/2",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), None)]),
                result=PGNGameResult.DRAW,
            ),
        ),
        (
            "1. e4??",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4", annotation=PGNBasicAnnotation.BLUNDER), None)]),
            ),
        ),
        (
            "1. e4?!",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4", annotation=PGNBasicAnnotation.DUBIOUS_MOVE), None)]),
            ),
        ),
        (
            "1. e4!?",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [PGNTurn(1, PGNTurnMove("e4", annotation=PGNBasicAnnotation.INTERESTING_MOVE), None)],
                ),
            ),
        ),
        (
            "1. e4!",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4", annotation=PGNBasicAnnotation.GOOD_MOVE), None)]),
            ),
        ),
        (
            "1. e4!!",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4", annotation=PGNBasicAnnotation.BRILLIANT_MOVE), None)]),
            ),
        ),
        (
            "1. d4 $1",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("d4", extra_annotations=[1]), None)]),
            ),
        ),
        (
            "1. d4 $1 $2 $3",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("d4", extra_annotations=[1, 2, 3]), None)]),
            ),
        ),
        (
            textwrap.dedent(
                """
                [UTCDate "2025.01.13"]

                1. d4""",
            ).strip(),
            PGN(
                metadata={"UTCDate": "2025.01.13"},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("d4"), None)]),
            ),
        ),
        (
            textwrap.dedent(
                """
                [UTCDate "2025.01.13"]
                [UTCTime "22:18:02"]
                [Variant "Standard"]

                1. d4
                """,
            ).strip(),
            PGN(
                metadata={"UTCDate": "2025.01.13", "UTCTime": "22:18:02", "Variant": "Standard"},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("d4"), None)]),
            ),
        ),
        (
            "1. e4 (1... e5 2. Nf3) 1... c5",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), None),
                        PGNTurnList(
                            [
                                PGNTurn(1, None, PGNTurnMove("e5")),
                                PGNTurn(2, PGNTurnMove("Nf3"), None),
                            ],
                        ),
                        PGNTurn(1, None, PGNTurnMove("c5")),
                    ],
                ),
            ),
        ),
        (
            "1. e4 e5 (1... c5 2. Nf3 d6) (1... e6 2. d4 d5) 2. Nf3 Nc6",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5")),
                        PGNTurnList(
                            [
                                PGNTurn(1, None, PGNTurnMove("c5")),
                                PGNTurn(2, PGNTurnMove("Nf3"), PGNTurnMove("d6")),
                            ],
                        ),
                        PGNTurnList(
                            [
                                PGNTurn(1, None, PGNTurnMove("e6")),
                                PGNTurn(2, PGNTurnMove("d4"), PGNTurnMove("d5")),
                            ],
                        ),
                        PGNTurn(2, PGNTurnMove("Nf3"), PGNTurnMove("Nc6")),
                    ],
                ),
            ),
        ),
        (
            "1. e4 (1... e5 (2. Nf3 (2... Nc6 3. Bb5))) 1... c5",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), None),
                        PGNTurnList(
                            [
                                PGNTurn(1, None, PGNTurnMove("e5")),
                                PGNTurnList(
                                    [
                                        PGNTurn(2, PGNTurnMove("Nf3"), None),
                                        PGNTurnList(
                                            [
                                                PGNTurn(2, None, PGNTurnMove("Nc6")),
                                                PGNTurn(3, PGNTurnMove("Bb5"), None),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        PGNTurn(1, None, PGNTurnMove("c5")),
                    ],
                ),
            ),
        ),
        (
            "1. e4! $1 $2",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [
                        PGNTurn(
                            1,
                            PGNTurnMove("e4", annotation=PGNBasicAnnotation.GOOD_MOVE, extra_annotations=[1, 2]),
                            None,
                        ),
                    ],
                ),
            ),
        ),
        (
            "1. e4! $1 $2 {Good move} 1... e5?! $3",
            PGN(
                metadata={},
                turns=PGNTurnList(
                    [
                        PGNTurn(
                            1,
                            PGNTurnMove(
                                "e4",
                                annotation=PGNBasicAnnotation.GOOD_MOVE,
                                extra_annotations=[1, 2],
                                comment="Good move",
                            ),
                            None,
                        ),
                        PGNTurn(
                            1,
                            None,
                            PGNTurnMove("e5", annotation=PGNBasicAnnotation.DUBIOUS_MOVE, extra_annotations=[3]),
                        ),
                    ],
                ),
            ),
        ),
        (
            "{This is a global comment}",
            PGN(
                metadata={},
                turns=PGNTurnList([]),
                comment="This is a global comment",
            ),
        ),
    ],
    ids=[
        "1-move",
        "2-moves",
        "3-moves",
        "3-moves-with-comment",
        "4-moves-with-2-single-move-comments",
        "split-turn",
        "split-turn-with-comments",
        "unfinished-result",
        "white-win-result",
        "black-win-result",
        "draw-result",
        "blunder-annotation",
        "dubious-move-annotation",
        "interesting-move-annotation",
        "good-move-annotation",
        "brilliant-move-annotation",
        "single-extra-annotation",
        "multiple-extra-annotations",
        "metadata-single-field",
        "metadata-multiple-fields",
        "single-variation",
        "multiple-variations",
        "nested-variations",
        "basic-annotation-with-extra-annotations",
        "basic-annotation-with-extra-annotations-and-comment",
        "global-comment",
    ],
)
def test_parser(pgn: str, expected_ast: PGN):
    """Check if the parser is working correctly, checking that the result matches the expected AST."""
    parsed = PGN.from_string(pgn)
    assert parsed == expected_ast
