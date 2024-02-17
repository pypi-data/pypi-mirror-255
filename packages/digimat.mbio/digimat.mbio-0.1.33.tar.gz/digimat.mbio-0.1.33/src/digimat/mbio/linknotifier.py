#!/bin/python

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .mbio import MBIO

import time
import socket

from digimat.lp import PacketManager, LP

from .task import MBIOTask
from .xmlconfig import XMLConfig

from .valuenotifier import MBIOValueNotifier


kLP_ST=20
kLP_MBIO=0xA4

kMBIO_PING=0
kMBIO_PONG=1
kMBIO_SYNC=2
kMBIO_RESTART=3
kMBIO_UPDATEVALUE=10
kMBIO_WRITEVALUE=11
kMBIO_UPDATEVALUEREQ=12
kMBIO_DECLAREVALUE=13
kMBIO_NOTIFYDISABLE=14


class MBIOLinkPacketManager(PacketManager):
    def __init__(self, link: MBIOLink, lid=0):
        super().__init__()
        self._link=link
        self._lid=lid

    @property
    def link(self):
        return self._link

    @property
    def logger(self):
        return self._link.logger

    def dispose(self):
        self.link.disconnect()
        super().dispose()

    def write(self, data):
        return self.link.write(data)

    def manager(self):
        data=self.link.read()
        if data:
            self.receive(data)

    def lp(self, lptype=kLP_MBIO):
        lp=LP(packetmanager=self)
        lp.create(lptype, idRequest=self._lid)
        return lp


class MBIOLink(object):
    def __init__(self, mbio: MBIO, host, port=5000, lid=0):
        self._mbio=mbio
        self._host=host
        self._port=port
        self._lid=lid
        self._autoDeclareItems={}
        self._pongReceived=False
        self._protocolVersion=0
        self._socket=None
        self._connected=False
        self._timeoutInhibit=3.0
        self._timeoutActivity=0
        self._delayAutoRefresh=0
        self._packetManager=MBIOLinkPacketManager(self, lid)
        self.registerHandlers()
        self.onInit()

    def onInit(self):
        pass

    @property
    def logger(self):
        return self._mbio.logger

    @property
    def packetManager(self):
        return self._packetManager

    def autoDeclareItemsManager(self):
        if self._autoDeclareItems:
            if self._connected and self._pongReceived:
                try:
                    count=16
                    while count>0:
                        count-=1
                        for data in self._autoDeclareItems.items():
                            (item, value)=data
                            self.logger.info(">DECLAREVALUE %s" % value)
                            lp=self.packetManager.lp()
                            up=lp.up(kMBIO_DECLAREVALUE)
                            up.writeWord(item)
                            up.writeByte(value.isWritable())
                            up.writeStrField(value.key)
                            up.store()
                            lp.send()
                            del(self._autoDeclareItems[item])
                            break
                except:
                    self.logger.exception('autoDeclareItemsManager')
                    self._autoDeclareItems={}

    def manager(self):
        if time.time()>=self._timeoutActivity:
            self.ping()
        self.packetManager.manager()
        self.autoDeclareItemsManager()

    def resetActivityTimeout(self):
        self._timeoutActivity=time.time()+10

    def connect(self):
        try:
            if not self._connected:
                if time.time()>=self._timeoutInhibit:
                    self.logger.info('Opening link %s:%d' % (self._host, self._port))
                    self._socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self._socket.settimeout(3)
                    interface=self._mbio.interface
                    if interface:
                        self.logger.info('Using interface ip %s' % interface)
                        # ifname=(self._interface+'\0').encode('utf-8')
                        # self._socket.setsockopt(socket.SOL_SOCKET, 25, ifname)
                        self._socket.bind((interface, 0))
                    address=(self._host, self._port)
                    self._socket.connect(address)
                    self._socket.settimeout(0)
                    self._connected=True
                    self._timeoutInhibit=time.time()+5
                    self.logger.info("Link connected to %s:%d" % (self._host, self._port))
                    self.resetActivityTimeout()
                    self.onConnect()
                    self._mbio.renotifyValues()
        except:
            self.logger.error("Unable to connect link to %s:%d" % (self._host, self._port))
            self._timeoutInhibit=time.time()+5

    def onConnect(self):
        self.ping()
        self.resync()

    def isConnected(self):
        return self._connected

    def disconnect(self):
        try:
            self._socket.close()
            self._socket=None
        except:
            pass

        if self._connected:
            self.logger.warning("Link disconnected from %s:%d" % (self._host, self._port))
            self._connected=False

    def write(self, data):
        try:
            self.connect()
            self._socket.send(data)
            self.resetActivityTimeout()
        except:
            self.disconnect()

    def read(self):
        try:
            self.connect()
            data = self._socket.recv(4096)
            if not data:
                self.disconnect()
                return

            self.resetActivityTimeout()
            return data
        except:
            pass

    def registerHandlers(self):
        self.packetManager.addHandler(kLP_MBIO, kMBIO_PONG, self.onPong)
        self.packetManager.addHandler(kLP_MBIO, kMBIO_SYNC, self.onSync)
        self.packetManager.addHandler(kLP_MBIO, kMBIO_RESTART, self.onRestart)
        self.packetManager.addHandler(kLP_MBIO, kMBIO_WRITEVALUE, self.onWriteValue)
        self.packetManager.addHandler(kLP_MBIO, kMBIO_UPDATEVALUEREQ, self.onUpdateValueRequest)
        self.packetManager.addHandler(kLP_MBIO, kMBIO_NOTIFYDISABLE, self.onNotifyDisable)

    def ping(self):
        if self._connected:
            self.logger.info(">PING")
            lp=self.packetManager.lp()
            up=lp.up(kMBIO_PING)
            up.store()
            lp.send()

    def resync(self):
        if self._connected:
            self.logger.info(">RESYNC")
            lp=self.packetManager.lp()
            up=lp.up(kMBIO_SYNC)
            up.store()
            lp.send()

    def updateValue(self, value):
        if value is not None and value.value is not None:
            try:
                self.logger.info(">UPDATEVALUE %s" % value)
                value._notifyCount+=1
                lp=self.packetManager.lp()
                up=lp.up(kMBIO_UPDATEVALUE)
                up.writeStr(value.key)
                up.writeFloat(float(value.value))
                up.writeFloat(value.resolution)
                up.writeByte(value.unit)
                up.writeByte(value.flagsAsValue())
                up.store()
                lp.send()
            except:
                self.logger.exception('updateValue')
                self.logger.error(value)

    def onPong(self, up):
        rid=up.readWord()
        protocolRevision=up.readWord()
        maxNbItems=up.readWord()
        itemCount=up.readWord()
        self._delayAutoRefresh=up.readWord()
        self._pongReceived=True
        self.logger.warning("<PONG(id=%u, protocol=%u, %u/%u items, autoRefresh=%us)" %
            (rid, protocolRevision, itemCount, maxNbItems, self._delayAutoRefresh))

    def onSync(self, up):
        self.logger.warning("<SYNC")

    def onRestart(self, up):
        self.logger.warning("<RESTART")
        self.disconnect()

    def onWriteValue(self, up):
        key=up.readStr()
        value=up.readFloat()
        unit=up.readByte()
        flags=up.readByte()
        self.logger.debug('<WRITEVALUE key=%s value=%.02f' % (key, value))

        mbiovalue=self._mbio.value(key)
        if mbiovalue is not None:
            mbiovalue.value=value
            if unit<0xfe:
                mbiovalue.unit=unit
            # TODO: flags

    def onUpdateValueRequest(self, up):
        key=up.readStr()
        value=self._mbio.value(key)
        if value is not None:
            self.logger.warning("<UPDATEVALUEREQ %s" % key)
            value.enableNotify(True)
            value.notify(force=True)

    def onNotifyDisable(self, up):
        key=up.readStr()
        value=self._mbio.value(key)
        if value is not None:
            self.logger.warning("<NOTIFYDISABLE %s" % key)
            value.enableNotify(False)

    # def onReadItemResponse(self, up):
        # pid=up.readWord()
        # index=up.readWord()
        # value=up.readFloat()
        # unit=up.readByte()
        # item=self._items.get(index)
        # if item:
            # item.value=value
            # item.unit=unit


class MBIOTaskLinkNotifier(MBIOTask):
    def onInit(self):
        self._link=None
        self._notifier=MBIOValueNotifier(self.getMBIO())
        self._iterValues=None

    def onLoad(self, xml: XMLConfig):
        mbio=self.getMBIO()

        host=xml.get('host')
        port=xml.getInt('port', 5000)
        lid=xml.getInt('id', 0)

        if host:
            self._link=MBIOLink(mbio, host, port=port, lid=lid)
        else:
            self.logger.error('Unable to create MBIOLink')

        item=0
        for declare in xml.children('declare'):
            item=declare.getInt('item', item)
            for value in declare.children('values'):
                values=mbio.values(value.get('key'))
                for v in values:
                    self._link._autoDeclareItems.update({item: v})
                    item+=1
                item+=value.getInt('skip', 0)

    def poweron(self):
        self._link.connect()
        return True

    def poweroff(self):
        self._link.disconnect()
        return True

    def notifyRefreshManager(self):
        count=8
        while count>0:
            count-=1
            if self._iterValues is None:
                try:
                    # reset list
                    self._iterValues=iter(self.getMBIO()._valuesByKey.values())
                except:
                    pass
            try:
                value=next(self._iterValues)
                # self.logger.warning(value)
                value.notifyManager(self._link._delayAutoRefresh)
            except:
                # force reinit list
                self._iterValues=None
                break

    def run(self):
        self._link.manager()
        if self._link.isConnected():
            if not self._link._autoDeclareItems:
                count=32
                while count>0:
                    value=self._notifier.get()
                    if value is None:
                        break
                    count-=1
                    # self.logger.debug('NOTIFYUPDATE %s' % value)
                    self.updateValue(value)

                self.notifyRefreshManager()
            return 0.1
        return 0.5

    def isError(self):
        if super().isError():
            return True
        if not self._link.isConnected():
            return True
        return False

    def updateValue(self, value):
        self._link.updateValue(value)


if __name__ == "__main__":
    pass
