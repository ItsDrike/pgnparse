import textwrap

import pytest
from lark import UnexpectedInput

from pgnparse import PGN, PGNBasicAnnotation, PGNGameResult, PGNTurn, PGNTurnList, PGNTurnMove


@pytest.mark.parametrize(
    ("pgn", "expected_ast"),
    [
        pytest.param(
            "1. e8=Q",
            PGN(turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e8=Q"), None)])),
            id="promotion-move",
        ),
        pytest.param(
            "1. exf8=B+",
            PGN(turns=PGNTurnList([PGNTurn(1, PGNTurnMove("exf8=B+"), None)])),
            id="capture-and-underpromotion-with-check",
        ),
        pytest.param(
            "1. Rae1",
            PGN(turns=PGNTurnList([PGNTurn(1, PGNTurnMove("Rae1"), None)])),
            id="disambiguation-file",
        ),
        pytest.param(
            "1. R1e1",
            PGN(turns=PGNTurnList([PGNTurn(1, PGNTurnMove("R1e1"), None)])),
            id="disambiguation-rank",
        ),
        pytest.param(
            "1. Raxd1",
            PGN(turns=PGNTurnList([PGNTurn(1, PGNTurnMove("Raxd1"), None)])),
            id="disambiguation-file-and-capture",
        ),
        pytest.param(
            "1. O-O O-O-O",
            PGN(turns=PGNTurnList([PGNTurn(1, PGNTurnMove("O-O"), PGNTurnMove("O-O-O"))])),
            id="castling",
        ),
        pytest.param(
            "1. e4 e5",
            PGN(turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5"))])),
            id="2-moves",
        ),
        pytest.param(
            "1. d4 d5 2. c4",
            PGN(
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("d4"), PGNTurnMove("d5")),
                        PGNTurn(2, PGNTurnMove("c4"), None),
                    ],
                ),
            ),
            id="3-moves",
        ),
        pytest.param(
            "1. d4 d5 2. c4 {Queen's Gambit}",
            PGN(
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("d4"), PGNTurnMove("d5")),
                        PGNTurn(2, PGNTurnMove("c4", comment="Queen's Gambit"), None),
                    ],
                ),
            ),
            id="3-moves-with-comment",
        ),
        pytest.param(
            "1. d4 d5 2. c4 {Queen's Gambit} dxc4 {Queen's Gambit Accepted}",
            PGN(
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
            id="4-moves-with-2-single-move-comments",
        ),
        pytest.param(
            "1. d4 d5 2. c4 2... dxc4",
            PGN(
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("d4"), PGNTurnMove("d5")),
                        PGNTurn(2, PGNTurnMove("c4"), None),
                        PGNTurn(2, None, PGNTurnMove("dxc4")),
                    ],
                ),
            ),
            id="split-turn",
        ),
        pytest.param(
            "1. d4 d5 2. c4 {Queen's Gambit} 2... dxc4 {Queen's Gambit Accepted}",
            PGN(
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
            id="split-turn-with-comments",
        ),
        pytest.param(
            "1. e4 *",
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), None)]),
                result=PGNGameResult.UNFINISHED,
            ),
            id="unfinished-result",
        ),
        pytest.param(
            "1. e4 1-0",
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), None)]),
                result=PGNGameResult.WHITE_WINS,
            ),
            id="white-win-result",
        ),
        pytest.param(
            "1. e4 0-1",
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), None)]),
                result=PGNGameResult.BLACK_WINS,
            ),
            id="black-win-result",
        ),
        pytest.param(
            "1. e4 1/2-1/2",
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4"), None)]),
                result=PGNGameResult.DRAW,
            ),
            id="draw-result",
        ),
        pytest.param(
            "1-0",
            PGN(result=PGNGameResult.WHITE_WINS),
            id="standalone-result",
        ),
        pytest.param(
            "1. e4??",
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4", annotation=PGNBasicAnnotation.BLUNDER), None)]),
            ),
            id="blunder-annotation",
        ),
        pytest.param(
            "1. e4?!",
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4", annotation=PGNBasicAnnotation.DUBIOUS_MOVE), None)]),
            ),
            id="dubious-move-annotation",
        ),
        pytest.param(
            "1. e4!?",
            PGN(
                turns=PGNTurnList(
                    [PGNTurn(1, PGNTurnMove("e4", annotation=PGNBasicAnnotation.INTERESTING_MOVE), None)],
                ),
            ),
            id="interesting-move-annotation",
        ),
        pytest.param(
            "1. e4!",
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4", annotation=PGNBasicAnnotation.GOOD_MOVE), None)]),
            ),
            id="good-move-annotation",
        ),
        pytest.param(
            "1. e4!!",
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("e4", annotation=PGNBasicAnnotation.BRILLIANT_MOVE), None)]),
            ),
            id="brilliant-move-annotation",
        ),
        pytest.param(
            "1. d4 $1",
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("d4", numeric_annotations=[1]), None)]),
            ),
            id="single-numeric-annotation",
        ),
        pytest.param(
            "1. d4 $1 $2 $3",
            PGN(
                turns=PGNTurnList([PGNTurn(1, PGNTurnMove("d4", numeric_annotations=[1, 2, 3]), None)]),
            ),
            id="multiple-numeric-annotations",
        ),
        pytest.param(
            '[EmptyTag ""]',
            PGN(tags={"EmptyTag": ""}),
            id="tags-single-empty",
        ),
        pytest.param(
            '[UTCDate "2025.01.13"]',
            PGN(tags={"UTCDate": "2025.01.13"}),
            id="tags-single",
        ),
        pytest.param(
            r'[Event "A \"quote\" in tag"]',
            PGN(tags={"Event": r"A \"quote\" in tag"}),
            id="tags-single-quote-escape",
        ),
        pytest.param(
            textwrap.dedent(
                """
                [UTCDate "2025.01.13"]
                [UTCTime "22:18:02"]
                [Variant "Standard"]
                """,
            ).strip(),
            PGN(
                tags={
                    "UTCDate": "2025.01.13",
                    "UTCTime": "22:18:02",
                    "Variant": "Standard",
                },
            ),
            id="tags-multiple",
        ),
        pytest.param(
            "1. e4 (1... e5 2. Nf3) 1... c5",
            PGN(
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
            id="single-variation",
        ),
        pytest.param(
            "1. e4 e5 (1... c5 2. Nf3 d6) (1... e6 2. d4 d5) 2. Nf3 Nc6",
            PGN(
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
            id="multiple-variations",
        ),
        pytest.param(
            "1. e4 (1... e5 (2. Nf3 (2... Nc6 3. Bb5))) 1... c5",
            PGN(
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
            id="nested-variations",
        ),
        pytest.param(
            "1. e4! $1 $2",
            PGN(
                turns=PGNTurnList(
                    [
                        PGNTurn(
                            1,
                            PGNTurnMove(
                                "e4",
                                annotation=PGNBasicAnnotation.GOOD_MOVE,
                                numeric_annotations=[1, 2],
                            ),
                            None,
                        ),
                    ],
                ),
            ),
            id="basic-annotation-with-numeric-annotations",
        ),
        pytest.param(
            "1. e4! $1 $2 {Good move} 1... e5?! $3",
            PGN(
                turns=PGNTurnList(
                    [
                        PGNTurn(
                            1,
                            PGNTurnMove(
                                "e4",
                                annotation=PGNBasicAnnotation.GOOD_MOVE,
                                numeric_annotations=[1, 2],
                                comment="Good move",
                            ),
                            None,
                        ),
                        PGNTurn(
                            1,
                            None,
                            PGNTurnMove(
                                "e5",
                                annotation=PGNBasicAnnotation.DUBIOUS_MOVE,
                                numeric_annotations=[3],
                            ),
                        ),
                    ],
                ),
            ),
            id="basic-annotation-with-numeric-annotations-and-comment",
        ),
        pytest.param(
            "{This is a global block comment}",
            PGN(comment="This is a global block comment"),
            id="global-block-comment",
        ),
        pytest.param(
            # Note: Line comment spec should end with a newline, it's not clear
            # whether this newline is optional when there's nothing else in the PGN.
            # The parser will currently expects a newline.
            ";This is a global line comment\n",
            PGN(comment="This is a global line comment"),
            id="global-line-comment",
        ),
        pytest.param(
            "",
            PGN(),
            id="empty",
        ),
        pytest.param(
            "2051. e4",
            PGN(turns=PGNTurnList([PGNTurn(2051, PGNTurnMove("e4"), None)])),
            id="large-turn-number",
        ),
        pytest.param(
            textwrap.dedent(
                """
                [Event "F/S Return Match"]
                [Site "Belgrade, Serbia JUG"]
                [Date "1992.11.04"]
                [Round "29"]
                [White "Fischer, Robert J."]
                [Black "Spassky, Boris V."]
                [Result "1/2-1/2"]

                1.e4 e5 2.Nf3 Nc6 3.Bb5 {This opening is called the Ruy Lopez.} 3...a6
                4.Ba4 Nf6 5.O-O Be7 6.Re1 b5 7.Bb3 d6 8.c3 O-O 9.h3 Nb8 10.d4 Nbd7
                11.c4 c6 12.cxb5 axb5 13.Nc3 Bb7 14.Bg5 b4 15.Nb1 h6 16.Bh4 c5 17.dxe5
                Nxe4 18.Bxe7 Qxe7 19.exd6 Qf6 20.Nbd2 Nxd6 21.Nc4 Nxc4 22.Bxc4 Nb6
                23.Ne5 Rae8 24.Bxf7+ Rxf7 25.Nxf7 Rxe1+ 26.Qxe1 Kxf7 27.Qe3 Qg5 28.Qxg5
                hxg5 29.b3 Ke6 30.a3 Kd6 31.axb4 cxb4 32.Ra5 Nd5 33.f3 Bc8 34.Kf2 Bf5
                35.Ra7 g6 36.Ra6+ Kc5 37.Ke1 Nf4 38.g3 Nxh3 39.Kd2 Kb5 40.Rd6 Kc5 41.Ra6
                Nf2 42.g4 Bd3 43.Re6 1/2-1/2
                """,
            ).strip(),
            PGN(
                tags={
                    "Event": "F/S Return Match",
                    "Site": "Belgrade, Serbia JUG",
                    "Date": "1992.11.04",
                    "Round": "29",
                    "White": "Fischer, Robert J.",
                    "Black": "Spassky, Boris V.",
                    "Result": "1/2-1/2",
                },
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5")),
                        PGNTurn(2, PGNTurnMove("Nf3"), PGNTurnMove("Nc6")),
                        PGNTurn(3, PGNTurnMove("Bb5", comment="This opening is called the Ruy Lopez."), None),
                        PGNTurn(3, None, PGNTurnMove("a6")),
                        PGNTurn(4, PGNTurnMove("Ba4"), PGNTurnMove("Nf6")),
                        PGNTurn(5, PGNTurnMove("O-O"), PGNTurnMove("Be7")),
                        PGNTurn(6, PGNTurnMove("Re1"), PGNTurnMove("b5")),
                        PGNTurn(7, PGNTurnMove("Bb3"), PGNTurnMove("d6")),
                        PGNTurn(8, PGNTurnMove("c3"), PGNTurnMove("O-O")),
                        PGNTurn(9, PGNTurnMove("h3"), PGNTurnMove("Nb8")),
                        PGNTurn(10, PGNTurnMove("d4"), PGNTurnMove("Nbd7")),
                        PGNTurn(11, PGNTurnMove("c4"), PGNTurnMove("c6")),
                        PGNTurn(12, PGNTurnMove("cxb5"), PGNTurnMove("axb5")),
                        PGNTurn(13, PGNTurnMove("Nc3"), PGNTurnMove("Bb7")),
                        PGNTurn(14, PGNTurnMove("Bg5"), PGNTurnMove("b4")),
                        PGNTurn(15, PGNTurnMove("Nb1"), PGNTurnMove("h6")),
                        PGNTurn(16, PGNTurnMove("Bh4"), PGNTurnMove("c5")),
                        PGNTurn(17, PGNTurnMove("dxe5"), PGNTurnMove("Nxe4")),
                        PGNTurn(18, PGNTurnMove("Bxe7"), PGNTurnMove("Qxe7")),
                        PGNTurn(19, PGNTurnMove("exd6"), PGNTurnMove("Qf6")),
                        PGNTurn(20, PGNTurnMove("Nbd2"), PGNTurnMove("Nxd6")),
                        PGNTurn(21, PGNTurnMove("Nc4"), PGNTurnMove("Nxc4")),
                        PGNTurn(22, PGNTurnMove("Bxc4"), PGNTurnMove("Nb6")),
                        PGNTurn(23, PGNTurnMove("Ne5"), PGNTurnMove("Rae8")),
                        PGNTurn(24, PGNTurnMove("Bxf7+"), PGNTurnMove("Rxf7")),
                        PGNTurn(25, PGNTurnMove("Nxf7"), PGNTurnMove("Rxe1+")),
                        PGNTurn(26, PGNTurnMove("Qxe1"), PGNTurnMove("Kxf7")),
                        PGNTurn(27, PGNTurnMove("Qe3"), PGNTurnMove("Qg5")),
                        PGNTurn(28, PGNTurnMove("Qxg5"), PGNTurnMove("hxg5")),
                        PGNTurn(29, PGNTurnMove("b3"), PGNTurnMove("Ke6")),
                        PGNTurn(30, PGNTurnMove("a3"), PGNTurnMove("Kd6")),
                        PGNTurn(31, PGNTurnMove("axb4"), PGNTurnMove("cxb4")),
                        PGNTurn(32, PGNTurnMove("Ra5"), PGNTurnMove("Nd5")),
                        PGNTurn(33, PGNTurnMove("f3"), PGNTurnMove("Bc8")),
                        PGNTurn(34, PGNTurnMove("Kf2"), PGNTurnMove("Bf5")),
                        PGNTurn(35, PGNTurnMove("Ra7"), PGNTurnMove("g6")),
                        PGNTurn(36, PGNTurnMove("Ra6+"), PGNTurnMove("Kc5")),
                        PGNTurn(37, PGNTurnMove("Ke1"), PGNTurnMove("Nf4")),
                        PGNTurn(38, PGNTurnMove("g3"), PGNTurnMove("Nxh3")),
                        PGNTurn(39, PGNTurnMove("Kd2"), PGNTurnMove("Kb5")),
                        PGNTurn(40, PGNTurnMove("Rd6"), PGNTurnMove("Kc5")),
                        PGNTurn(41, PGNTurnMove("Ra6"), PGNTurnMove("Nf2")),
                        PGNTurn(42, PGNTurnMove("g4"), PGNTurnMove("Bd3")),
                        PGNTurn(43, PGNTurnMove("Re6"), None),
                    ],
                ),
                result=PGNGameResult.DRAW,
            ),
            id="full-game",
        ),
        pytest.param(
            """
            [Event "F/S Return Match"]
            [Site "Belgrade, Serbia JUG"]
            [Date "1992.11.04"]

            [Round "29"]
            [White "Fischer, Robert J."]


            [Black "Spassky, Boris V."]
            [Result "1/2-1/2"]
            1.e4 e5\t2.Nf3 Nc6 3.Bb5{This opening is called the Ruy Lopez.} 3...a6
            4.Ba4 Nf6 5.O-O Be7 6.Re1 b5 7. Bb3 d6 8.c3\tO-O 9.h3 Nb8 10.d4 Nbd7
            11.c4 c6 12.cxb5 axb5 13.Nc3 Bb7 14.Bg5 b4 15.Nb1 h6 16.Bh4 c5 17.dxe5
            Nxe4 18.Bxe7 Qxe7     19.exd6 Qf6 20.Nbd2 \t Nxd6 21.Nc4 Nxc4 22.Bxc4 Nb6
            23.Ne5 Rae8 24.Bxf7+ Rxf7 25.Nxf7 Rxe1+ 26.Qxe1 Kxf7 27.Qe3 Qg5 28.Qxg5
            hxg5 29.b3 Ke6 30.a3 Kd6 31.axb4 cxb4 32.Ra5 Nd5 33.f3 Bc8 34.Kf2 Bf5
            35.Ra7 g6            36.Ra6+ Kc5
            37.Ke1 Nf4 38.g3 Nxh3 39.   Kd2 Kb5 40.Rd6 Kc5 41.Ra6
            Nf2 42.g4 Bd3 43. Re6 \t\t1/2-1/2


            """,
            PGN(
                tags={
                    "Event": "F/S Return Match",
                    "Site": "Belgrade, Serbia JUG",
                    "Date": "1992.11.04",
                    "Round": "29",
                    "White": "Fischer, Robert J.",
                    "Black": "Spassky, Boris V.",
                    "Result": "1/2-1/2",
                },
                turns=PGNTurnList(
                    [
                        PGNTurn(1, PGNTurnMove("e4"), PGNTurnMove("e5")),
                        PGNTurn(2, PGNTurnMove("Nf3"), PGNTurnMove("Nc6")),
                        PGNTurn(3, PGNTurnMove("Bb5", comment="This opening is called the Ruy Lopez."), None),
                        PGNTurn(3, None, PGNTurnMove("a6")),
                        PGNTurn(4, PGNTurnMove("Ba4"), PGNTurnMove("Nf6")),
                        PGNTurn(5, PGNTurnMove("O-O"), PGNTurnMove("Be7")),
                        PGNTurn(6, PGNTurnMove("Re1"), PGNTurnMove("b5")),
                        PGNTurn(7, PGNTurnMove("Bb3"), PGNTurnMove("d6")),
                        PGNTurn(8, PGNTurnMove("c3"), PGNTurnMove("O-O")),
                        PGNTurn(9, PGNTurnMove("h3"), PGNTurnMove("Nb8")),
                        PGNTurn(10, PGNTurnMove("d4"), PGNTurnMove("Nbd7")),
                        PGNTurn(11, PGNTurnMove("c4"), PGNTurnMove("c6")),
                        PGNTurn(12, PGNTurnMove("cxb5"), PGNTurnMove("axb5")),
                        PGNTurn(13, PGNTurnMove("Nc3"), PGNTurnMove("Bb7")),
                        PGNTurn(14, PGNTurnMove("Bg5"), PGNTurnMove("b4")),
                        PGNTurn(15, PGNTurnMove("Nb1"), PGNTurnMove("h6")),
                        PGNTurn(16, PGNTurnMove("Bh4"), PGNTurnMove("c5")),
                        PGNTurn(17, PGNTurnMove("dxe5"), PGNTurnMove("Nxe4")),
                        PGNTurn(18, PGNTurnMove("Bxe7"), PGNTurnMove("Qxe7")),
                        PGNTurn(19, PGNTurnMove("exd6"), PGNTurnMove("Qf6")),
                        PGNTurn(20, PGNTurnMove("Nbd2"), PGNTurnMove("Nxd6")),
                        PGNTurn(21, PGNTurnMove("Nc4"), PGNTurnMove("Nxc4")),
                        PGNTurn(22, PGNTurnMove("Bxc4"), PGNTurnMove("Nb6")),
                        PGNTurn(23, PGNTurnMove("Ne5"), PGNTurnMove("Rae8")),
                        PGNTurn(24, PGNTurnMove("Bxf7+"), PGNTurnMove("Rxf7")),
                        PGNTurn(25, PGNTurnMove("Nxf7"), PGNTurnMove("Rxe1+")),
                        PGNTurn(26, PGNTurnMove("Qxe1"), PGNTurnMove("Kxf7")),
                        PGNTurn(27, PGNTurnMove("Qe3"), PGNTurnMove("Qg5")),
                        PGNTurn(28, PGNTurnMove("Qxg5"), PGNTurnMove("hxg5")),
                        PGNTurn(29, PGNTurnMove("b3"), PGNTurnMove("Ke6")),
                        PGNTurn(30, PGNTurnMove("a3"), PGNTurnMove("Kd6")),
                        PGNTurn(31, PGNTurnMove("axb4"), PGNTurnMove("cxb4")),
                        PGNTurn(32, PGNTurnMove("Ra5"), PGNTurnMove("Nd5")),
                        PGNTurn(33, PGNTurnMove("f3"), PGNTurnMove("Bc8")),
                        PGNTurn(34, PGNTurnMove("Kf2"), PGNTurnMove("Bf5")),
                        PGNTurn(35, PGNTurnMove("Ra7"), PGNTurnMove("g6")),
                        PGNTurn(36, PGNTurnMove("Ra6+"), PGNTurnMove("Kc5")),
                        PGNTurn(37, PGNTurnMove("Ke1"), PGNTurnMove("Nf4")),
                        PGNTurn(38, PGNTurnMove("g3"), PGNTurnMove("Nxh3")),
                        PGNTurn(39, PGNTurnMove("Kd2"), PGNTurnMove("Kb5")),
                        PGNTurn(40, PGNTurnMove("Rd6"), PGNTurnMove("Kc5")),
                        PGNTurn(41, PGNTurnMove("Ra6"), PGNTurnMove("Nf2")),
                        PGNTurn(42, PGNTurnMove("g4"), PGNTurnMove("Bd3")),
                        PGNTurn(43, PGNTurnMove("Re6"), None),
                    ],
                ),
                result=PGNGameResult.DRAW,
            ),
            id="full-game-extra-whitespace",
        ),
        pytest.param(
            " ".join(f"{i}. e4 e5" for i in range(1, 301)),
            PGN(
                turns=PGNTurnList(
                    [PGNTurn(i, PGNTurnMove("e4"), PGNTurnMove("e5")) for i in range(1, 301)],
                ),
            ),
            id="large-game",
        ),
    ],
)
def test_valid_pgn(pgn: str, expected_ast: PGN):
    """Check if given valid PGN is parsed correctly (matches the expected AST)."""
    parsed = PGN.from_string(pgn)
    assert parsed == expected_ast


@pytest.mark.parametrize(
    "pgn",
    [
        pytest.param(
            "(1. e4)",
            id="variation-without-mainline",
        ),
        pytest.param(
            "e4 e5",
            id="missing-turn-number",
        ),
        pytest.param(
            "1. e4 $-1",
            id="negative-numeric-annotation",
        ),
        pytest.param(
            "1. e4 {First comment} {Second comment}",
            id="multiple-turn-comments",
        ),
        pytest.param(
            "{First comment} {Second comment}\n1. e4",
            id="multiple-global-comments",
        ),
        pytest.param(
            # we might want to allow this in the future
            """
            ;This is a comment before tags
            [Event "Game"]
            """,
            id="global-comment-before-tags",
        ),
        pytest.param(
            "1. e4 (1... e5",
            id="unclosed-variation",
        ),
        pytest.param(
            "1. e4 {This comment is not closed",
            id="unclosed-turn-comment",
        ),
        pytest.param(
            "1. Qa9",
            id="invalid-move-rank",
        ),
        pytest.param(
            "1. Qi8",
            id="invalid-move-file",
        ),
        pytest.param(
            "1. Pg5",
            id="invalid-move-piece",
        ),
        pytest.param(
            "1. P&5",
            id="invalid-move-special-char",
        ),
        pytest.param(
            "1. e4e5",
            id="no-space-between-moves",
        ),
        pytest.param(
            "1. e4 e52. Nf3",
            id="no-space-between-turns",
        ),
        pytest.param(
            # we might want to allow this in the future
            "1. e4 e5 1/2-1/2 {Draw agreed}",
            id="draw-comment",
        ),
        pytest.param(
            # we might want to allow this in the future
            "1. d4 {}",
            id="empty-comment",
        ),
        pytest.param(
            "1. e4 e5 1-0 0-1",
            id="multiple-results",
        ),
        pytest.param(
            "[Event]",
            id="tag-missing-value",
        ),
        pytest.param(
            '[Event "Missing end quote]',
            id="tag-unclosed-value",
        ),
    ],
)
def test_invalid_pgn(pgn: str):
    """Check if given invalid PGN raises an exception during parsing/lexing."""
    with pytest.raises(UnexpectedInput):
        _ = PGN.from_string(pgn)
