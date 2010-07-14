#!/usr/bin/env python
# vim: et ai sts=4 sw=4 ts=4


import time
import socket

from ..models import Connection
from .base import BackendBase

from ..utils.modules import try_import
smpplib = try_import('smpplib')


class Backend(BackendBase):

    def __init__(self, *args, **kwargs):
        BackendBase.__init__(*args, **kwargs)

        if smpplib is None:
            raise ImportError(
                "The rapidsms.backends.smpp engine is not available, " +
                "because 'smpplib' is not installed.")

    def configure(self, **args):
        self.host = args['host']
        self.port = args['port']
        self.user = args['username']
        self.pwd  = args['password']
        self.sender = args['sender']
        self.system_type = args['system_type'] if args.has_key('system_type') else None
        self.address_range = args['address_range'] if args.has_key('address_range') else None

        # compulsory SMPP parameters
        self.source_addr_ton = args['source_addr_ton'] if args.has_key('source_addr_ton') else 0
        self.dest_addr_ton   = args['dest_addr_ton'] if args.has_key('dest_addr_ton') else 0
	
        self.smppClient = Client(self.host, self.port)
        self.smppClient.set_message_received_handler(self.recv_handler)
        self.justConnected = False

    def run (self):
        while self.running and self.smppClient.connectAndBind(
            system_id=self.user, password=self.pwd,
            address_range=self.address_range, system_type=self.system_type):
            if not self.smppClient.justConnected and self.smppClient.isConnected and self.smppClient.isBinded:
                self.info('Connected to %s:%s' % (self.host, self.port))
                self.smppClient.justConnected = True
            if self.message_waiting and self.smppClient.isConnected and self.smppClient.isBinded:
                msg = self.next_message()
                self.outgoing(msg)
            if not self.smppClient.listen():
                break

        self.info("Shutting down...")
        self.smppClient.disconnect()

    def outgoing (self, msg):
        try:
            senderAddress = msg.return_addr
        except AttributeError:
            senderAddress = self.sender
        target = msg.connection.identity
        self.info("sending to %s: %s", target, msg.text)
        self.smppClient.send_message(
            source_addr_ton = self.source_addr_ton,
            source_addr     = senderAddress,
            dest_addr_ton   = self.dest_addr_ton,
            destination_addr= target,
            short_message   = msg.text)

    def recv_handler(self, **args):
        p = args['pdu']
        self.debug("%s >> %s : %s", p.source_addr, 
            p.destination_addr, p.short_message)

        self.info("injecting message into router")
        con = Connection(self, p.source_addr)
        msg = self.message(con.identity, p.short_message)
        msg.return_addr = p.destination_addr
        self.route(msg)


if smpplib is not None:
    class Client(smpplib.client.Client):
        '''I needed to override certain functionality that's the reason 
        for this'''
        def __init__(self, host, port, debug=False):
            self.isConnected = False
            self.isBinded    = False
            self.justConnected = False
            self.failedToConnect = False
            smpplib.client.Client.__init__(self, host, port)
            smpplib.client.DEBUG = debug

        def disconnect(self):
            try:
                self.unbind()
            except socket.error:
                pass
            except Exception:
                pass

            try:
                smpplib.client.Client.disconnect(self)
                self._socket.shutdown()
            except socket.error:
                pass
            except Exception:
                pass

            self.isConnected = False
            self.isBinded = False
            self.justConnected = False
            return True

        def connect(self):
            '''This method continues to attempt to connect to the server
            until it's either successful or there's an interrupt'''
            
            if not self.isConnected:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(0.1)
        
                try:
                    if self.failedToConnect:
                        time.sleep(3)
                    smpplib.client.Client.connect(self)
                    self.isConnected = True
                    return self.isConnected
                except KeyboardInterrupt:
                    return self.isConnected
                except smpplib.client.ConnectionError:
                    self.failedToConnect = True
                    return self.isConnected

            # This gets called if there's an attempt to reconnect an 
            # established connection
            return self.isConnected

        def connectAndBind(self, **args):
            '''Connects and binds to the server as a transceiver'''
            if not self.isBinded and self.connect():
                try:
                    self.bind_transceiver(**(args))
                    self.isBinded = True
                    return self.isBinded
                except socket.error:
                    self.disconnect()
                    return self.isBinded
                except Exception:
                    self.disconnect()
                    return self.isBinded
                except KeyboardInterrupt:
                    self.disconnect()
                    return self.isBinded
            #return self.isBinded and self.isConnected
            return True

        def listen(self):
            """Listen for PDUs and act"""
            if not (self.isConnected and self.isBinded):
                return True

            if not self.receiver_mode:
                raise Exception('Client.listen() is not allowed to be ' \
                    'invoked manually for non receiver connection')

            p = None

            try:
                p = self.read_pdu()
            except socket.timeout:
                #smpplib.client.log('Socket timeout, listening again')
                return True
            except KeyboardInterrupt:
                return False
            except socket.error:
                # We have a socket error and we assume we've been disconnected
                # we don't want to implicitly shutdown the backend but we want
                # to attempt to reconnect
                self.disconnect()
                return True
            except smpplib.client.ConnectionError:
                self.disconnect()
                return True

            if p and p.command == 'unbind': #unbind_res
                smpplib.client.log('Unbind command received')
                # Don't know if I should return True on this one
                return True
            elif p and p.command == 'deliver_sm':
                self._message_received(p)
            elif p and p.command == 'enquire_link':
                self._enquire_link_received()
            else:
                if p:
                    print "WARNING: Unhandled SMPP command '%s'" % p.command

                self.disconnect()
                #self.isConnected = False # Found out this happens
                return True

            # message was handled so return True
            return True
