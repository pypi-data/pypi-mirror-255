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

import logging
import numpy as np
import numpy.testing as npt
import operator as op
import typing as tp
from collections.abc import Sequence
from itertools import groupby

import vmodes
from .. import types as vmt
from ..decoder import _position as vmpc, position as vmp
from ..util import data_index

import pytest
from .conftest import to_bin_msg, to_ts_msg
from .data import POSITION_DATA

logger = logging.getLogger(__name__)

T = tp.TypeVar('T')

Position: tp.TypeAlias = tuple[float, float]
MatchFunction: tp.TypeAlias = tp.Callable[
    [float, vmt.Time, vmt.Icao, vmt.CprFormat],
    vmt.UInt8,
]

RECEIVER = -6.27, 53.421389

POSITION_AIRBORNE_GLOBAL = (
    (
        # odd and even messages
        '8d4ca4ed5861a6af48fc38424c44',
        '8d4ca4ed5861a345e0f4bf8d3262',
        (-5.21980285, 52.90942382),
    ),
    (
        # even and odd messages
        '8d4ca4ed5861934616f4a174496e',
        '8d4ca4ed586186afaefc022b21cb',
        (-5.22305733, 52.91122695),
    ),
)

POSITION_AIRBORNE_LOCAL = (
    # even message
    ('8d4ca4ed5861934616f4a174496e', (-5.22209167, 52.91065979),),
    # odd message
    ('8d4ca4ed5861a6af48fc38424c44', (-5.21881975, 52.90885278)),
)

POSITION_SURFACE_GLOBAL = (
    # even and odd message
    (
        '8c4ca98c38f0027bbd20f13f50e5',
        '8c4ca98c38f0041bd34497bf73ba',
        (-6.26303504, 53.43127363),
    ),
    # odd and even message
    (
        '8c4ca98c3810041bc544b1cd83ac',
        '8c4ca98c3920027ba12107e70fc7',
        (-6.26269749, 53.43109130),
    ),
)

POSITION_SURFACE_LOCAL = (
    # even message
    ('8c4ca98c3900027b9d20f3892355', (-6.26308986, 53.43106842)),
    # odd message
    ('8c4ca98c3910041bad449fb14ad9', (-6.26287348, 53.43105251)),
)

CPR_NL_DATA = (
    (0.0, 59),
    (10.0, 59),
    (10.4704712999684801388866617344319820404052734375, 59),
    (11.0, 58),
    (50.0, 38),
    (86.53536997512100015228497795760631561279296875000000, 3),
    (86.535369976, 2),
    (87.0, 2),
    (87.1, 1),
    (89.9, 1),
    (90.0, 1),
)

pos_coord = op.itemgetter('longitude', 'latitude')
first = op.itemgetter(0)

@pytest.mark.parametrize('msg, expected', POSITION_AIRBORNE_LOCAL)
def test_position_air_local(msg: str, expected: Position) -> None:
    """
    Test locally determined airborne position.
    """
    messages = to_bin_msg([msg])
    cpr_fmt = vmodes.cpr_format_type(messages)
    cpr_coord = vmp.cpr_coordidnates(messages)

    pos = vmpc.position_air_local(*RECEIVER, *cpr_coord[0], cpr_fmt[0])  # type: ignore[call-arg]
    assert pos_coord(pos) == pytest.approx(expected)
    assert pos['is_valid']

@pytest.mark.parametrize('msg1, msg2, expected', POSITION_AIRBORNE_GLOBAL)
def test_position_air_global(msg1: str, msg2: str, expected: Position) -> None:
    """
    Test globally determined airborne position.
    """
    messages = to_bin_msg([msg1, msg2])
    cpr_fmt = vmodes.cpr_format_type(messages)
    cpr_coord = vmp.cpr_coordidnates(messages)
    pos = vmpc.position_air_global(*cpr_coord[0], *cpr_coord[1], cpr_fmt[1])  # type: ignore[call-arg]
    assert pos_coord(pos) == pytest.approx(expected)
    assert pos['is_valid']

@pytest.mark.parametrize('msg, expected', POSITION_SURFACE_LOCAL)
def test_position_srf_local(msg: str, expected: Position) -> None:
    """
    Test locally determined surface position.
    """
    messages = to_bin_msg([msg])
    cpr_fmt = vmodes.cpr_format_type(messages)
    cpr_coord = vmp.cpr_coordidnates(messages)

    pos = vmpc.position_srf_local(*RECEIVER, *cpr_coord[0], cpr_fmt[0])  # type: ignore[call-arg]
    assert pos_coord(pos) == pytest.approx(expected)
    assert pos['is_valid']

@pytest.mark.parametrize('msg1, msg2, expected', POSITION_SURFACE_GLOBAL)
def test_position_srf_global(msg1: str, msg2: str, expected: Position) -> None:
    """
    Test globally determined surface position.
    """
    messages = to_bin_msg([msg1, msg2])
    cpr_fmt = vmodes.cpr_format_type(messages)
    cpr_coord = vmp.cpr_coordidnates(messages)
    pos = vmpc.position_srf_global(
        *RECEIVER, *cpr_coord[0], *cpr_coord[1], cpr_fmt[1]  # type: ignore[call-arg]
    )
    assert pos_coord(pos) == pytest.approx(expected)
    assert pos['is_valid']

def test_cpr_format_type(message: vmt.Message) -> None:
    """
    Test determining CPR format type.
    """
    result = vmp.cpr_format_type(message)

    expected = [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1]
    npt.assert_array_equal(expected, result)

def test_nuc_p(message: vmt.Message, tc_message: vmt.TypeCode) -> None:
    """
    Test decoding of navigational accuracy category for position.
    """
    result = vmp.nuc_p(message, tc_message)
    expected = np.ma.array([
        [np.ma.masked] * 3,
        [np.ma.masked] * 3,
        [np.ma.masked] * 3,
        [np.ma.masked] * 3,
        [np.ma.masked] * 3,
        [7.5, 3, 4],
        [25, 10, 15],
        [185, 93, np.nan],
        [370, 185, np.nan],
        [7.5, 3, 4],
        [185.0, 93, np.nan],
        [np.nan, np.nan, np.nan],
        [7.5, 3, 4],
        [7.5, 3, 4],
    ])  # type: ignore
    npt.assert_array_equal(expected, result)

def test_cpr_coordinates(message_cpr: vmt.Message) -> None:
    """
    Test decoding of CPR coordinates.
    """
    expected = [
        [0.37216186, 0.8770980],
        [0.37313079, 0.8774871],
        [0.37545776, 0.8784103],
        [0.37719726, 0.8791046],
        [0.37735748, 0.8791656],
        [0.38890838, 0.7286682],
        [0.38948059, 0.7289047],
        [0.39026641, 0.7292175],
        [0.39120483, 0.7295989],
        [0.39273071, 0.7302093],
    ]

    result = vmp.cpr_coordidnates(message_cpr)
    npt.assert_almost_equal(expected, result)

def test_pos_distance() -> None:
    """
    Test calculating distance using equirectangular projection.
    """
    p1 = _to_cpos(-5.17, 53.0)
    p2 = _to_cpos(-5.18, 53.2)
    result = vmpc.pos_distance(p1, p2)
    npt.assert_array_almost_equal(result, 22266.540827)

@pytest.mark.parametrize('latitude, expected', CPR_NL_DATA)
def test_cpr_nl(latitude: float, expected: int) -> None:
    """
    Test decoding latitude zone.
    """
    nl = vmpc.cpr_nl(latitude)
    assert nl == expected

@pytest.mark.parametrize('st_data, expected_state', POSITION_DATA)
def test_position(
        st_data: Sequence[tuple[int, float, str, tuple[float, float]]],
        expected_state: dict[str, list[tp.Any]],
) -> None:
    """
    Test decoding of position data.
    """
    # test precondition
    assert len({k for k, *_ in st_data}) == len(expected_state)

    receiver = vmodes.Receiver(*RECEIVER)
    ctx = vmodes.PosDecoderCtx(receiver)

    # process each chunk of test data stream
    for k, (_, chunk) in enumerate(groupby(st_data, key=first)):
        data = list(chunk)
        size = len(data)

        # extract position decoding input, and expected result
        # from the test data
        ts, messages = to_ts_msg(data, start=1)
        expected = [(t, p) for _, t, _, p in data if not np.isnan(p[0])]
        t_expected = [t for t, _ in expected]
        p_expected = np.array([p for t, p in expected]).reshape((-1, 2))
        p_prev_expected = np.array(expected_state[k]['prev_position']).reshape((-1, 2))  # type: ignore

        # decode positions data
        icao = vmodes.icao(messages)
        tc = vmodes.typecode(messages)
        pos_data = vmodes.position(ctx, messages, ts, icao, tc)

        # use the new state when decoding next chunk of test data
        ctx = pos_data.ctx

        # determine valid positions from the result of decoding
        assert pos_data.position.shape == (size, 2)
        pos = pos_data.position.compressed().reshape(-1, 2)
        idx = data_index(pos_data.position)

        # let's log some debug data
        msg_num = np.arange(size)[idx]
        items = zip(msg_num, ts[idx], icao[idx], tc[idx], pos[:, 0], pos[:, 1])
        debug_data = '\n'.join(
            '{:03d} {:.6f} {:06x} {:2d} {:10.8f} {:10.8f}'.format(*v)
            for v in items
        )
        logger.warning('position debug data ({}):\n{}'.format(k, debug_data))

        # verify position data and state data
        npt.assert_array_almost_equal(ts[idx], t_expected)
        npt.assert_array_almost_equal(pos, p_expected)

        last_t_pos = list(ctx.last_position.values())
        result_icao = list(ctx.last_position.keys())
        result_time = [p.time for p in last_t_pos]
        result_pos = [pos_coord(p.position) for p in last_t_pos]
        result_valid = [p.position['is_valid'] for p in last_t_pos]
        prev_pos = pos_data.prev_position[data_index(pos_data.prev_position)]

        npt.assert_array_equal(result_icao, expected_state[k]['icao'])  # type: ignore
        npt.assert_array_equal(result_time, expected_state[k]['time'])  # type: ignore
        npt.assert_array_almost_equal(result_pos, expected_state[k]['position'])  # type: ignore
        npt.assert_array_equal(result_valid, expected_state[k]['valid'])  # type: ignore
        npt.assert_array_equal(ctx.carry_over.time, expected_state[k]['carry_over_time'])  # type: ignore
        # verify position result for carried over data
        npt.assert_array_almost_equal(prev_pos, p_prev_expected)

        # lookup last position information using in decoded data; last
        # position for an icao address should exist in the expected
        # decoding state
        result_items = _agg_last(zip(icao[idx], ts[idx], list(pos)))  # type: ignore
        result_last = {
            i: (t, pytest.approx(tuple(p))) for i, t, p in result_items
        }
        expected_items = zip(
            expected_state[k]['icao'],  # type: ignore
            expected_state[k]['time'],  # type: ignore
            expected_state[k]['position'],  # type: ignore
            expected_state[k]['valid'],  # type: ignore
        )
        expected_last = {i: (t, p) for i, t, p, v in expected_items if v}
        assert result_last == expected_last

def _agg_last(items: list[T]) -> list[T]:
    items = sorted(items, key=first)  # type: ignore
    items = groupby(items, key=first)  # type: ignore
    return [v[-1] if (v := list(g)) else [] for k, g in items]  # type: ignore

def _to_cpos(longitude: float, latitude: float) -> vmt.CPosition:
    return {'longitude': longitude, 'latitude': latitude, 'is_valid': True}

# vim: sw=4:et:ai
