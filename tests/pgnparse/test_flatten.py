import pytest

from pgnparse import PGNTurn, PGNTurnList, PGNTurnMove


@pytest.mark.parametrize(
    ("inp", "expected"),
    [
        pytest.param(
            PGNTurnList([]),
            [PGNTurnList([])],
            id="empty",
        ),
        pytest.param(
            PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))]),
            [PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))])],
            id="mainline-only",
        ),
        pytest.param(
            # 1. e4 (1... e5 2. Nf3) 1... c5
            PGNTurnList(
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
            [
                PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5")),
                        PGNTurn(2, PGNTurnMove("Nf3"), None),
                    ],
                ),
                # mainline
                PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("c5"))]),
            ],
            id="single-variation",
        ),
        pytest.param(
            # 1. e4 e5 (1... c5 2. Nf3 d6) (1... e6 2. d4 d5) 2. Nf3 Nc6
            PGNTurnList(
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
            [
                PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("c5")),
                        PGNTurn(2, PGNTurnMove("Nf3"), PGNTurnMove("d6")),
                    ],
                ),
                PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e6")),
                        PGNTurn(2, PGNTurnMove("d4"), PGNTurnMove("d5")),
                    ],
                ),
                # mainline
                PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5")),
                        PGNTurn(2, PGNTurnMove("Nf3"), PGNTurnMove("Nc6")),
                    ],
                ),
            ],
            id="multiple-variations",
        ),
        pytest.param(
            # 1. e4 (1... e5 (2. Nf3 (2... Nc6 3. Bb5))) 1... c5
            PGNTurnList(
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
            [
                PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5")),
                        PGNTurn(2, PGNTurnMove("Nf3"), PGNTurnMove("Nc6")),
                        PGNTurn(3, PGNTurnMove("Bb5"), None),
                    ],
                ),
                PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5")),
                        PGNTurn(2, PGNTurnMove("Nf3"), None),
                    ],
                ),
                PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5")),
                    ],
                ),
                # mainline
                PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("c5"))]),
            ],
            id="nested-variations",
        ),
    ],
)
def test_flatten(inp: PGNTurnList, expected: list[PGNTurnList]):
    """Test that the flatten function works as expected."""
    assert list(inp.flatten()) == expected
