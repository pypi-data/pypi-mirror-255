#!/bin/python

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mbio import MBIO

from .items import Items
# from .config import MBIOConfig
from .xmlconfig import XMLConfig
from .device import MBIODevices, MBIODeviceGeneric
from .value import MBIOValues, MBIOValueDigital

from .metzconnect import MBIODeviceMetzConnectMRAI8
from .metzconnect import MBIODeviceMetzConnectMRAOP4
from .metzconnect import MBIODeviceMetzConnectMRDI10
from .metzconnect import MBIODeviceMetzConnectMRDI4
from .metzconnect import MBIODeviceMetzConnectMRDO4
from .belimo import MBIODeviceBelimoP22RTH
from .digimatplc import MBIODeviceDigimatPLC
from .ebm import MBIODeviceEBM

from .socket import MBIOSocketString

import time
import threading

from prettytable import PrettyTable

from pymodbus.client import ModbusTcpClient
import logging
import ipcalc

# from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder

# Modbus Clients Examples
# https://pymodbus.readthedocs.io/en/dev/source/examples.html


class MBIOGateway(object):
    """MBIOGateway object, containing MBIOValues containing every MBIOValue"""
    def __init__(self, parent: MBIO, name, host, port=502, interface=None, timeout=3, retries=3, xml: XMLConfig = None):
        self._parent: MBIO = parent
        self._name=str(name).lower()
        if not name:
            name='gw%d' % parent.gateways.count()
        self._host=host
        self._model=None
        self._MAC=None
        self._password=None
        self._interface=interface
        self._port=port
        self._timeout=timeout
        self._retries=retries
        self._error=False

        self._key='%s' % self._name

        self._client: ModbusTcpClient=None
        self._timeoutClient=0
        self._timeoutIdleAfterSend=0

        self._devices=MBIODevices(parent.logger)
        self._sysvalues=MBIOValues(self, self.key, self.logger)
        self._sysComErr=MBIOValueDigital(self._sysvalues, 'comerr')

        self.logger.info('Declaring GW:%s', self.host)

        self._eventStop=threading.Event()

        self.load(xml)

        # FIXME: daemon=True ?
        self._thread=threading.Thread(target=self.manager)
        self.logger.info("Starting background GW:%s task" % self.host)
        self._thread.start()

    @property
    def parent(self) -> MBIO:
        return self._parent

    def getMBIO(self) -> MBIO:
        return self._parent

    @property
    def logger(self):
        return self._parent.logger

    def configurator(rself):
        # To be overriden
        pass

    def onLoad(self, xml: XMLConfig):
        pass

    def load(self, xml: XMLConfig):
        if xml:
            try:
                self._MAC=xml.get('mac')
                self._model=xml.get('model')
                self._password=xml.get('password')
                if xml.isConfig('gateway'):
                    # TODO: clone other gw feature
                    self.onLoad(xml)
            except:
                self.logger.exception('%s:%s:load()' % (self.__class__.__name__, self.key))

    @property
    def key(self):
        return self._key

    def timeout(self, delay):
        return time.time()+delay

    def isTimeout(self, t):
        if time.time()>=t:
            return True
        return False

    def isOpen(self):
        if self._client and self._client.is_socket_open():
            return True
        return False

    def open(self):
        if not self._client:
            try:
                self.logger.info('Connecting to GW %s:%d (interface %s)' % (self._host, self._port, self._interface))
                source=(self._interface, 0)
                if not self._interface:
                    source=None
                self._client=ModbusTcpClient(host=self._host, port=self._port,
                            source_address=source,
                            timeout=self._timeout,
                            retries=self._retries,
                            # broadcast_enable=True,
                            # strict=True,
                            close_comm_on_error=False)
                # FIXME: how to disable correctly pymodbus logging (connect errors) ?
                logger=logging.getLogger()
                if logger:
                    logger.setLevel(logging.CRITICAL)
                self._timeoutIdleAfterSend=0
            except:
                pass

        if self._client:
            if self._client.connected:
                return self._client
            try:
                if self.isTimeout(self._timeoutClient):
                    self._timeoutClient=self.timeout(15)
                    self.logger.info('Opening socket')
                    if self._client.connect():
                        return self._client
            except:
                pass

    def close(self):
        try:
            if self._client:
                self.logger.info('Closing socket')
                self._client.close()
        except:
            pass
        self._client=None

    @property
    def client(self):
        return self.open()

    @property
    def name(self):
        return self._name

    @property
    def host(self):
        return self._host

    @property
    def MAC(self):
        return self._MAC

    @property
    def model(self):
        return self._model

    @property
    def password(self):
        return self._password

    def probe(self, address):
        try:
            self.logger.debug('Probing device address %d' % address)
            self.checkIdleAfterSend()
            r=self.client.read_device_information(slave=address)
            self.signalMessageTransmission()
            if r and not r.isError():
                data={'address': address,
                      'vendor': r.information[0].decode(),
                      'model': r.information[1].decode(),
                      'version': r.information[2].decode()}
                self.logger.info('Found device [%s] [%s] %s at address %d' %
                                 (data['vendor'], data['model'], data['version'], address))
                return data
        except:
            pass

    # FIXME: implement a better MBIODevice class registration
    def declareDeviceFromName(self, vendor, model, address, xml: XMLConfig = None):
        try:
            address=int(address)
            model=model or 'unknown'

            if vendor and address>0:
                vendor=vendor.lower()
                model=model.lower()
                device=None

                if 'metz' in vendor:
                    if 'di10' in model:
                        device=MBIODeviceMetzConnectMRDI10(self, address, xml=xml)
                    if 'di4' in model:
                        device=MBIODeviceMetzConnectMRDI4(self, address, xml=xml)
                    elif 'do4' in model:
                        device=MBIODeviceMetzConnectMRDO4(self, address, xml=xml)
                    elif 'aop4' in model or 'ao4' in model:
                        device=MBIODeviceMetzConnectMRAOP4(self, address, xml=xml)
                    elif 'ai8' in model:
                        device=MBIODeviceMetzConnectMRAI8(self, address, xml=xml)

                elif 'belimo' in vendor:
                    if 'p22rth' in model:
                        device=MBIODeviceBelimoP22RTH(self, address, xml=xml)

                elif 'digimat' in vendor:
                    if 'plc' in model:
                        device=MBIODeviceDigimatPLC(self, address, xml=xml)

                elif 'ebm' in vendor:
                    if 'base' in model:
                        device=MBIODeviceEBM(self, address, xml=xml)

                elif 'generic' in vendor:
                    device=MBIODeviceGeneric(self, address, xml=xml)

                return device
        except:
            pass

    def discover(self, start=1, end=32, maxerrors=3):
        devices=[]
        errors=0
        for address in range(start, end+1):
            data=self.probe(address)
            if data:
                if not self.device(address):
                    device=self.declareDeviceFromName(data['vendor'], data['model'], address)
                    if device:
                        devices.append(device)
                continue
            errors+=1
            maxerrors-=1
            if maxerrors>0 and errors>maxerrors:
                break
        return devices

    def ping(self, address):
        try:
            self.checkIdleAfterSend()
            r=self.client.diag_read_bus_message_count(slave=address)
            self.signalMessageTransmission()
            if r:
                if not r.isError():
                    return True
            self.logger.error('Unable to ping device %d' % address)
        except:
            # self.logger.exception('ping')
            pass
        return False

    def stop(self):
        self.halt()
        self._eventStop.set()

    def waitForThreadTermination(self):
        self.stop()
        self._thread.join()
        self.close()

    def sleep(self, delay=1):
        try:
            if self._eventStop.is_set():
                return True
            return self._eventStop.wait(delay)
        except:
            pass

    def checkIdleAfterSend(self):
        while not self.isTimeout(self._timeoutIdleAfterSend):
            self.sleep(0.001)

    def signalMessageTransmission(self):
        # https://minimalmodbus.readthedocs.io/en/stable/serialcommunication.html
        # 19200bps->2ms
        self._timeoutIdleAfterSend=self.timeout(0.002)

    def manager(self):
        while True:
            self.sleep(0.1)
            try:
                halted=True
                error=False
                for device in self._devices:
                    device.manager()
                    device.microsleep()
                    if device.isError():
                        error=True
                    if not device.isHalted():
                        halted=False

                self._error=error
                self._sysComErr.updateValue(self._error)

                if self._eventStop.is_set():
                    if halted:
                        self.logger.info("Exiting background GW:%s task" % self.host)
                        self.close()
                        return
            except:
                self.logger.exception("Background GW:%s task" % self.host)

    def isError(self):
        return self._error

    @property
    def devices(self):
        return self._devices

    def device(self, did):
        return self._devices.item(did)

    def reset(self, address=None):
        if address is not None:
            try:
                self.device(address).reset()
            except:
                pass
        else:
            self._devices.reset()

    def resetHalted(self):
        self._devices.resetHalted()

    def halt(self, address=None):
        if address is not None:
            try:
                self.device(address).halt()
            except:
                pass
        else:
            self._devices.halt()

    def dump(self):
        if self._devices:
            t=PrettyTable()
            t.field_names=['ADR', 'Key', 'Vendor', 'Model', 'Version', 'Class', 'State', 'Error', 'Values']
            t.align='l'
            for device in self._devices:
                t.add_row([device.address, device.key, device.vendor, device.model, device.version,
                           device.__class__.__name__, device.statestr(), str(device.isError()), device.values.count()])

        print(t.get_string(sortby="ADR"))

    def count(self):
        return len(self._devices)

    def __getitem__(self, key):
        return self.device(key)

    # FIXME: for METZ only
    def rs485(self, speed, parity='E'):
        data=0x5300

        parity=parity.upper()
        if parity[0]=='E':
            data|=0x10
        elif parity[0]=='O':
            data|=0x20
        else:
            data|=0x30

        try:
            n=[1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200].index(int(speed))
            data|=(0x1+n)
        except:
            return

        self.checkIdleAfterSend()
        self.client.write_registers(0x41, data, slave=0)
        self.signalMessageTransmission()
        # self.client.diag_restart_communication(False, slave=0)
        # for device in self._devices:
        for device in range(1, 32):
            print("Set speed 0x%02X for device %d" % (data, device))
            self.checkIdleAfterSend()
            self.client.write_registers(0x41, data)
            self.signalMessageTransmission()

    def __repr__(self):
        state='CLOSED'
        if self.isOpen():
            state='OPEN'
        return '%s(%s=%s, %d devices, %s)' % (self.__class__.__name__, self.name, self.host, self.count(), state)

    # FIXME: debug
    def toggle(self):
        for device in self.devices:
            try:
                device.toggle()
            except:
                pass

    def on(self):
        for device in self.devices:
            try:
                device.on()
            except:
                pass

    def off(self):
        for device in self.devices:
            try:
                device.off()
            except:
                pass

    def auto(self):
        for device in self.devices:
            device.auto()

    def manual(self):
        for device in self.devices:
            device.manual()


class MBIOGateways(Items):
    def __init__(self, logger):
        super().__init__(logger)
        self._items: list[MBIOGateway]=[]
        self._itemByHost={}
        self._itemByKey={}
        self._itemByName={}

    def item(self, key):
        item=super().item(key)
        if item:
            return item

        item=self.getByKey(key)
        if item:
            return item

        item=self.getByHost(key)
        if item:
            return item

        item=self.getByName(key)
        if item:
            return item

        try:
            return self[key]
        except:
            pass

    def add(self, item: MBIOGateway) -> MBIOGateway:
        if isinstance(item, MBIOGateway):
            super().add(item)
            self._itemByName[item.name]=item
            self._itemByKey[item.key]=item
            self._itemByHost[item.host]=item

    def getByHost(self, host):
        try:
            return self._itemByHost[host]
        except:
            pass

    def getByName(self, name):
        try:
            return self._itemByName[name]
        except:
            pass

    def getByKey(self, key):
        try:
            return self._itemByKey[key]
        except:
            pass

    def stop(self):
        for item in self._items:
            item.stop()

    def reset(self):
        for item in self._items:
            item.reset()

    def halt(self):
        for item in self._items:
            item.halt()

    def resetHalted(self):
        for item in self._items:
            item.resetHalted()

    def waitForThreadTermination(self):
        for item in self._items:
            item.waitForThreadTermination()

    def discover(self):
        for item in self._items:
            item.discover()

    # def dump(self):
        # if not self.isEmpty():
            # t=PrettyTable()
            # t.field_names=['#', 'Key', 'Name', 'Host', 'Open']
            # t.align='l'
            # for item in self._items:
                # t.add_row([self.index(item), item.key, item.name, item.host, item.isOpen()])

        # print(t.get_string(sortby="Key"))


class MBIOGatewayMetzConnect(MBIOGateway):
    def configurator(self):
        return MBIOGatewayMetzConnectConfigurator(self.host, self.password)


class MBIOGatewayMetzConnectConfigurator(object):
    def __init__(self, host, password):
        self._host=host
        self._password=password
        self._link=MBIOSocketString(self._host, 23)
        self._config={}
        self._updated=False
        self._buf=None
        self._auth=False
        self.reset()

    @property
    def config(self):
        return self._config or self

    def reset(self):
        self._buf=''

    def isConnected(self):
        if self._link.isConnected():
            return True

    def isAuthenticated(self):
        if self.isConnected() and self._auth:
            return True
        return False

    def auth(self):
        if self.isConnected():
            if self._auth:
                return True
            passwords=['1234']
            if self._password:
                passwords.insert(0, self._password)
            for password in passwords:
                if self.send(password):
                    self._auth=True
                    self.update()
                    return True
        return False

    def connect(self):
        if self.isConnected():
            return self.auth()
        self._auth=False
        if self._link.connect(timeout=3.0):
            return self.auth()

    def disconnect(self):
        self._link.disconnect()
        self._auth=False
        self.reset()

    def __del__(self):
        self.disconnect()
        self._link=None

    def read(self):
        if self.isConnected():
            data=self._link.read()
            if data:
                self._buf+=data
                return data

    def wait(self, data, timeout=3.0):
        t=time.time()+timeout
        while True:
            r=self.read()
            if r and data in self._buf:
                return self._buf
            if not self._auth and 'password:' in self._buf:
                break
            if not timeout:
                break
            time.sleep(0.01)
            if time.time()>=t:
                break

    def waitprompt(self, timeout=3.0):
        if self.wait('>', timeout):
            try:
                lines=[]
                buf=self._buf.replace('\r\n', '\n')
                for line in buf.split('\n'):
                    line=line.strip()
                    if not line or line=='>':
                        continue
                    lines.append(line)
                return lines
            except:
                pass

    def send(self, data, timeout=3.0):
        if self.isConnected():
            self.reset()
            if self._link.write(data+'\n'):
                return self.waitprompt(timeout)
        return False

    def updateInfo(self):
        if self.isConnected():
            data=self.send('inf')
            if data:
                try:
                    for line in data:
                        pos=line.find(':')
                        if pos>0:
                            key=line[:pos]
                            value=line[pos+1:]
                            key=key.strip().lower()
                            value=value.strip()
                            if key and value:
                                self._config[key]=value
                    return True
                except:
                    pass

    def updateConfig(self):
        if self.isConnected():
            data=self.send('cfg')
            if data:
                try:
                    for line in data:
                        pos=line.find(':')
                        if pos>0:
                            key=line[:pos]
                            value=line[pos+1:]
                            key=key.strip().lower()
                            value=value.strip()
                            if key and value:
                                if 'commands' not in key:
                                    self._config[key]=value
                    return True
                except:
                    pass

    def update(self):
        if self.updateInfo() and self.updateConfig():
            return self._config

    def __getitem__(self, key):
        try:
            return self._config[key.lower()]
        except:
            pass

    def check(self, key, value):
        try:
            if self._config[key.lower()]==value:
                return True
        except:
            pass
        return False

    def command(self, command, value):
        if self.isConnected():
            if command and value is not None:
                command=command.lower()
                value=str(value)
                if value and command in ['name', 'ip', 'mask', 'gateway',
                        'dhcp', 'mac', 'password', 'allowedip', 'allowedmask',
                        'mode', 'parity', 'baudrate', 'stopbits',
                        'timeout', 'terminator', 'idletimeout']:
                    if self.check(command, value):
                        return True
                    self._updated=True
                    self.send('%s %s' % (command, value))
                    if command=='password':
                        self.disconnect()
                    self.update()
                    return self.check(command, value)
        return False

    @property
    def name(self) -> type:
        return self['name']

    @name.setter
    def name(self, value: type):
        self.command('name', value)

    @property
    def password(self) -> type:
        return self['password']

    @password.setter
    def password(self, value: type):
        self.command('password', value)
        self.disconnect()
        self._password=value
        self.connect()

    @property
    def idletimeout(self) -> type:
        return int(self['idletimeout'])

    @idletimeout.setter
    def idletimeout(self, seconds: type):
        seconds=int(seconds)
        if seconds<1:
            seconds=100
        self.command('idletimeout', seconds)

    def setIP(self, ip, mask='255.255.255.0', gw=None):
        try:
            n=ipcalc.Network('%s/%s' % (ip, mask))
            result=self.command('ip', n.to_tuple()[0])
            result&=self.command('mask', str(n.netmask()))
            result&=self.command('dhcp', 0)
            if gw:
                try:
                    n=ipcalc.Network(gw)
                    result&=self.command('gateway', n.to_tuple()[0])
                except:
                    pass
            return result
        except:
            pass
        return False

    def setAllowedIP(self, network):
        try:
            n=ipcalc.Network(network)
            result=self.command('allowedip', n.to_tuple()[0])
            result&=self.command('allowedmask', str(n.netmask()))
            return result
        except:
            pass
        return False

    def setDHCP(self):
        return self.command('dhcp', 1)

    def netrestart(self):
        if self._updated:
            self.send('netstart')
            self._updated=False
            return True

    def setRS485(self, speed=19200, parity='E', stopbits=1, timeout=0.1, terminator=True):
        result=self.command('mode', 0)

        speed=int(speed)
        if speed not in [9600, 19200, 38400, 57600]:
            speed=19200

        result&=self.command('baudrate', speed)
        try:
            parity={'N': 0, 'E': 1, 'O': 2}.get(parity.upper())
            result&=self.command('parity', parity)
        except:
            pass

        if timeout<1:
            timeout=1
        result&=self.command('timeout', int(timeout*1000.0))

        result&=self.command('stopbits', stopbits)
        value=1
        if not terminator:
            value=0
        result&=self.command('terminator', value)
        return result

    def __repr__(self):
        return '%s(%s@%s/%s, fw=%s)' % (self.__class__.__name__, self['name'], self['mac'], self['ip'], self['firmware version'])

    def dump(self):
        t=PrettyTable()
        t.field_names=['Property', 'Value']
        t.align='l'

        for key in self._config:
            t.add_row([key, self._config[key]])

        print(t.get_string())


if __name__ == "__main__":
    pass
