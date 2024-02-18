import logging
from threading import Thread

from pymavlink.dialects.v20.ardupilotmega import MAVLink_message
from pymavlink.mavutil import mavfile

from .uav_data import UAVData

logger = logging.getLogger()


class DirectReceiveLoop(Thread):
    def __init__(self, mavlink_connection: mavfile, uav_data: UAVData) -> None:
        super().__init__(name=self.__class__.__name__)
        self.mavlink_connection = mavlink_connection
        self.data = uav_data

    def run(self) -> None:
        logger.info("Starting Telemetry Loop")

        while True:
            msg: MAVLink_message = self.mavlink_connection.recv_match(blocking=True)

            if not msg:
                continue

            self.data.process_mav_encapsulated_data(msg)
            if (
                self.data.uav_addr.system_id == msg.get_srcSystem()
                or self.data.uav_addr.component_id == msg.get_srcComponent()
            ):
                self.data.process_mav_telem(msg)
