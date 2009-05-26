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
# Modified by Yusuf Kaka <yusufk at gmail>
# Added support for Optional TLV's


"""SMPP Commands module"""

import struct
import binascii

import smpp
import pdu
from ptypes import ostr, flag


#
# TON (Type Of Number) values
#
SMPP_TON_UNK = 0x00
SMPP_TON_INTL = 0x01
SMPP_TON_NATNL = 0x02
SMPP_TON_NWSPEC = 0x03
SMPP_TON_SBSCR = 0x04
SMPP_TON_ALNUM = 0x05
SMPP_TON_ABBREV = 0x06


#
# NPI (Numbering Plan Indicator) values
#
SMPP_NPI_UNK = 0x00  # Unknown
SMPP_NPI_ISDN = 0x01  # ISDN (E163/E164)
SMPP_NPI_DATA = 0x03  # Data (X.121)
SMPP_NPI_TELEX = 0x04  # Telex (F.69)
SMPP_NPI_LNDMBL = 0x06  # Land Mobile (E.212)
SMPP_NPI_NATNL = 0x08  # National
SMPP_NPI_PRVT = 0x09  # Private
SMPP_NPI_ERMES = 0x0A  # ERMES
SMPP_NPI_IP = 0x0E  # IPv4
SMPP_NPI_WAP = 0x12  # WAP


#
# Encoding Types
#
SMPP_ENCODING_DEFAULT = 0x00  # SMSC Default
SMPP_ENCODING_IA5 = 0x01  # IA5 (CCITT T.50)/ASCII (ANSI X3.4)
SMPP_ENCODING_BINARY = 0x02  # Octet unspecified (8-bit binary)
SMPP_ENCODING_ISO88591 = 0x03  # Latin 1 (ISO-8859-1)
SMPP_ENCODING_BINARY2 = 0x04  # Octet unspecified (8-bit binary)
SMPP_ENCODING_JIS = 0x05  # JIS (X 0208-1990)
SMPP_ENCODING_ISO88595 = 0x06  # Cyrillic (ISO-8859-5)
SMPP_ENCODING_ISO88598 = 0x07  # Latin/Hebrew (ISO-8859-8)
SMPP_ENCODING_ISO10646 = 0x08  # UCS2 (ISO/IEC-10646)
SMPP_ENCODING_PICTOGRAM = 0x09  # Pictogram Encoding
SMPP_ENCODING_ISO2022JP = 0x0A  # ISO-2022-JP (Music Codes)
SMPP_ENCODING_EXTJIS = 0x0D  # Extended Kanji JIS (X 0212-1990)
SMPP_ENCODING_KSC5601 = 0x0E  # KS C 5601


#
# Language Types
#
SMPP_LANG_DEFAULT = 0x00
SMPP_LANG_EN = 0x01
SMPP_LANG_FR = 0x02
SMPP_LANG_ES = 0x03
SMPP_LANG_DE = 0x04


#
# ESM class values
#
SMPP_MSGMODE_DEFAULT = 0x00  # Default SMSC mode (e.g. Store and Forward)
SMPP_MSGMODE_DATAGRAM = 0x01  # Datagram mode
SMPP_MSGMODE_FORWARD = 0x02  # Forward (i.e. Transaction) mode
SMPP_MSGMODE_STOREFORWARD = 0x03  # Store and Forward mode (use this to
                                  # select Store and Forward mode if Default
                                  # mode is not Store and Forward)


SMPP_MSGTYPE_DEFAULT = 0x00  # Default message type (i.e. normal message)
SMPP_MSGTYPE_DELIVERYACK = 0x08  # Message containts ESME Delivery
                                 # Acknowledgement
SMPP_MSGTYPE_USERACK = 0x10  # Message containts ESME Manual/User
                             # Acknowledgement

SMPP_GSMFEAT_NONE = 0x00  # No specific features selected
SMPP_GSMFEAT_UDHI = 0x40  # UDHI Indicator (only relevant for MT msgs)
SMPP_GSMFEAT_REPLYPATH = 0x80  # Set Reply Path (only relevant for GSM net)
SMPP_GSMFEAT_UDHIREPLYPATH = 0xC0  # Set UDHI and Reply Path (for GSM net)

#
# SMPP Protocol ID
#
SMPP_PID_DEFAULT = 0x00 #Default
SMPP_PID_RIP= 0x41    #Replace if present on handset

#
# SMPP protocol versions
#
SMPP_VERSION_33 = 0x33
SMPP_VERSION_34 = 0x34


#
# SMPP commands map (human-readable -> numeric)
#
commands = {
    'generic_nack': 0x80000000,
    'bind_receiver': 0x00000001,
    'bind_receiver_resp': 0x80000001,
    'bind_transmitter': 0x00000002,
    'bind_transmitter_resp': 0x80000002,
    'query_sm': 0x00000003,
    'query_sm_resp': 0x80000003,
    'submit_sm': 0x00000004,
    'submit_sm_resp': 0x80000004,
    'deliver_sm': 0x00000005,
    'deliver_sm_resp': 0x80000005,
    'unbind': 0x00000006,
    'unbind_resp': 0x80000006,
    'replace_sm': 0x00000007,
    'replace_sm_resp': 0x80000007,
    'cancel_sm': 0x00000008,
    'cancel_sm_resp': 0x80000008,
    'bind_transceiver': 0x00000009,
    'bind_transceiver_resp': 0x80000009,
    'outbind': 0x0000000B,
    'enquire_link': 0x00000015,
    'enquire_link_resp': 0x80000015,
    'submit_multi': 0x00000021,
    'submit_multi_resp': 0x80000021,
    'alert_notification': 0x00000102,
    'data_sm': 0x00000103,
    'data_sm_resp': 0x80000103
}

#
# Optional parameters map
#
optional_params = {
    'dest_addr_subunit': 0x0005,
    'dest_network_type': 0x0006,
    'dest_bearer_type': 0x0007,
    'dest_telematics_id': 0x0008,
    'source_addr_subunit': 0x000D,
    'source_network_type': 0x000E,
    'source_bearer_type': 0x000F,
    'source_telematics_id': 0x010,
    'qos_time_to_live': 0x0017,
    'payload_type': 0x0019,
    'additional_status_info_text': 0x01D,
    'receipted_message_id': 0x001E,
    'ms_msg_wait_facilities': 0x0030,
    'privacy_indicator': 0x0201,
    'source_subaddress': 0x0202,
    'dest_subaddress': 0x0203,
    'user_message_reference': 0x0204,
    'user_response_code': 0x0205,
    'source_port': 0x020A,
    'destination_port': 0x020B,
    'sar_msg_ref_num': 0x020C,
    'language_indicator': 0x020D,
    'sar_total_segments': 0x020E,
    'sar_segment_seqnum': 0x020F,
    'sc_interface_version': 0x0210,#0x1002,
    'callback_num_pres_ind': 0x0302,
    'callback_num_atag': 0x0303,
    'number_of_messages': 0x0304,
    'callback_num': 0x0381,
    'dpf_result': 0x0420,
    'set_dpf': 0x0421,
    'ms_availability_status': 0x0422,
    'network_error_code': 0x0423,
    'message_payload': 0x0424,
    'delivery_failure_reason': 0x0425,
    'more_messages_to_send': 0x0426,
    'message_state': 0x0427,
    'ussd_service_op': 0x0501,
    'display_time': 0x1201,
    'sms_signal': 0x1203,
    'ms_validity': 0x1204,
    'alert_on_message_delivery': 0x130C,
    'its_reply_type': 0x1380,
    'its_session_info': 0x1383
}


def get_command_name(code):
    """Return command name by given code. If code is unknown, raise
    UnkownCommandError exception"""

    try:
        return commands.keys()[commands.values().index(code)]
    except ValueError:
        raise smpp.UnknownCommandError("Unknown SMPP command code " \
                                       "'0x%x'" % code)


def get_command_code(name):
    """Return command code by given command name. If name is unknown,
    raise UnknownCommandError exception"""

    try:
        return commands[name]
    except KeyError:
        raise smpp.UnknownCommandError("Unknown SMPP command name '%s'" \
            % name)

def get_optional_name(code):
    """Return optional_params name by given code. If code is unknown, raise
    UnkownCommandError exception"""

    try:
        return optional_params.keys()[optional_params.values().index(code)]
    except ValueError:
        raise smpp.UnknownCommandError("Unknown SMPP command code " \
                                       "'0x%x'" % code)


def get_optional_code(name):
    """Return optional_params code by given command name. If name is unknown,
    raise UnknownCommandError exception"""

    try:
        return optional_params[name]
    except KeyError:
        raise smpp.UnknownCommandError("Unknown SMPP command name '%s'" \
            % name)
        
class Command(pdu.PDU):
    """SMPP PDU Command class"""

    params = {}


    def __init__(self, command, **args):
        """Initialize"""

        #pdu.PDU.__init__(self, **(args))

        self.command = command
        if args.get('sequence') is None:
            self.sequence_number = smpp.next_seq()

        self.status = pdu.SMPP_ESME_ROK

        #if self.is_vendor() and self.vdefs:
        #    self.defs = self.defs + self.vdefs

        #self.__dict__.update(**(args))
        self._set_vars(**(args))


    def _print_dict(self):

        print '\n'.join([' -> '.join([str(key), str(value)]) for key, value in \
            self.__dict__.items()])


    def _set_vars(self, **args):

        for key, value in args.items():
            if not hasattr(self, key) or getattr(self, key) is None:
                setattr(self, key, value)


    def generate_params(self):
        """Generate binary data from the object"""

        if hasattr(self, 'prep') and callable(self.prep):
            self.prep()

        body = ''

        for field in self.params_order:
            #print field
            param = self.params[field]
            #print param
            if self.field_is_optional(field):
                if param.type is int:
                    value = self._generate_int_tlv(field)
                    if value: body += value
                elif param.type is str:
                    value = self._generate_string_tlv(field)
                    if value: body += value
                elif param.type is ostr:
                    value = self._generate_ostring_tlv(field)
                    if value: body += value
            else:
                if param.type is int:
                    value = self._generate_int(field)
                    body += value
                elif param.type is str:
                    value = self._generate_string(field)
                    body += value
                elif param.type is ostr:
                    value = self._generate_ostring(field)
                    if value: body += value
            #print value
        return body

        
    def _generate_opt_header(self, field):
        """Generate a header for an optional parameter"""

        raise NotImplementedError('Vendors not supported')


    def _generate_int(self, field):
        """Generate integer value"""

        format = self._pack_format(field)
        data = getattr(self, field)
        if data:
            return struct.pack(format, data)
        else:
            return chr(0)  # null terminator
        
    def _generate_string(self, field):
        """Generate string value"""

        field_value = getattr(self, field)

        if hasattr(self.params[field], 'size'):
            size = self.params[field].size
            value = field_value.ljust(size, chr(0))
        elif hasattr(self.params[field], 'max'):
            if len(field_value or '') > self.params[field].max:
                field_value = field_value[0:self.params[field].max-1]

            if field_value:
                value = field_value + chr(0)
            else:
                value = chr(0)

        setattr(self, field, field_value)
        return value


    def _generate_ostring(self, field):
        """Generate octet string value (no null terminator)"""

        value = getattr(self, field)
        if value:
            return value
        else: return None #chr(0)
        
    def _generate_int_tlv(self, field):
        """Generate integer value"""
        format = self._pack_format(field)
        data = getattr(self, field)
        field_code = get_optional_code(field)
        field_length = self.params[field].size
        value = None
        if data:
            value = struct.pack(">HH"+format, field_code,field_length,data)
            #print binascii.b2a_hex(value)
        return value


    def _generate_string_tlv(self, field):
        """Generate string value"""

        field_value = getattr(self, field)
        field_code = get_optional_code(field)
        
        if hasattr(self.params[field], 'size'):
            size = self.params[field].size
            fvalue = field_value.ljust(size, chr(0))
            value = struct.pack(">HH", field_code,size)+fvalue
        elif hasattr(self.params[field], 'max'):
            if len(field_value or '') > self.params[field].max:
                field_value = field_value[0:self.params[field].max-1]

            if field_value:
                field_length = len(field_value)
                fvalue = field_value + chr(0)
                value = struct.pack(">HH", field_code, field_length)+fvalue
                #print binascii.b2a_hex(value)
            else:
                value = None #chr(0)
        #setattr(self, field, field_value)
        return value


    def _generate_ostring_tlv(self, field):
        """Generate octet string value (no null terminator)"""
        try:
            field_value = getattr(self, field)
        except: 
            return None
        field_code = get_optional_code(field)
        
        value = None
        if field_value:
            field_length = len(field_value)
            value = struct.pack(">HH",field_code, field_length) + field_value
            #print binascii.b2a_hex(value)
        return value


    def _pack_format(self, field):
        """Return format type"""

        if self.params[field].size == 1:
            return 'B'
        elif self.params[field].size == 2:
            return 'H'
        elif self.params[field].size == 3:
            return 'L'
        return None


    def _parse_int(self, field, data, pos):
        """Parse fixed-length chunk from a PDU.
        Return (data, pos) tuple."""

        size = self.params[field].size
        field_value = getattr(self, field)
        unpacked_data = self._unpack(self._pack_format(field),
                                     data[pos:pos+size])
        field_value = ''.join(map(str, unpacked_data))
        setattr(self, field, field_value)
        pos += size

        return data, pos


    def _parse_string(self, field, data, pos):
        """Parse variable-length string from a PDU.
        Return (data, pos) tuple."""

        end = data.find(chr(0), pos)
        length = end - pos

        field_value = data[pos:pos+length]
        setattr(self, field, field_value)
        pos += length + 1

        return data, pos


    def _parse_ostring(self, field, data, pos, length=None):
        """Parse an octet string from a PDU.
        Return (data, pos) tuple."""
        
        if length is None:
            length_field = self.params[field].len_field
            length = int(getattr(self, length_field))
            #print length_field, type(length_field), length, type(length_field)

        setattr(self, field, data[pos:pos+length])
        pos += length

        return data, pos


    def is_fixed(self, field):
        """Return True if field has fixed length, False otherwise"""
        
        if hasattr(self.params[field], 'size'):
            return True

        return False
        

    def parse_params(self, data):
        """Parse data into the object structure"""

        pos = 0
        dlen = len(data)

        for field in self.params_order:
            param = self.params[field]
            if pos == dlen or self.field_is_optional(field):
                break

            if param.type is int:
                data, pos = self._parse_int(field, data, pos)
            elif param.type is str:
                data, pos = self._parse_string(field, data, pos)
            elif param.type is ostr:
                data, pos = self._parse_ostring(field, data, pos)
        #print pos,field,data
        if pos < dlen:
            #None
            self.parse_optional_params(data[pos:])


    def parse_optional_params(self, data):
        """Parse optional parameters.
        
        Optional parameters have the following format:
            * type (2 bytes)
            * length (2 bytes)
            * value (variable, <length> bytes)
        """

        #print binascii.b2a_hex(data)
        #print len(data)
        dlen = len(data)#-4
        pos = 0
        
        while pos < dlen:
            #print pos
            #unpacked_data1,unpacked_data2 = struct.unpack('2B', data[pos:pos+2]) 
            #pack = struct.pack(unpacked_data2,unpacked_data1)
            #unpacked_data = struct.unpack('H', pack) 
            unpacked_data = struct.unpack('>H', data[pos:pos+2]) 
            type_code = int(''.join(map(str, unpacked_data)))
            
            #print type_code
            #field=None
            field = get_optional_name(type_code)
            #try:
            #    field = \
            #        optional_params.keys()[\
            #            optional_params.values().index(type_code)]
                
            #except ValueError:
            #    raise ValueError("Type '0x%x' not found" % type_code)
                #print ("Type '0x%x' not found" % type_code)
           

            #if field != None:
            pos += 2

            length = int(''.join(map(str, struct.unpack('!H', data[pos:pos+2]))))
            pos += 2
            param = self.params[field]

            if param.type is int:
                data, pos = self._parse_int(field, data, pos)
            elif param.type is str:
                data, pos = self._parse_string(field, data, pos)
            elif param.type is ostr:
                data, pos = self._parse_ostring(field, data, pos, length)


    def field_exists(self, field):
        """Return True if field exists, False otherwise"""

        return hasattr(self.params, field)


    def field_is_optional(self, field):
        """Return True if field is optional, False otherwise"""

        if field in optional_params:
            return True
        elif self.is_vendor():
            # FIXME: No vendor support yet
            return False

        return False


class Param:
    """Command parameter info class"""

    def __init__(self, **args):
        """Initialize"""

        if not args.has_key('type'):
            raise KeyError('Parameter Type not defined')

        if args.get('type') not in [int, str, ostr, flag]:
            raise ValueError("Invalid parameter type: %s" \
                % args.get('type'))

        valid_keys = ['type', 'size', 'min', 'max', 'len_field']
        for k in args.keys():
            if k not in valid_keys:
                raise KeyError("Key '%s' not allowed here" % k)

        self.type = args.get('type')

        if args.has_key('size'):
            self.size = args.get('size')

        if args.has_key('min'):
            self.min = args.get('min')

        if args.has_key('max'):
            self.max = args.get('max')

        if args.has_key('len_field'):
            self.len_field = args.get('len_field')



class BindTransmitter(Command):
    """Bind as a transmitter command"""

    params = {
        'system_id': Param(type=str, max=16),
        'password': Param(type=str, max=9),
        'system_type': Param(type=str, max=13),
        'interface_version': Param(type=int, size=1),
        'addr_ton': Param(type=int, size=1),
        'addr_npi': Param(type=int, size=1),
        'address_range': Param(type=str, max=41),
    }

    # Order is important, but params dictionary is unordered
    params_order = ('system_id', 'password', 'system_type', 
        'interface_version', 'addr_ton', 'addr_npi', 'address_range')

    
    def __init__(self, command, **args):
        """Initialize"""

        Command.__init__(self, command, **(args))

        #self.__dict__.update({}.fromkeys(self.params.keys()))
        self._set_vars(**({}.fromkeys(self.params.keys())))

        self.interface_version = SMPP_VERSION_34


class BindReceiver(BindTransmitter):
    pass


class BindTransceiver(BindTransmitter):
    pass


class BindTransmitterResp(Command):
    """Response for bind as a transmitter command"""

    params = {
        'system_id': Param(type=str),
        'sc_interface_version': Param(type=int, size=1),
    }

    params_order = ('system_id', 'sc_interface_version')

    def __init__(self, command):
        """Initialize"""

        Command.__init__(self, command)

        self._set_vars(**({}.fromkeys(self.params.keys())))


class BindReceiverResp(BindTransmitterResp):
    pass

    
class BindTransceiverResp(BindTransmitterResp):
    pass


class DataSM(Command):
    """data_sm command is used to transfer data between SMSC and the ESME"""

    params = {
        'service_type': Param(type=str, max=6),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'dest_addr_ton': Param(type=int, size=1),
        'dest_addr_npi': Param(type=int, size=1),
        'destination_addr': Param(type=str, max=21),
        'esm_class': Param(type=int, size=1),
        'registered_delivery': Param(type=int, size=1),
        'data_coding': Param(type=int, size=1),

        # Optional params:
        'source_port': Param(type=int, size=2),
        'source_addr_subunit': Param(type=int, size=1),
        'source_network_type': Param(type=int, size=1),
        'source_bearer_type': Param(type=int, size=1),
        'source_telematics_id': Param(type=int, size=2),
        'destination_port': Param(type=int, size=2),
        'dest_addr_subunit': Param(type=int, size=1),
        'dest_network_type': Param(type=int, size=1),
        'dest_bearer_type': Param(type=int, size=1),
        'dest_telematics_id': Param(type=int, size=2),
        'sar_msg_ref_num': Param(type=int, size=2),
        'sar_total_segments': Param(type=int, size=1),
        'sar_segment_seqnum': Param(type=int, size=1),
        'more_messages_to_send': Param(type=int, size=1),
        'qos_time_to_live': Param(type=int, size=4),
        'payload_type': Param(type=int, size=1),
        'message_payload': Param(type=ostr, max=260),
        'receipted_message_id': Param(type=str, max=65),
        'message_state': Param(type=int, size=1),
        'network_error_code': Param(type=ostr, size=3),
        'user_message_reference': Param(type=int, size=2),
        'privacy_indicator': Param(type=int, size=1),
        'callback_num': Param(type=str, min=4, max=19),
        'callback_num_pres_ind': Param(type=int, size=1),
        'callback_num_atag': Param(type=str, max=65),
        'source_subaddress': Param(type=str, min=2, max=23),
        'dest_subaddress': Param(type=str, min=2, max=23),
        'user_response_code': Param(type=int, size=1),
        'display_time': Param(type=int, size=1),
        'sms_signal': Param(type=int, size=2),
        'ms_validity': Param(type=int, size=1),
        'ms_msg_wait_facilities': Param(type=int, size=1),
        'number_of_messages': Param(type=int, size=1),
        'alert_on_msg_delivery': Param(type=flag),
        'language_indicator': Param(type=int, size=1),
        'its_reply_type': Param(type=int, size=1),
        'its_session_info': Param(type=int, size=2)
    }

    params_order = ('service_type', 'source_addr_ton', 'source_addr_npi',
        'source_addr', 'dest_addr_ton', 'dest_addr_npi', 'destination_addr',
        'esm_class', 'registered_delivery', 'data_coding'
        
        # Optional params:
        'source_port', 'source_addr_subunit', 'source_network_type',
        'source_bearer_type', 'source_telematics_id', 'destination_port',
        'dest_addr_subunit', 'dest_network_type', 'dest_bearer_type',
        'dest_telematics_id', 'sar_msg_ref_num', 'sar_total_segments',
        'sar_segment_seqnum', 'more_messages_to_send', 'qos_time_to_live',
        'payload_type', 'message_payload', 'receipted_message_id',
        'message_state', 'network_error_code', 'user_message_reference',
        'privacy_indicator', 'callback_num', 'callback_num_pres_ind',
        'callback_num_atag', 'source_subaddress', 'dest_subaddress',
        'user_response_code', 'display_time', 'sms_signal',
        'ms_validity', 'ms_msg_wait_facilities', 'number_of_messages',
        'alert_on_message_delivery', 'language_indicator', 'its_reply_type',
        'its_session_info')


    def __init__(self, command):
        """Initialize"""
        
        Command.__init__(self, command)

        self._set_vars(**({}.fromkeys(self.params.keys())))


class DataSMResp(Command):
    """Reponse command for data_sm"""

    message_id = None
    delivery_failure_reason = None
    network_error_code = None
    additional_status_info_text = None
    dpf_result = None


class GenericNAck(Command):
    """General Negative Acknowledgement class"""

    _defs = []


    
class SubmitSM(Command):
    """submit_sm command class
    
    This command is used by an ESME to submit short message to the SMSC.
    submit_sm PDU does not support the transaction mode."""

    #
    # Service type
    # The following generic service types are defined:
    #   '' -- default
    #   'CMT' -- Cellural Messaging
    #   'CPT' -- Cellural Paging
    #   'VMN' -- Voice Mail Notification
    #   'VMA' -- Voice Mail Alerting
    #   'WAP' -- Wireless Application Protocol
    #   'USSD' -- Unstructured Supplementary Services Data
    service_type = None

    #
    # Type of Number for source address
    #
    source_addr_ton = None

    #
    # Numbering Plan Indicator for source address
    #
    source_addr_npi = None

    #
    # Address of SME which originated this message
    #
    source_addr = None

    #
    # TON for destination
    #
    dest_addr_ton = None

    #
    # NPI for destination
    #
    dest_addr_npi = None

    #
    # Destination address for this message
    #
    destination_addr = None

    #
    # Message mode and message type
    #
    esm_class = None#SMPP_MSGMODE_DEFAULT

    #
    # Protocol Identifier
    #
    protocol_id = None

    #
    # Priority level of this message
    #
    priority_flag = None

    #
    # Message is to be scheduled by the SMSC for delivery
    #
    schedule_delivery_time = None

    #
    # Validity period of this message
    #
    validity_period = None

    #
    # Indicator to signify if if an SMSC delivery receipt or and SME
    # acknowledgement is required.
    #
    registered_delivery = None

    #
    # This flag indicates if submitted message should replace an existing
    # message
    #
    replace_if_present_flag = None

    #
    # Encoding scheme of the short messaege data
    #
    data_coding = None #SMPP_ENCODING_DEFAULT#ISO10646

    #
    # Indicates the short message to send from a list of predefined
    # ('canned') short messages stored on the SMSC
    #
    sm_default_msg_id = None

    #
    # Message length in octets
    #
    sm_length = 0

    #
    # Up to 254 octets of short message user data
    #
    short_message = None

    #
    # Optional are taken from params list and are set dynamically when 
    # __init__ is called.
    #

    params = {
        'service_type': Param(type=str, max=6),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'dest_addr_ton': Param(type=int, size=1),
        'dest_addr_npi': Param(type=int, size=1),
        'destination_addr': Param(type=str, max=21),
        'esm_class': Param(type=int, size=1),
        'protocol_id': Param(type=int, size=1),
        'priority_flag': Param(type=int, size=1),
        'schedule_delivery_time': Param(type=str, max=17),
        'validity_period': Param(type=str, max=17),
        'registered_delivery': Param(type=int, size=1),
        'replace_if_present_flag': Param(type=int, size=1),
        'data_coding': Param(type=int, size=1),
        'sm_default_msg_id': Param(type=int, size=1),
        'sm_length': Param(type=int, size=1),
        'short_message': Param(type=ostr, max=254, 
                               len_field='sm_length'),
        # Optional params
        'user_message_reference': Param(type=int, size=2),
        'source_port': Param(type=int, size=2),
        'source_addr_subunit': Param(type=int, size=2),
        'destination_port': Param(type=int, size=2),
        'dest_addr_subunit': Param(type=int, size=1),
        'sar_msg_ref_num': Param(type=int, size=2),
        'sar_total_segments': Param(type=int, size=1),
        'sar_segment_seqnum': Param(type=int, size=1),
        'more_messages_to_send': Param(type=int, size=1),
        'payload_type': Param(type=int, size=1),
        'message_payload': Param(type=ostr, max=260),
        'privacy_indicator': Param(type=int, size=1),
        'callback_num': Param(type=str, min=4, max=19),
        'callback_num_pres_ind': Param(type=int, size=1),
        'source_subaddress': Param(type=str, min=2, max=23),
        'dest_subaddress': Param(type=str, min=2, max=23),
        'user_response_code': Param(type=int, size=1),
        'display_time': Param(type=int, size=1),
        'sms_signal': Param(type=int, size=2),
        'ms_validity': Param(type=int, size=1),
        'ms_msg_wait_facilities': Param(type=int, size=1),
        'number_of_messages': Param(type=int, size=1),
        'alert_on_message_delivery': Param(type=flag),
        'language_indicator': Param(type=int, size=1),
        'its_reply_type': Param(type=int, size=1),
        'its_session_info': Param(type=int, size=2),
        'ussd_service_op': Param(type=int, size=1),
    }

    params_order = ('service_type', 'source_addr_ton', 'source_addr_npi',
        'source_addr', 'dest_addr_ton', 'dest_addr_npi',
        'destination_addr', 'esm_class', 'protocol_id', 'priority_flag',
        'schedule_delivery_time', 'validity_period', 'registered_delivery',
        'replace_if_present_flag', 'data_coding', 'sm_default_msg_id',
        'sm_length', 'short_message',

        # Optional params
        'user_message_reference', 'source_port', 'source_addr_subunit',
        'destination_port', 'dest_addr_subunit', 'sar_msg_ref_num',
        'sar_total_segments', 'sar_segment_seqnum', 'more_messages_to_send',
        'payload_type', 'message_payload', 'privacy_indicator',
        'callback_num', 'callback_num_pres_ind', 'source_subaddress',
        'dest_subaddress', 'user_response_code', 'display_time',
        'sms_signal', 'ms_validity', 'ms_msg_wait_facilities',
        'number_of_messages', 'alert_on_message_delivery',
        'language_indicator', 'its_reply_type', 'its_session_info',
        'ussd_service_op')

    
    def __init__(self, command, **args):
        """Initialize"""
        
        Command.__init__(self, command, **(args))

        self._set_vars(**({}.fromkeys(self.params.keys())))


    def prep(self):
        """Prepare to generate binary data"""

        if self.short_message:
            self.sm_length = len(self.short_message)
            delattr(self, 'message_payload')
        else:
            self.sm_length = 0


class SubmitSMResp(Command):
    """Response command for submit_sm"""

    params = {
        'message_id': Param(type=str, max=65)
    }

    params_order = ('message_id',)

    def __init__(self, command):
        """Initialize"""
        
        Command.__init__(self, command)

        self._set_vars(**({}.fromkeys(self.params.keys())))


class DeliverSM(SubmitSM):
    """deliver_sm command class, similar to submit_sm but has different optional params"""

    params = {
        'service_type': Param(type=str, max=6),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'dest_addr_ton': Param(type=int, size=1),
        'dest_addr_npi': Param(type=int, size=1),
        'destination_addr': Param(type=str, max=21),
        'esm_class': Param(type=int, size=1),
        'protocol_id': Param(type=int, size=1),
        'priority_flag': Param(type=int, size=1),
        'schedule_delivery_time': Param(type=str, max=17),
        'validity_period': Param(type=str, max=17),
        'registered_delivery': Param(type=int, size=1),
        'replace_if_present_flag': Param(type=int, size=1),
        'data_coding': Param(type=int, size=1),
        'sm_default_msg_id': Param(type=int, size=1),
        'sm_length': Param(type=int, size=1),
        'short_message': Param(type=ostr, max=254, 
                               len_field='sm_length'),
                               
        # Optional params
        'user_message_reference': Param(type=int, size=2),
        'source_port': Param(type=int, size=2),
        'destination_port': Param(type=int, size=2),
        'sar_msg_ref_num': Param(type=int, size=2),
        'sar_total_segments': Param(type=int, size=1),
        'sar_segment_seqnum': Param(type=int, size=1),
        'user_response_code': Param(type=int, size=1),
        'privacy_indicator': Param(type=int, size=1),
        'payload_type': Param(type=int, size=1),
        'message_payload': Param(type=ostr, max=260),
        'callback_num': Param(type=str, min=4, max=19),
        'source_subaddress': Param(type=str, min=2, max=23),
        'dest_subaddress': Param(type=str, min=2, max=23),
        'language_indicator': Param(type=int, size=1),
        'its_session_info': Param(type=int, size=2),
        'network_error_code': Param(type=ostr, size=3),
        'message_state': Param(type=int, size=1),
        'receipted_message_id': Param(type=str, max=65),
        }
    
    params_order = ('service_type', 'source_addr_ton', 'source_addr_npi',
        'source_addr', 'dest_addr_ton', 'dest_addr_npi',
        'destination_addr', 'esm_class', 'protocol_id', 'priority_flag',
        'schedule_delivery_time', 'validity_period', 'registered_delivery',
        'replace_if_present_flag', 'data_coding', 'sm_default_msg_id',
        'sm_length', 'short_message',

        # Optional params
        'user_message_reference', 'source_port', 'destination_port', 'sar_msg_ref_num',
        'sar_total_segments', 'sar_segment_seqnum', 'user_response_code',
        'privacy_indicator', 'payload_type', 'message_payload',
        'callback_num','source_subaddress',
        'dest_subaddress','language_indicator', 'its_session_info', 
        'network_error_code','message_state','receipted_message_id')
    
class DeliverSMResp(SubmitSMResp): 
    """deliver_sm_response response class, same as submit_sm"""
    message_id = None


class Unbind(Command):
    """Unbind command"""

    params = {}
    params_order = ()


class UnbindResp(Command):
    """Unbind response command"""

    params = {}
    params_order = ()

class EnquireLink(Command):
    params = {}
    params_order = ()

class EnquireLinkResp(Command):
    params = {}
    params_order = ()