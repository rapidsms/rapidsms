#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import serial


class GsmError(serial.SerialException):
    pass


class GsmIOError(GsmError):
    pass


class GsmWriteError(GsmIOError):
    pass


class GsmReadError(GsmIOError):
    pass


class GsmReadTimeoutError(GsmReadError):
    def __init__(self, pending_data):
        self.pending_data = pending_data


class GsmModemError(GsmError):
    STRINGS = {
        "CME": {
            3:   "Operation not allowed",
            4:   "Operation not supported",
            5:   "PH-SIM PIN required (SIM lock)",
            10:  "SIM not inserted",
            11:  "SIM PIN required",
            12:  "SIM PUK required",
            13:  "SIM failure",
            16:  "Incorrect password",
            17:  "SIM PIN2 required",
            18:  "SIM PUK2 required",
            20:  "Memory full",
            21:  "Invalid index",
            22:  "Not found",
            24:  "Text string too long",
            26:  "Dial string too long",
            27:  "Invalid characters in dial string",
            30:  "No network service",
            32:  "Network not allowed. Emergency calls only",
            40:  "Network personal PIN required (Network lock)",
            103: "Illegal MS (#3)",
            106: "Illegal ME (#6)",
            107: "GPRS services not allowed",
            111: "PLMN not allowed",
            112: "Location area not allowed",
            113: "Roaming not allowed in this area",
            132: "Service option not supported",
            133: "Requested service option not subscribed",
            134: "Service option temporarily out of order",
            148: "unspecified GPRS error",
            149: "PDP authentication failure",
            150: "Invalid mobile class" },
        "CMS": {
            021: "Call Rejected (out of credit?)",
            301: "SMS service of ME reserved",
            302: "Operation not allowed",
            303: "Operation not supported",
            304: "Invalid PDU mode parameter",
            305: "Invalid text mode parameter",
            310: "SIM not inserted",
            311: "SIM PIN required",
            312: "PH-SIM PIN required",
            313: "SIM failure",
            316: "SIM PUK required",
            317: "SIM PIN2 required",
            318: "SIM PUK2 required",
            321: "Invalid memory index",
            322: "SIM memory full",
            330: "SC address unknown",
            340: "No +CNMA acknowledgement expected",
            500: "Unknown error",
            512: "MM establishment failure (for SMS)",
            513: "Lower layer failure (for SMS)",
            514: "CP error (for SMS)",
            515: "Please wait, init or command processing in progress",
            517: "SIM Toolkit facility not supported",
            518: "SIM Toolkit indication not received",
            519: "Reset product to activate or change new echo cancellation algo",
            520: "Automatic abort about get PLMN list for an incomming call",
            526: "PIN deactivation forbidden with this SIM card",
            527: "Please wait, RR or MM is busy. Retry your selection later",
            528: "Location update failure. Emergency calls only",
            529: "PLMN selection failure. Emergency calls only",
            531: "SMS not send: the <da> is not in FDN phonebook, and FDN lock is enabled (for SMS)" }}

    def __init__(self, type=None, code=None):
        self.type = type
        self.code = code

    def __str__(self):
        if self.type and self.code:
            return "%s ERROR %d: %s" % (
                self.type, self.code,
                self.STRINGS[self.type][self.code])

        # no type and/or code were provided
        else: return "Unknown GSM Error"
