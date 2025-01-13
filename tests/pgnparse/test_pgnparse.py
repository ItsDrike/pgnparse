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
                result=PGNGameResult.UNSPECIFIED,
            ),
        ),
        (
            "1. e4 e5",
            PGN(
                metadata={},
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))]),
                result=PGNGameResult.UNSPECIFIED,
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
                result=PGNGameResult.UNSPECIFIED,
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
                result=PGNGameResult.UNSPECIFIED,
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
                result=PGNGameResult.UNSPECIFIED,
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
                result=PGNGameResult.UNSPECIFIED,
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
                result=PGNGameResult.UNSPECIFIED,
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
                result=PGNGameResult.UNSPECIFIED,
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
    ],
)
def test_parser(pgn: str, expected_ast: PGN):
    """Check if the parser is working correctly, checking that the result matches the expected AST."""
    parsed = PGN.from_string(pgn)
    assert parsed == expected_ast
