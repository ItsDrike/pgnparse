import textwrap
from typing import Any

import pytest

from pgnparse import PGN, PGNGameResult, PGNTurn, PGNTurnList, PGNTurnMove

# This avoids pyright complaining about unknown generic type
# as we'll be using the Any type in the parameterized tests a lot
PGNTurnListA = PGNTurnList[Any]


@pytest.mark.parametrize(
    ("ast", "expected"),
    [
        pytest.param(
            PGN(),
            "",
            id="empty",
        ),
        pytest.param(
            PGN(result=PGNGameResult.WHITE_WINS),
            "1-0",
            id="only-result",
        ),
        pytest.param(
            PGN(comment="This is a global comment."),
            "{This is a global comment.}",
            id="only-global-comment",
        ),
        pytest.param(
            PGN(turns=PGNTurnListA([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))])),
            "1. e4 e5",
            id="only-single-turn",
        ),
        pytest.param(
            PGN(
                turns=PGNTurnListA(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5")),
                        PGNTurn(2, PGNTurnMove("Nf3"), PGNTurnMove("Nc6")),
                    ],
                ),
            ),
            "1. e4 e5 2. Nf3 Nc6",
            id="only-multiple-turns",
        ),
        pytest.param(
            PGN(tags={"Event": "F/S Return Match"}),
            '[Event "F/S Return Match"]',
            id="only-single-tag",
        ),
        pytest.param(
            PGN(tags={"Event": "F/S Return Match", "Site": "Belgrade, Serbia"}),
            textwrap.dedent(
                """
                [Event "F/S Return Match"]
                [Site "Belgrade, Serbia"]
                """,
            ).strip(),
            id="only-multiple-tags",
        ),
    ],
)
def test_stringify(ast: PGN, expected: str):
    """Test that the AST is correctly stringified."""
    assert str(ast) == expected
