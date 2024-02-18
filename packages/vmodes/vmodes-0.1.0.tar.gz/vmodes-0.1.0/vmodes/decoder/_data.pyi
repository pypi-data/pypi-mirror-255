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

from .. import types as vmt

class Receiver:
    def __init__(
            self, longitude: float, latitude: float, range: float=666000
    ): ...

class PosDecoderData:
    def __init__(  # noqa: PLR0913
            self,
            time: vmt.Time,
            icao: vmt.Icao,
            is_surface: vmt.BIndex,
            cpr_fmt: vmt.CprFormat,
            cpr_coord: vmt.CprCoordinate,
    ): ...

class PosDecoderCarryData:
    data: vmt.Message
    time: vmt.Time
    icao: vmt.Icao
    typecode: vmt.TypeCode
    is_surface: vmt.BIndex
    cpr_fmt: vmt.CprFormat
    cpr_coord: vmt.CprCoordinate

    size: int

    def __init__(  # noqa: PLR0913
            self,
            data: vmt.Message,
            time: vmt.Time,
            icao: vmt.Icao,
            typecode: vmt.TypeCode,
            is_surface: vmt.BIndex,
            cpr_fmt: vmt.CprFormat,
            cpr_coord: vmt.CprCoordinate,
    ): ...

class PosDecoderCtx:
    receiver: Receiver
    carry_over: PosDecoderCarryData
    last_position: vmt.LastPosition

    def __init__(
            self,
            receiver: Receiver,
            carry_over: PosDecoderCarryData | None=None,
            last_position: vmt.LastPosition | None=None
    ): ...

# vim: sw=4:et:ai
