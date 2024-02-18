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

import cython
import logging
import numpy as np
from cython import Py_ssize_t

cimport numpy as cnp
from cpython.ref cimport PyObject
from libc.stdint cimport uint8_t, uint32_t, uint64_t, int32_t
from libc.math cimport acos, cos, fabs, floor, fmod, sqrt

from ._data cimport PosDecoder, PosDecoderCtx, PosDecoderData, PositionTime, \
    PosDecoderCarryData, Receiver, MessageCheck, Position, t_time, t_bool, \
    t_func_check_message, t_func_position_local, t_func_position_global

logger = logging.getLogger(__name__)

cdef extern from "arpa/inet.h":
    uint32_t ntohl(uint32_t)

# maximum time between even and odd ADS-B position messages
DEF TIME_SURFACE_MSG_PAIR = 50   # [icao9871]_, C.2.6.8
DEF TIME_AIRBORNE_MSG_PAIR = 10  # [icao9871]_, C.2.6.7

# maximum time between last position and ADS-B position message for locally
# unambiguous decoding of position [icao9871]_, C.2.6.10.3
DEF TIME_POS_LOCAL = 30

# specification says "based on reception of a new odd and an even Position
# Message" ([icao9871]_, C.2.6.10.2), but we need to have some time limit when
# looking up next pair;
DEF TIME_NEXT_MESSAGE_PAIR = 30

# use maximum of above specified times for carry over cutoff
DEF TIME_CUTOFF_LAST = TIME_POS_LOCAL
DEF TIME_CUTOFF_SRF = TIME_NEXT_MESSAGE_PAIR + 2 * TIME_SURFACE_MSG_PAIR
DEF TIME_CUTOFF_AIR = TIME_NEXT_MESSAGE_PAIR + 2 * TIME_AIRBORNE_MSG_PAIR

DEF M_PI = 3.14159265358979323846
# cos(M_PI / 30) 0.9945218953682733
DEF NL_A = 1 - 0.9945218953682733  # 30 == 15 * 2 == NZ * 2
DEF PI_DEG = M_PI / 180
DEF PI_2 = M_PI * 2

DEF R_EARTH = 6371000 
DEF GRID_POS_AIRBORNE_VER = (5 / R_EARTH) ** 2
DEF GRID_POS_SURFACE_VER = (1.25 / R_EARTH) ** 2
DEF GRID_LOC_RECV = (666000 / R_EARTH) ** 2

# 2.5 nautical mile, surface participant receiving airborne position
# message
DEF GRID_POS_LOC_AIRBORNE = (2.5 * 1852 / R_EARTH) ** 2
# 0.75 nautical mile, surface participant receiving surface position
# message
DEF GRID_POS_LOC_SURFACE = (0.75 * 1852 / R_EARTH) ** 2

# definitions of decoders for surface and airborne positions decoding; used
# by `pos_decoder` function
cdef PosDecoder[2] POS_DECODER = [
    PosDecoder(
        decode_pos_air_local, decode_pos_air_global,
        TIME_AIRBORNE_MSG_PAIR, GRID_POS_AIRBORNE_VER, GRID_POS_LOC_AIRBORNE,
    ),
    PosDecoder(
        decode_pos_srf_local, decode_pos_srf_global,
        TIME_SURFACE_MSG_PAIR, GRID_POS_SURFACE_VER, GRID_POS_LOC_SURFACE,
    ),
]

#  constants for determining number of longitude zone for given latitude
DEF NL_INVALID = 0
DEF NL_NUM = 59
cdef double[NL_NUM] NL_ARRAY = [  # see [icao9871]_, section C.2.6.2, point (d)
    10.47047129996848013888666173443198204040527343750000,
    14.82817436868679372707902075489982962608337402343750,
    18.18626357071335419846036529634147882461547851562500,
    21.02939492602846272006900107953697443008422851562500,
    23.54504486557070563890192715916782617568969726562500,
    25.82924707058775481982593191787600517272949218750000,
    27.93898710121904471748166542965918779373168945312500,
    29.91135685731808280252153053879737854003906250000000,
    31.77209707681076977792145044077187776565551757812500,
    33.53993436298483743485121522098779678344726562500000,
    35.22899597796384796311031095683574676513671875000000,
    36.85025107593526172422571107745170593261718750000000,
    38.41241892412256220268318429589271545410156250000000,
    39.92256684333861471714044455438852310180664062500000,
    41.38651832260239160632409038953483104705810546875000,
    42.80914012243555077930068364366888999938964843750000,
    44.19454951419274379986745771020650863647460937500000,
    45.54626722660234605655205086804926395416259765625000,
    46.86733252498745372349731042049825191497802734375000,
    48.16039128096621624308681930415332317352294921875000,
    49.42776439255686682372470386326313018798828125000000,
    50.67150165553834995080251246690750122070312500000000,
    51.89342469168768445797468302771449089050292968750000,
    53.09516152796003041203221073374152183532714843750000,
    54.27817472272899834706549881957471370697021484375000,
    55.44378444495043112283383379690349102020263671875000,
    56.59318756205917821944240131415426731109619140625000,
    57.72747353866113684262018068693578243255615234375000,
    58.84763776148457026238247635774314403533935546875000,
    59.95459276694029426835186313837766647338867187500000,
    61.04917774246351314104686025530099868774414062500000,
    62.13216659210328884910268243402242660522460937500000,
    63.20427479381928037582838442176580429077148437500000,
    64.26616522567439915292197838425636291503906250000000,
    65.31845309682088895897322800010442733764648437500000,
    66.36171008382616776088980259373784065246582031250000,
    67.39646774084667413262650370597839355468750000000000,
    68.42322022083330068653594935312867164611816406250000,
    69.44242631144024358036404009908437728881835937500000,
    70.45451074987599326959752943366765975952148437500000,
    71.45986473028982288724364480003714561462402343750000,
    72.45884544728944831604167120531201362609863281250000,
    73.45177441667864570717938477173447608947753906250000,
    74.43893415725136719629517756402492523193359375000000,
    75.42056256653356172137137036770582199096679687500000,
    76.39684390794468527019489556550979614257812500000000,
    77.36789461328187655908550368621945381164550781250000,
    78.33374082922746595158969284966588020324707031250000,
    79.29428225456925360958848614245653152465820312500000,
    80.24923213280511902212310815230011940002441406250000,
    81.19801349271948254227027064189314842224121093750000,
    82.13956980510606342704704729840159416198730468750000,
    83.07199444719813641313521657139062881469726562500000,
    83.99173562980564611279987730085849761962890625000000,
    84.89166190702084691110940184444189071655273437500000,
    85.75541620944417786631674971431493759155273437500000,
    86.53536997512100015228497795760631561279296875000000,
    87.00000000000000000000000000000000000000000000000000,
    90,
]

#
# public API; functions
#

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
def cpr_coordidnates(uint8_t[:, :] data):
    """
    Calculate CPR coordinates.

    :param data: ADS-B messages.
    """
    cdef:
        Py_ssize_t size = len(data)
        Py_ssize_t i
        cnp.ndarray[cnp.double_t, ndim=2] result = np.zeros((size, 2), dtype=np.double)

    for i in range(size):
        result[i, 0] = (unpack_uint32(&data[i, 7]) & 0x0001ffff) / 131072.0
        result[i, 1] = ((unpack_uint32(&data[i, 5]) >> 1) & 0x0001ffff) / 131072.0

    return result

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
def decode_positions(PosDecoderCtx ctx, PosDecoderData data):
    cdef:
        Py_ssize_t i
        t_bool in_past, is_local
        t_time time_delta, cutoff_last, cutoff_srf, cutoff_air, last_time
        Position pos
        PositionTime last

        # index of data to carry over for next position decoding
        cnp.ndarray[t_bool, ndim=1, cast=True] carry_over = np.full(
            data.size, True, dtype=np.bool_
        )
        # index of valid positions in the result array
        cnp.ndarray[t_bool, ndim=1, cast=True] index = np.zeros(
            data.size, dtype=np.bool_
        )
        cnp.ndarray[cnp.double_t, ndim=2] result = np.zeros(
            (data.size, 2), dtype=np.double
        )

    # determine cutoff time for
    #
    # - last position of an aircraft in the position decoder context
    # - data for surface positions
    # - data for airborne positions
    #
    #  an item older than a cutoff is no longer necessary, and is not
    #  carried over
    if data.size > 0:
        last_time = data.time[data.size - 1]
        cutoff_last = last_time - TIME_CUTOFF_LAST
        cutoff_srf = last_time - TIME_CUTOFF_SRF
        cutoff_air = last_time - TIME_CUTOFF_AIR
    else:
        cutoff_last = 0
        cutoff_srf = 0
        cutoff_air = 0

    for i in range(data.size):
        last = ctx.get(data.icao[i], data.time[i])
        time_delta = data.time[i] - last.time
        in_past = last.position.is_valid and time_delta <= 0

        # do not carry over data
        # - for which position is not to be determined
        # - which is no longer necessary
        carry_over[i] = not (
            in_past
            or data.is_surface[i] and data.time[i] < cutoff_srf
            or not data.is_surface[i] and data.time[i] < cutoff_air
        )

        # there is last valid position in the future; we are going over
        # carried over data, so let's skip
        if in_past:
            continue

        pos, is_local = find_position_any(ctx, <PyObject*> data, i, last, time_delta)

        # only locally determined positions are in the result; globally
        # determined positions are used only as most recent valid positions
        if is_local and pos.is_valid:
            index[i] = True
            result[i, 0] = pos.longitude
            result[i, 1] = pos.latitude

        # both globally and locally determined positions can become most
        # recent position
        if pos.is_valid:
            last.time = data.time[i]
            last.position = pos

        # do not carry over data for positions
        # - both valid and invalid locally determined
        # - valid globally determined (data for invalid position can still
        #   be used in next decoding of a position)
        #
        # NOTE: carry_over might be false, then keep it false
        carry_over[i] = carry_over[i] and not (is_local or pos.is_valid)

        if __debug__:
            logger.debug('carry over: i={}, time={}, carry_over={}'.format(
                i, data.time[i], carry_over[i]
            ))

    return index, result, ctx.prune(cutoff_last), carry_over

#
# decode position locally and globally 
#

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef inline Position decode_pos_air_global(
        Position location, PyObject* data, Py_ssize_t i, Py_ssize_t j
) noexcept:
    # NOTE: `location` argument is ignored; it is needed to match
    #       `decode_pos_srf_global` signature
    cdef:
        PosDecoderData pd = <PosDecoderData> data

    return position_air_global(
        pd.cpr_coord[i, 0], pd.cpr_coord[i, 1],
        pd.cpr_coord[j, 0], pd.cpr_coord[j, 1],
        pd.cpr_fmt[j],
    )

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef inline Position decode_pos_srf_global(
        Position location, PyObject* data, Py_ssize_t i, Py_ssize_t j
) noexcept:
    cdef:
        PosDecoderData pd = <PosDecoderData> data

    return position_srf_global(
        location.longitude, location.latitude,
        pd.cpr_coord[i, 0], pd.cpr_coord[i, 1],
        pd.cpr_coord[j, 0], pd.cpr_coord[j, 1],
        pd.cpr_fmt[j],
    )

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef inline Position decode_pos_air_local(
        Position location, PyObject* data, Py_ssize_t i
) noexcept:
    cdef:
        PosDecoderData pd = <PosDecoderData> data

    return position_air_local(
        location.longitude, location.latitude,
        pd.cpr_coord[i, 0], pd.cpr_coord[i, 1],
        pd.cpr_fmt[i],
    )

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef inline Position decode_pos_srf_local(
        Position location, PyObject* data, Py_ssize_t i
) noexcept:
    cdef:
        PosDecoderData pd = <PosDecoderData> data

    return position_srf_local(
        location.longitude, location.latitude,
        pd.cpr_coord[i, 0], pd.cpr_coord[i, 1],
        pd.cpr_fmt[i],
    )

cpdef inline Position position_air_local(
        double ref_lon,
        double ref_lat,
        double cpr_lon,
        double cpr_lat,
        uint8_t is_odd,
) noexcept:
    return position_any_local(ref_lon, ref_lat, cpr_lon, cpr_lat, is_odd, 360)

cpdef inline Position position_srf_local(
        double ref_lon,
        double ref_lat,
        double cpr_lon,
        double cpr_lat,
        uint8_t is_odd,
) noexcept:
    return position_any_local(ref_lon, ref_lat, cpr_lon, cpr_lat, is_odd, 90)

@cython.cdivision(True)
cpdef inline Position position_air_global(
        double cpr_lon_prev,
        double cpr_lat_prev,
        double cpr_lon_next,
        double cpr_lat_next,
        uint8_t cpr_fmt_next,
) noexcept:
    cdef:
        double cpr_lon_odd, cpr_lon_even, cpr_lat_odd, cpr_lat_even
        uint8_t nl
        double longitude, latitude

        uint8_t is_odd = cpr_fmt_next

    cpr_lon_even, cpr_lat_even, cpr_lon_odd, cpr_lat_odd = coord_swap(
        is_odd,
        cpr_lon_prev, cpr_lat_prev,
        cpr_lon_next, cpr_lat_next,
    )

    lat_even, lat_odd = latitude_from_cpr(cpr_lat_even, cpr_lat_odd, 360)
    latitude = lat_odd if is_odd else lat_even

    nl = latitude_nl(lat_even, lat_odd)
    if nl == NL_INVALID:
        return Position(0, 0, False)

    longitude = longitude_from_cpr(cpr_lon_even, cpr_lon_odd, is_odd, nl, 360)
    return Position(longitude, latitude, True)

@cython.cdivision(True)
cpdef inline Position position_srf_global(
        double location_lon,
        double location_lat,
        double cpr_lon_prev,
        double cpr_lat_prev,
        double cpr_lon_next,
        double cpr_lat_next,
        uint8_t cpr_fmt_next,
) noexcept:
    cdef:
        double cpr_lon_odd, cpr_lon_even, cpr_lat_odd, cpr_lat_even
        uint8_t nl
        double longitude, latitude

        uint8_t is_odd = cpr_fmt_next

    cpr_lon_even, cpr_lat_even, cpr_lon_odd, cpr_lat_odd = coord_swap(
        is_odd,
        cpr_lon_prev, cpr_lat_prev,
        cpr_lon_next, cpr_lat_next,
    )

    lat_even, lat_odd = latitude_from_cpr(cpr_lat_even, cpr_lat_odd, 90)
    if location_lat < 0:
        lat_even = lat_even - 90
        lat_odd = lat_odd - 90
    latitude = lat_odd if is_odd else lat_even

    nl = latitude_nl(lat_even, lat_odd)
    if nl == NL_INVALID:
        return Position(0, 0, False)

    longitude = longitude_from_cpr(cpr_lon_even, cpr_lon_odd, is_odd, nl, 90)
    longitude = find_srf_longitude(location_lon, longitude)

    return Position(longitude, latitude, True)

@cython.cdivision(True)
cpdef inline Position position_any_local(
        double longitude,
        double latitude,
        double cpr_lon,
        double cpr_lat,
        uint8_t is_odd,
        double nl_base,
) noexcept:
    cdef:
        double d_lon, d_lat
        double j, m
        uint8_t ni
        double lon, lat

    assert is_odd == 0 or is_odd == 1

    d_lat = nl_base / (60 - is_odd)
    assert d_lat > 0.0

    j = floor(latitude / d_lat) \
        + floor(0.5 + cmod(latitude, d_lat) / d_lat - cpr_lat)
    lat = d_lat * (j + cpr_lat)

    ni = cpr_nl(lat) - is_odd
    d_lon = nl_base / ni if ni > 0 else nl_base
    assert d_lon > 0.0

    m = floor(longitude / d_lon) \
        + floor(0.5 + cmod(longitude, d_lon) / d_lon - cpr_lon)
    lon = d_lon * (m + cpr_lon)

    return Position(lon, lat, True)

#
# finding positions
#

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef inline (Position, t_bool) find_position_any(
        PosDecoderCtx ctx,
        PyObject* data,
        Py_ssize_t i,
        PositionTime last,
        t_time time_delta
):
    """
    Determine position globally or locally.
    """
    cdef:
        t_bool is_local
        PosDecoder p_decoder

        PosDecoderData pd = <PosDecoderData> data

    if __debug__:
        logger.debug('local: i={}, time={:.6f}, icao={:6x}, valid={}, time_delta={:.6f}'.format(
            i, pd.time[i], pd.icao[i], last.position.is_valid, time_delta
        ))
    assert last.position.is_valid and time_delta > 0 or not last.position.is_valid

    is_local = last.position.is_valid and time_delta <= TIME_POS_LOCAL
    if is_local:
        p_decoder = pos_decoder(pd.is_surface[i])
        pos = p_decoder.local_pos(last.position, data, i)
        assert pos.is_valid

        # [icao9871]_, section C.2.6.10.3, greater or equal, then fail
        pos.is_valid = grid_distance(pos, last.position) < p_decoder.max_dist_pos_local
        if __debug__ and not pos.is_valid:
            logger.debug('local, distance invalid: i={}'.format(i))

        # if distance test failed, then just invalidate decoded position;
        # keep the *last position* for next position decoding
    else:
        pos = find_position_global(i, <PyObject*> ctx.receiver, data)
        if __debug__:
            logger.debug('global: i={}, time={:.6f}, icao={:6x}, odd={}, valid={}, ({:.8f}, {:.8f})'.format(
                i, pd.time[i], pd.icao[i], pd.cpr_fmt[i],
                pos.is_valid, pos.longitude, pos.latitude
            ))

    return pos, is_local

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef Position find_position_global(
        Py_ssize_t start,
        PyObject *receiver,
        PyObject *data,
):
    """
    Determine position globally.
    """
    cdef:
        Py_ssize_t i_ref_2, i_ver_1, i_ver_2
        Position s_pos, v_pos, l_pos
        PosDecoder s_pos_dec, v_pos_dec

        Py_ssize_t i_ref_1 = start
        Receiver rcv = <Receiver> receiver
        PosDecoderData pd = <PosDecoderData> data

        Position not_found = Position(0, 0, False)

    s_pos_dec = pos_decoder(pd.is_surface[start])
    i_ref_2 = find_message_global(check_next_message, s_pos_dec.max_time, i_ref_1, data)
    if __debug__:
        logger.debug('global: i={}, i-pair={}'.format(i_ref_1, i_ref_2))
    if i_ref_2 == -1:
        return not_found

    i_ver_1 = find_message_global(check_next_pair, TIME_NEXT_MESSAGE_PAIR, i_ref_2, data)
    if __debug__:
        logger.debug('global: i={}, i-pair={}, ver={}'.format(
            i_ref_1, i_ref_2, i_ver_1
        ))
    if i_ver_1 == -1:
        return not_found

    v_pos_dec = pos_decoder(pd.is_surface[i_ver_1])
    i_ver_2 = find_message_global(check_next_message, v_pos_dec.max_time, i_ver_1, data)
    if __debug__:
        logger.debug('global: i={}, i-pair={}, ver={}, ver-pair={}'.format(
            i_ref_1, i_ref_2, i_ver_1, i_ver_2
        ))
    if i_ver_2 == -1:
        return not_found

    assert i_ref_1 < i_ref_2 < i_ver_1 < i_ver_2 < pd.size
    assert pd.is_surface[i_ref_1] == pd.is_surface[i_ref_2]
    assert pd.is_surface[i_ver_1] == pd.is_surface[i_ver_2]
    assert pd.cpr_fmt[i_ref_1] == 1 - pd.cpr_fmt[i_ref_2]
    assert pd.cpr_fmt[i_ver_1] == 1 - pd.cpr_fmt[i_ver_2]
    
    s_pos = s_pos_dec.global_pos(rcv.location, data, i_ref_1, i_ref_2)
    if not s_pos.is_valid or grid_distance(s_pos, rcv.location) > GRID_LOC_RECV:
        if __debug__:
            if s_pos.is_valid:
                logger.debug('start position invalid: i={}'.format(i_ref_1))
            else:
                logger.debug(
                    'start position receiver distance test failed: i={}'
                    .format(i_ref_1)
                )
        return not_found

    v_pos = v_pos_dec.global_pos(rcv.location, data, i_ver_1, i_ver_2)
    if not v_pos.is_valid:
        if __debug__:
            logger.debug('ver position invalid: i={}'.format(i_ref_1))
        return not_found

    l_pos = v_pos_dec.local_pos(s_pos, data, i_ver_2)
    assert l_pos.is_valid
    if grid_distance(v_pos, l_pos) > v_pos_dec.max_dist_pos_ver:
        if __debug__:
            logger.debug('ver position distance test failed: i={}'.format(i_ref_1))
        return not_found

    assert s_pos.is_valid
    return s_pos

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef inline Py_ssize_t find_message_global(
        t_func_check_message check_f,
        t_time max_time,
        Py_ssize_t i,
        PyObject *data
) noexcept:
    cdef:
        Py_ssize_t j
        MessageCheck msg_check

        PosDecoderData pd = <PosDecoderData> data
        Py_ssize_t result = -1

    for j in range(i + 1, (<PosDecoderData> data).size):
        msg_check = check_f(max_time, i, j, data)
        if msg_check == MessageCheck.FOUND:
            result = j
            break
        elif msg_check == MessageCheck.NO_DATA:
            break

        assert msg_check == MessageCheck.NOT_FOUND

    return result

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef MessageCheck check_next_message(
        t_time max_time,
        Py_ssize_t i,
        Py_ssize_t j,
        PyObject *data,
) noexcept:
    cdef:
        PosDecoderData pd = <PosDecoderData> data
        t_bool valid_time = pd.time[j] - pd.time[i] <= max_time 

        MessageCheck result

    if not valid_time:
        result = MessageCheck.NO_DATA
    elif pd.icao[i] == pd.icao[j] and pd.is_surface[i] == pd.is_surface[j] and pd.cpr_fmt[i] == 1 - pd.cpr_fmt[j]:
        result = MessageCheck.FOUND
    else:
        result = MessageCheck.NOT_FOUND

    return result

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef MessageCheck check_next_pair(
        t_time max_time,
        Py_ssize_t i,
        Py_ssize_t j,
        PyObject *data,
) noexcept:
    cdef:
        PosDecoderData pd = <PosDecoderData> data
        t_bool valid_time = pd.time[j] - pd.time[i] <= max_time 

        MessageCheck result

    if not valid_time:
        result = MessageCheck.NO_DATA
    elif pd.icao[i] == pd.icao[j]:
        result = MessageCheck.FOUND
    else:
        result = MessageCheck.NOT_FOUND

    return result

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef inline PosDecoder pos_decoder(t_bool is_surface) noexcept:
    """
    Get position decoder structure

    .. seealso:: PosDecoder
    """
    assert 0 <= is_surface <= 1
    return POS_DECODER[is_surface]

#
# coordinate decoding
#

@cython.cdivision(True)
cdef inline double longitude_from_cpr(
        double cpr_lon_even,
        double cpr_lon_odd,
        uint32_t is_odd,
        int32_t nl,
        double nl_base,
) noexcept:
    cdef:
        double m, cpr_base, longitude
        int32_t ni

    # for longitude decoding, a later message is a significant one
    #
    # is_odd -> t0 < t1 -> even message is significant:
    # - cpr_base = cpr_lon_even
    # - cpr_ni = max(nl, 1) = max(nl - is_odd, 1)
    #
    # not is_odd -> t0 > t1 -> odd message is significant:
    # - crp_base = cpr_lon_odd
    # - cpr_ni = max(nl, 1) = max(nl - is_odd, 1)
    cpr_base = cpr_lon_odd if is_odd else cpr_lon_even
    ni = max(nl - is_odd, 1)

    m = floor(cpr_lon_even * (nl - 1) - cpr_lon_odd * nl + 0.5)
    longitude = (nl_base / ni) * (cmod(m, ni) + cpr_base)

    return adjust_value(longitude, 180, 360)

cdef inline (double, double) latitude_from_cpr(
        double cpr_lat_even,
        double cpr_lat_odd,
        double d_lat_base,
) noexcept:
    cdef:
        double j, air_d_lat_even, air_d_lat_odd
        double lat_even, lat_odd

    j = floor(59 * cpr_lat_even - 60 * cpr_lat_odd + 0.5)

    air_d_lat_even = d_lat_base / 60
    air_d_lat_odd = d_lat_base / 59

    lat_even = air_d_lat_even * (cmod(j, 60) + cpr_lat_even)
    lat_odd = air_d_lat_odd * (cmod(j, 59) + cpr_lat_odd)

    lat_even = adjust_value(lat_even, 270, 360)
    lat_odd = adjust_value(lat_odd, 270, 360)
    return lat_even, lat_odd

cdef inline double find_srf_longitude(double location_lon, double longitude) noexcept:
    """
    Find solution for longitude of surface position.

    There are four possible solutions. find the closest one to the
    longitude of emitter location `location_lon`.

    See [icao9871]_, section C.2.6.8.
    """
    cdef:
        double c_lon, c_lon_dist, lon_dist
        uint32_t k

        double result = longitude

    assert -180 <= longitude <= 180

    lon_dist = fabs(result - location_lon)
    for k in range(90, 271, 90):  # 90, 180, 270
        c_lon = cmod(longitude + k + 180, 360) - 180
        c_lon_dist = fabs(c_lon - location_lon)
        if c_lon_dist < lon_dist:
            result = c_lon

    assert -180 <= result <= 180
    return result

cdef inline uint8_t latitude_nl(double lat_even, double lat_odd) noexcept:
    """
    Calculate and check longitude zone number NL.

    Return 0 (invalid longitude zone number) if NL differs for both
    latitude values.
    """
    cdef:
        uint8_t nl_even, nl_odd

    nl_even = cpr_nl(lat_even)
    nl_odd = cpr_nl(lat_odd)
    if nl_even == nl_odd:
        return nl_even
    else:
        return NL_INVALID

@cython.cdivision(True)
cpdef inline uint8_t cpr_nl(double latitude) noexcept:
    """
    Calculate number of longitude zone for given latitude.

    :param latitude: Input latitude.
    """
    cdef:
        double abs_lat
        uint8_t nl

    abs_lat = fabs(latitude)
    if abs_lat > 90:
        abs_lat = cmod(abs_lat, 90)

    assert 0 <= abs_lat <= 90
    nl = NL_NUM - bisect_left(NL_ARRAY, abs_lat, NL_NUM)

    assert 1 <= nl <= NL_NUM  # [icao9871]_, section C.2.6.2, point (d)
    return nl

cdef inline (double, double, double, double) coord_swap(
        uint8_t is_odd,
        double lon1,
        double lat1,
        double lon2,
        double lat2,
) noexcept:
    if not is_odd:
        lon1, lon2 = lon2, lon1
        lat1, lat2 = lat2, lat1
    return lon1, lat1, lon2, lat2

#
# math and distance functions
#

cpdef double pos_distance(Position p1, Position p2) noexcept:
    """
    Calculate distance between two WGS84 positions using equirectangular
    projection.

    See also https://en.wikipedia.org/wiki/Equirectangular_projection.

    :param p1: First position.
    :param p2: Second position.
    """
    return R_EARTH * sqrt(grid_distance(p1, p2))

cdef inline double grid_distance(Position p1, Position p2) noexcept:
    cdef:
        double rx1 = radians(p1.longitude)
        double ry1 = radians(p1.latitude)
        double rx2 = radians(p2.longitude)
        double ry2 = radians(p2.latitude)

        double dx, dy

    dx = (rx2 - rx1) * cos((rx1 + rx2) / 2)
    dy = ry2 - ry1
    return dx ** 2 + dy ** 2

@cython.cdivision(True)
cdef inline double cmod(double x, double y) noexcept:
    """
    Get reminder of `x / y` division as defined by ICAO.

    For modulus function defined by ICAO, see [icao9871]_, section 2.6.2.

    .. note::

       For negative `x`, the function is different than `fmod` C function
       or Python's `math.fmod` function, and is similar to the modulo
       operator in the Python language.

    """
    assert y > 0.0
    return x - y * floor(x / y)

cdef inline double radians(double degree) noexcept:
    return degree * PI_DEG

cdef inline double adjust_value(
        double value,
        int32_t limit,
        int32_t correction,
) noexcept:
    return value - correction if value >= limit else value

#
# other utilities
#

cdef uint8_t bisect_left(double[] arr, double val, Py_ssize_t size) noexcept:
    # NOTE: based on function bisect_left from Python's bisect module
    cdef:
        uint8_t mid

        uint8_t lo = 0
        uint8_t hi = size

    assert hi < 127

    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < val:
            lo = mid + 1
        else:
            hi = mid
    return lo

cdef inline uint32_t unpack_uint32(const uint8_t* data) noexcept:
    return ntohl((<uint32_t*> data)[0])

# vim: sw=4:et:ai
