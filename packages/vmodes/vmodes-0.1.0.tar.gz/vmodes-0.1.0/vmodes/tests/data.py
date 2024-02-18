#
# VModeS - vectorized decoding of Mode S and ADS-B data
#
# Copyright (C) 2020-2024 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import numpy as np
import typing as tp

NO_COORD = np.nan
EMPTY_STATE: dict[str, list[tp.Any]] = {
    'icao': [], 'time': [], 'position': [], 'valid': [], 'carry_over_time': [],
    'prev_position': [],
}

# legend for a stream of messages
#
#   . - any non-position message
#   o - position message, odd cpr format type
#   e - position message, even cpr format type
#   i - message for non-valid position
#   [a] - all following position messages are airborne ones
#   [s] - all following position messages are surface ones
#   <space> - new chunk of messages in a stream

# test: no crash, when no ads-b position messages in input
# stream: ...
P_MSG_0 = (
    (0, 1676212322.500000,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212324.104649, '8d4ca4edea1978677b1c086aa538',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 29 n -
    (0, 1676212324.594973,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
)
P_STATE_0 = (EMPTY_STATE,)

# test: last known airborne position is reused in a next chunk of messages
#       in a stream
# stream: [a].o.e..e.o. .ee. .i..o.
P_MSG_1 = (
    (0, 1676212322.500000,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212323.707462, '8d4ca4ed5861a6af48fc38424c44',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 1
    (0, 1676212324.104649, '8d4ca4edea1978677b1c086aa538',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 29 n -
    (0, 1676212324.254611, '8d4ca4ed5861a345e0f4bf8d3262', (-5.21980286, 52.90942383)),  # 4ca4ed 17 11 a 0
    (0, 1676212324.593688,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212324.594973,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212325.297388, '8d4ca4ed5861934616f4a174496e', (-5.22209167, 52.91065979)),  # 4ca4ed 17 11 a 0
    (0, 1676212325.620938,               '5d4ca4edb27622',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212325.898300, '8d4ca4ed586186afaefc022b21cb', (-5.22305734, 52.91122695)),  # 4ca4ed 17 11 a 1  last known position
    (0, 1676212326.333228, '8d4ca4ed990d011d986420804acb',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 19 n -

    (1, 1676212326.600000,               '5d4ca4edb2762f',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (1, 1676212326.665183, '8d4ca4ed586173465af47d7a165b', (-5.22483826, 52.91221619)),  # 4ca4ed 17 11 a 0
    (1, 1676212327.212929, '8d4ca4ed5861634672f4709ed8c9', (-5.22583008, 52.91276550)),  # 4ca4ed 17 11 a 0  last known position
    (1, 1676212327.100000,               '5d4ca4edb2762f',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -

    (2, 1676212327.814243, '8d4ca4edf82300060048784c3105',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 31 n -
    (2, 1676212327.817334, '8d4ca4ed586165bfd578531f21ce',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 1  invalid
    (2, 1676212327.973889, '8d4ca4ed990d001d98681f359b25',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 19 n -
    (2, 1676212328.348986,               '5d4ca4edb27622',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (2, 1676212328.351835, '8d4ca4ed586156b024fbc321d7af', (-5.22800119, 52.91397353)),  # 4ca4ed 17 11 a 1
    (2, 1676212328.460821, '8d4ca4ed990d001d986820cb1a05',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 19 n -
)
P_STATE_1 = (
    {'icao': [0x4ca4ed], 'time': [1676212325.898300], 'position': [(-5.22305734, 52.91122695)], 'valid': [True], 'prev_position': [], 'carry_over_time': []},
    {'icao': [0x4ca4ed], 'time': [1676212327.212929], 'position': [(-5.22583008, 52.91276550)], 'valid': [True], 'prev_position': [], 'carry_over_time': []},
    {'icao': [0x4ca4ed], 'time': [1676212328.351835], 'position': [(-5.22800119, 52.91397353)], 'valid': [True], 'prev_position': [], 'carry_over_time': []},
)

# test: use ads-b position messages from one previous chunk to determine
#       global position, validate that position, and calculate new positions;
#       positions from the previous chunk are stored as "previous positions"
# stream: [a].o.e..e .o..ee.
P_MSG_2 = (
    (0, 1676212322.500000,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212323.707462, '8d4ca4ed5861a6af48fc38424c44',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 1  validated here
    (0, 1676212324.104649, '8d4ca4edea1978677b1c086aa538',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 29 n -
    (0, 1676212324.254611, '8d4ca4ed5861a345e0f4bf8d3262',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 0  (-5.21980286, 52.90942383)
    (0, 1676212324.593688,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212324.594973,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212325.297388, '8d4ca4ed5861934616f4a174496e',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 0  (-5.22209167, 52.91065979)

    (1, 1676212325.620938,               '5d4ca4edb27622',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (1, 1676212325.898300, '8d4ca4ed586186afaefc022b21cb', (-5.22305734, 52.91122695)),  # 4ca4ed 17 11 a 1
    (1, 1676212326.333228, '8d4ca4ed990d011d986420804acb',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 19 n -
    (1, 1676212326.600000,               '5d4ca4edb2762f',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (1, 1676212326.665183, '8d4ca4ed586173465af47d7a165b', (-5.22483826, 52.91221619)),  # 4ca4ed 17 11 a 0
    (1, 1676212327.212929, '8d4ca4ed5861634672f4709ed8c9', (-5.22583008, 52.91276550)),  # 4ca4ed 17 11 a 0
    (1, 1676212327.100000,               '5d4ca4edb2762f',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
)
P_STATE_2 = (
    {
        'icao': [0x4ca4ed],
        'time': [1676212323.707462],
        'position': [(0, 0)],
        'valid': [False],
        'carry_over_time': [1676212323.707462, 1676212324.254611, 1676212325.297388],
        'prev_position': [],
    },
    {
        'icao': [0x4ca4ed],
        'time': [1676212327.212929],
        'position': [(-5.22583008, 52.91276550)],
        'valid': [True],
        'carry_over_time': [],
        'prev_position': [(-5.21980286, 52.90942383), (-5.22209167, 52.91065979)],
    },
)

# test: use ads-b position messages from two previous chunks to determine
#       global position, validate that position, and calculate new positions;
#       positions from the previous chunks are stored as "previous positions"
# stream: [a].o.e ..e .o..ee.
P_MSG_3 = (
    (0, 1676212322.500000,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212323.707462, '8d4ca4ed5861a6af48fc38424c44',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 1  validated here
    (0, 1676212324.104649, '8d4ca4edea1978677b1c086aa538',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 29 n -
    (0, 1676212324.254611, '8d4ca4ed5861a345e0f4bf8d3262',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 0  (-5.21980286, 52.90942383)

    (1, 1676212324.593688,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (1, 1676212324.594973,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (1, 1676212325.297388, '8d4ca4ed5861934616f4a174496e',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 0  (-5.22209167, 52.91065979)

    (2, 1676212325.620938,               '5d4ca4edb27622',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (2, 1676212325.898300, '8d4ca4ed586186afaefc022b21cb', (-5.22305734, 52.91122695)),  # 4ca4ed 17 11 a 1
    (2, 1676212326.333228, '8d4ca4ed990d011d986420804acb',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 19 n -
    (2, 1676212326.600000,               '5d4ca4edb2762f',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (2, 1676212326.665183, '8d4ca4ed586173465af47d7a165b', (-5.22483826, 52.91221619)),  # 4ca4ed 17 11 a 0
    (2, 1676212327.212929, '8d4ca4ed5861634672f4709ed8c9', (-5.22583008, 52.91276550)),  # 4ca4ed 17 11 a 0
    (2, 1676212327.100000,               '5d4ca4edb2762f',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
)
P_STATE_3 = (
    {
        'icao': [0x4ca4ed],
        'time': [1676212323.707462],
        'position': [(0, 0)],
        'valid': [False],
        'carry_over_time': [1676212323.707462, 1676212324.254611],
        'prev_position': [],
    },
    {
        'icao': [0x4ca4ed],
        'time': [1676212323.707462],
        'position': [(0, 0)],
        'valid': [False],
        'carry_over_time': [1676212323.707462, 1676212324.254611, 1676212325.297388],
        'prev_position': [],
    },
    {
        'icao': [0x4ca4ed],
        'time': [1676212327.212929],
        'position': [(-5.22583008, 52.91276550)],
        'valid': [True],
        'carry_over_time': [],
        'prev_position': [(-5.21980286, 52.90942383), (-5.22209167, 52.91065979)],
    },
)

# test: carry over data of ads-b messages is correct; use of carry over data
#       does not generate additional positions
# stream: [a]o[+50s]o[+10s].o.e..e.o ..ee.
P_MSG_4 = (
    (0, 1676212272.000000, '8d4ca4ed5861a6af48fc38424c44',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 1
    (0, 1676212312.000000, '8d4ca4ed5861a6af48fc38424c44',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 1  can generate additional previous message
    (0, 1676212322.500000,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212323.707462, '8d4ca4ed5861a6af48fc38424c44',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 11 a 1
    (0, 1676212324.104649, '8d4ca4edea1978677b1c086aa538',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 29 n -
    (0, 1676212324.254611, '8d4ca4ed5861a345e0f4bf8d3262', (-5.21980286, 52.90942383)),  # 4ca4ed 17 11 a 0
    (0, 1676212324.593688,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212324.594973,               '5d4ca4edb27614',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212325.297388, '8d4ca4ed5861934616f4a174496e', (-5.22209167, 52.91065979)),  # 4ca4ed 17 11 a 0
    (0, 1676212325.620938,               '5d4ca4edb27622',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (0, 1676212325.898300, '8d4ca4ed586186afaefc022b21cb', (-5.22305734, 52.91122695)),  # 4ca4ed 17 11 a 1

    (1, 1676212326.333228, '8d4ca4ed990d011d986420804acb',       (NO_COORD, NO_COORD)),  # 4ca4ed 17 19 n -
    (1, 1676212326.600000,               '5d4ca4edb2762f',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
    (1, 1676212326.665183, '8d4ca4ed586173465af47d7a165b', (-5.22483826, 52.91221619)),  # 4ca4ed 17 11 a 0
    (1, 1676212327.212929, '8d4ca4ed5861634672f4709ed8c9', (-5.22583008, 52.91276550)),  # 4ca4ed 17 11 a 0
    (1, 1676212327.100000,               '5d4ca4edb2762f',       (NO_COORD, NO_COORD)),  # 4ca4ed 11 -- n -
)
P_STATE_4 = (
    {
        'icao': [0x4ca4ed],
        'time': [1676212325.898300],
        'position': [(-5.22305734, 52.91122695)],
        'valid': [True],
        'carry_over_time': [1676212312.000000],
        'prev_position': [],
    },
    {
        'icao': [0x4ca4ed],
        'time': [1676212327.212929],
        'position': [(-5.22583008, 52.91276550)],
        'valid': [True],
        'carry_over_time': [],
        'prev_position': [],
    },
)

# test: last known surface position is reused in a next chunk of messages
#       in a stream; a positions fail local reasonabless test
# stream: [s]o[+6s]o.[+46s]e..o.o.o.e e.
P_MSG_5 = (
    (0, 1704108111.759284, '8c4ca98c3810041bc544b1cd83ac',       (NO_COORD, NO_COORD)),  # 4ca98c 17 07 s 1  even message > 50 sec
    (0, 1704108118.323862, '8c4ca98c3810041bc544b1cd83ac',       (NO_COORD, NO_COORD)),  # 4ca98c 17 07 s 1  next position fails reasonabless test (local)
    (0, 1704108118.487454, '8c4ca98cf9002202804a30209afd',       (NO_COORD, NO_COORD)),  # 4ca98c 17 31 n -
    (0, 1704108164.525671, '8c4ca98c3920027ba12107e70fc7',       (NO_COORD, NO_COORD)),  # 4ca98c 17 07 s 0
    (0, 1704108167.914949, '8c4ca98cf9002202804a30209afd',       (NO_COORD, NO_COORD)),  # 4ca98c 17 31 n -
    (0, 1704108169.604120, '8c4ca98cf9002202804a30209afd',       (NO_COORD, NO_COORD)),  # 4ca98c 17 31 n -
    (0, 1704108169.874646, '8c4ca98c3910041bad449fb14ad9', (-6.26287348, 53.43105252)),  # 4ca98c 17 07 s 1
    (0, 1704108172.112674, '8c4ca98cf9002202804a30209afd',       (NO_COORD, NO_COORD)),  # 4ca98c 17 31 n -
    (0, 1704108173.201341, '8c4ca98c3900041bab449acfbe08', (-6.26297446, 53.43104088)),  # 4ca98c 17 07 s 1
    (0, 1704108173.808476, '8c4ca98cf9002202804a30209afd',       (NO_COORD, NO_COORD)),  # 4ca98c 17 31 n -
    (0, 1704108176.698019, '8c4ca98c3900041baf4495074f44', (-6.26307544, 53.43106415)),  # 4ca98c 17 07 s 1
    (0, 1704108176.870261, '8c4ca98cf9002202804a30209afd',       (NO_COORD, NO_COORD)),  # 4ca98c 17 31 n -
    (0, 1704108177.135960, '8c4ca98c3900027b9d20f3892355', (-6.26308986, 53.43106842)),  # 4ca98c 17 07 s 0

    (1, 1704108178.124581, '8c4ca98c3900027b9f20f26d7fde', (-6.26310948, 53.43107986)),  # 4ca98c 17 07 s 0
    (1, 1704108178.614104, '8c4ca98cf9002202804a30209afd',       (NO_COORD, NO_COORD)),  # 4ca98c 17 31 n -
)
P_STATE_5 = (
    {
        'icao': [0x4ca98c],
        'time': [1704108177.135960],
        'position': [(-6.26308986, 53.43106842)],
        'valid': [True],
        'carry_over_time': [1704108111.759284],
        'prev_position': [],
    },
    EMPTY_STATE | {'icao': [0x4ca98c], 'time': [1704108178.124581], 'position': [(-6.26310948, 53.43107986)], 'valid': [True]},
)

# test: surface position reasonabless test is performed with airborne
#       position data
# stream: [s]eeo.[a]o...ee
P_MSG_6 = (
    (0, 1704695698.847369, '8c4ca304427a22755f1d7b6bf695',       (NO_COORD, NO_COORD)),  # 4ca304 17 08 s 0
    (0, 1704695699.435441, '8c4ca304427a22755d1d7e8f9228', (-6.28045218, 53.42191315)),  # 4ca304 17 08 s 0
    (0, 1704695700.268926, '8c4ca304428a24158b413f6ca703', (-6.28032236, 53.42191664)),  # 4ca304 17 08 s 1
    (0, 1704695721.396960, '8d4ca304ea11a935151c00ae0974',       (NO_COORD, NO_COORD)),  # 4ca304 17 29 n -
    (0, 1704695721.618800, '8d4ca3046003b70548d0de5aec12', (-6.26883114, 53.42129982)),  # 4ca304 17 12 a 1
    (0, 1704695721.994547, '8d4ca30499087e81b00c1f090e4e',       (NO_COORD, NO_COORD)),  # 4ca304 17 19 n -
    (0, 1704695725.278382,               '5d4ca3046296d5',       (NO_COORD, NO_COORD)),  # 4ca304 11 -- n -
    (0, 1704695725.869060, '8d4ca30499088e81f06c1f28efae',       (NO_COORD, NO_COORD)),  # 4ca304 17 19 n -
    (0, 1704695726.426409, '8d4ca3046003d39d2ec835626a24', (-6.26369803, 53.42097473)),  # 4ca304 17 12 a 0
    (0, 1704695726.593740,               '5d4ca3046296d4',       (NO_COORD, NO_COORD)),  # 4ca304 11 -- n -
    (0, 1704695726.797714, '8d4ca30499089081f0981f6919a5',       (NO_COORD, NO_COORD)),  # 4ca304 17 19 n -
    (0, 1704695727.393335, '8d4ca304f80300060048786b2920',       (NO_COORD, NO_COORD)),  # 4ca304 17 31 n -
    (0, 1704695727.843414, '8d4ca3046003f39d2ac8493688b2', (-6.26212856, 53.42088318)),  # 4ca304 17 12 a 0
)
P_STATE_6 = (
    EMPTY_STATE | {'icao': [0x4ca304], 'time': [1704695727.843414], 'position': [(-6.26212856, 53.42088318)], 'valid': [True]},
)

# TODO: NL change unit test required
POSITION_DATA = [
    (P_MSG_0, P_STATE_0),
    (P_MSG_1, P_STATE_1),
    (P_MSG_2, P_STATE_2),
    (P_MSG_3, P_STATE_3),
    (P_MSG_4, P_STATE_4),
    (P_MSG_5, P_STATE_5),
    (P_MSG_6, P_STATE_6),
]

# vim: sw=4:et:ai
