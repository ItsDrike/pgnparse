import textwrap

import pytest

from pgnparse import PGN, PGNGameResult, PGNTurn, PGNTurnList, PGNTurnMove


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
            id="result-only",
        ),
        pytest.param(
            PGN(comment="This is a global comment."),
            "{This is a global comment.}",
            id="global-comment",
        ),
        pytest.param(
            PGN(comment="This is a global comment.\nIt spans multiple lines."),
            "{This is a global comment.\nIt spans multiple lines.}",
            id="global-comment-multiline",
        ),
        pytest.param(
            PGN(turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), None)])),
            "1. e4",
            id="single-move-turn",
        ),
        pytest.param(
            PGN(turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))])),
            "1. e4 e5",
            id="single-turn",
        ),
        pytest.param(
            PGN(
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5")),
                        PGNTurn(2, PGNTurnMove("Nf3"), PGNTurnMove("Nc6")),
                    ],
                ),
            ),
            "1. e4 e5 2. Nf3 Nc6",
            id="multiple-turns",
        ),
        pytest.param(
            PGN(turns=PGNTurnList([PGNTurn(1, None, PGNTurnMove("e5"))])),
            "1... e5",
            id="single-continuation-turn",
        ),
        pytest.param(
            PGN(turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5", comment="Comment"))])),
            "1. e4 e5 {Comment}",
            id="single-turn-with-comment",
        ),
        pytest.param(
            PGN(
                turns=PGNTurnList(
                    [
                        PGNTurn(
                            1,
                            PGNTurnMove("e4", comment="Comment1"),
                            PGNTurnMove("e5", comment="Comment2"),
                        ),
                    ],
                ),
            ),
            "1. e4 {Comment1} e5 {Comment2}",
            id="single-turn-with-two-comments",
        ),
        pytest.param(
            PGN(turns=PGNTurnList([PGNTurn(1, None, PGNTurnMove("e5", comment="Comment"))])),
            "1... e5 {Comment}",
            id="single-continuation-turn-with-comment",
        ),
        pytest.param(
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))]),
                result=PGNGameResult.WHITE_WINS,
            ),
            "1. e4 e5 1-0",
            id="single-turn-and-result",
        ),
        pytest.param(
            PGN(tags={"Event": "F/S Return Match"}),
            '[Event "F/S Return Match"]',
            id="single-tag",
        ),
        pytest.param(
            PGN(tags={"Key": 'Value with "quotes"'}),
            '[Key "Value with \\"quotes\\""]',
            id="single-tag-with-escaped-value",
        ),
        pytest.param(
            PGN(tags={"Event": "F/S Return Match", "Site": "Belgrade, Serbia"}),
            textwrap.dedent(
                """
                [Event "F/S Return Match"]
                [Site "Belgrade, Serbia"]
                """,
            ).strip(),
            id="multiple-tags",
        ),
        pytest.param(
            PGN(tags={"Event": "F/S Return Match"}, comment="This is a global comment."),
            textwrap.dedent(
                """
                [Event "F/S Return Match"]

                {This is a global comment.}
                """,
            ).strip(),
            id="tags-and-global-comment",
        ),
        pytest.param(
            PGN(
                tags={"Event": "F/S Return Match"},
                turns=PGNTurnList(
                    [PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))],
                ),
            ),
            textwrap.dedent(
                """
                [Event "F/S Return Match"]

                1. e4 e5
                """,
            ).strip(),
            id="tag-and-single-turn",
        ),
        pytest.param(
            PGN(
                comment="This is a global comment.",
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))]),
            ),
            textwrap.dedent(
                """
                {This is a global comment.}
                1. e4 e5
                """,
            ).strip(),
            id="global-comment-and-single-turn",
        ),
        pytest.param(
            PGN(
                tags={"Event": "F/S Return Match"},
                comment="This is a global comment.",
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))]),
            ),
            textwrap.dedent(
                """
                [Event "F/S Return Match"]

                {This is a global comment.}
                1. e4 e5
                """,
            ).strip(),
            id="tag-with-global-comment-and-single-turn",
        ),
    ],
)
def test_stringify(ast: PGN, expected: str):
    """Test that the AST is correctly stringified."""
    assert str(ast) == expected
