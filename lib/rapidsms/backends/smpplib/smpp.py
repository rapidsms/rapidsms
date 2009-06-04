#
# smpplib -- SMPP Library for Python
# Copyright (c) 2005 Martynas Jocius <mjoc@akl.lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# Modified by Yusuf Kaka <yusufk at gmail>
# Added support for Optional TLV's

"""SMPP module"""

import pdu


smpp_instance = None


def make_pdu(command_name, **args):
    """Return PDU instance"""

    f = pdu.factory(command_name, **(args))

    return f


def parse_pdu(data):
    """Parse binary PDU"""

    command = pdu.PDU.extract_command(data)

    if command is None:
        return None

    new_pdu = make_pdu(command)
    new_pdu.parse(data)

    return new_pdu


def next_seq():
    """Return next sequence number"""

    pdu.sequence += 1

    return pdu.sequence


def get_instance():
    """Return SMPP class instance. Singleton design pattern -- let only one
    instance exist"""

    global smpp_instance

    if smpp_instance is None:
        smpp_instance = SMPP()

    return smpp_instance


#
# Exceptions
#

class UnknownCommandError(Exception):
    """Raised when unknown command ID is received"""

