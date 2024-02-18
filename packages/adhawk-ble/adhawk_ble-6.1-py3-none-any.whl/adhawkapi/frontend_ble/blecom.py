'''Module to handle communications with BLE trackers'''

import asyncio
import logging
import random
import struct
import threading
import queue

from bleak import BleakError, BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

from adhawkapi import AckCodes, PacketType


COMMAND_CHARACTERISTIC_UUID = '7f694ea3-1d44-49c5-8ae3-10e64037741e'
ET_CHARACTERISTIC_UUID = '26760f11-42c7-4439-8743-53a052d7e127'
EVENT_CHARACTERISTIC_UUID = 'ab2af9ff-f7c2-4b21-bf52-b24113fea0f2'
TRACKER_READY_CHARACTERISTIC_UUID = 'ab2af9ff-f7c2-4b21-bf52-b24113fea0f3'
STREAM_CHARACTERISTIC_UUID = 'ab2af9ff-f7c2-4b21-bf52-b24113fea0f4'

MAX_REQUEST_ID = 0xffff


class BLECom:
    '''Class to handle communications with BLE trackers'''

    def __init__(self, device_name, packet_handler):
        self._device_name = device_name
        self._packet_handler = packet_handler
        self._client = None
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._main_loop, name='ble_com')
        self._shutting_down = False
        self._requests = queue.Queue()
        self._cur_request_id = random.randint(0, MAX_REQUEST_ID)

    def start(self):
        '''start'''
        self._thread.start()
        try:
            asyncio.run_coroutine_threadsafe(self._start(), self._loop)
        except Exception:  # pylint: disable=broad-except
            self.shutdown()
            return

    def shutdown(self):
        '''shutdown'''
        if self._shutting_down:
            return

        self._shutting_down = True
        asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)
        self._thread.join()

    def send(self, data: bytearray):
        '''send'''
        asyncio.run_coroutine_threadsafe(self._send(data), self._loop)

    def _main_loop(self):
        try:
            self._loop.run_forever()
        finally:
            self._loop.close()

    async def _start(self):
        logging.info('Scanning...')
        try:
            # backendcom.py never times out, so this matches that behaviour
            device = await BleakScanner.find_device_by_name(name=self._device_name, timeout=None)
            if device is None:
                logging.error(f"Could not find: {self._device_name}")
                return False
        except BleakError as error:
            logging.error(error)
            return False

        logging.info('Connecting...')
        self._client = BleakClient(device, disconnected_callback=self._handle_disconnect)
        await self._client.connect()

        await self._client.start_notify(COMMAND_CHARACTERISTIC_UUID, self._handle_response)
        await self._client.start_notify(ET_CHARACTERISTIC_UUID, self._handle_stream_data)
        await self._client.start_notify(EVENT_CHARACTERISTIC_UUID, self._handle_stream_data)
        await self._client.start_notify(TRACKER_READY_CHARACTERISTIC_UUID, self._handle_stream_data)
        await self._client.start_notify(STREAM_CHARACTERISTIC_UUID, self._handle_stream_data)
        logging.info('Connected!')

        # Send a tracker state message to trigger the "device connected" callback
        data = struct.pack('<BB', PacketType.TRACKER_STATUS, AckCodes.SUCCESS)
        self._packet_handler(data[0], data[1:])
        return True

    async def _shutdown(self):
        if self._client:
            await self._client.disconnect()
        self._loop.stop()

    async def _send(self, data: bytearray):
        self._requests.put(self._cur_request_id)
        request = struct.pack('<H', self._cur_request_id) + data
        self._cur_request_id = (self._cur_request_id + 1) % MAX_REQUEST_ID

        await self._client.write_gatt_char(COMMAND_CHARACTERISTIC_UUID, request)

    def _handle_response(self, _characteristic: BleakGATTCharacteristic, data: bytearray):
        request_id, = struct.unpack('<H', data[:2])
        expected_request_id = self._requests.get()
        if expected_request_id != request_id:
            logging.warning(f'Unexpected response. Expected: {expected_request_id}, Received: {request_id}')
            return

        self._packet_handler(data[2], data[3:])

    def _handle_stream_data(self, _characteristic: BleakGATTCharacteristic, data: bytearray):
        self._packet_handler(data[0], data[1:])

    def _handle_disconnect(self, _client):
        if not self._shutting_down:
            data = struct.pack('<BB', PacketType.TRACKER_STATUS, AckCodes.TRACKER_DISCONNECTED)
            self._packet_handler(data[0], data[1:])
            asyncio.run_coroutine_threadsafe(self._start(), self._loop)
