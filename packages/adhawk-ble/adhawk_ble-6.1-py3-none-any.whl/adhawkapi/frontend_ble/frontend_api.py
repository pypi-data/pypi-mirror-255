'''This module facilitates the communication with the eye tracker over BLE'''

import adhawkapi
from adhawkapi import frontend

from . import blecom


class FrontendApi(frontend.FrontendApi):
    '''Specialized FrontendApi for communication over BLE'''

    def __init__(self, devname, eye_mask=adhawkapi.EyeMask.BINOCULAR):
        super().__init__(eye_mask)
        self._devname = devname

    def _create_com(self):
        return blecom.BLECom(self._devname, self._handler.handle_packet)
