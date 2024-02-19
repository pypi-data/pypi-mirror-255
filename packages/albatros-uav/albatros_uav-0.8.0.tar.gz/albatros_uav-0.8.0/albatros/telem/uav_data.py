import logging
from queue import Queue
from time import time

from pymavlink.dialects.v20.ardupilotmega import (
    MAVLink_encapsulated_data_message,
    MAVLink_message,
)

from .message_models import (
    Attitude,
    CommandACK,
    EncapsulatedData,
    GlobalPositionInt,
    GPSRawInt,
    GPSStatus,
    Heartbeat,
    HomePosition,
    LocalPositionNED,
    MavMessage,
    MissionACK,
    MissionItemReached,
    MissionRequestInt,
    NavControllerOutput,
    ParamValue,
    PositionTargetLocalNED,
    RadioStatus,
    RCChannels,
    RcChannelsRaw,
    ServoOutputRaw,
    SysStatus,
    WindCov,
)
from .models import ComponentAddress

logger = logging.getLogger()


class UAVData:
    def __init__(self, uav_addr: ComponentAddress) -> None:
        self.uav_addr = uav_addr
        self.heartbeat = Heartbeat()
        self.global_position_int = GlobalPositionInt()
        self.attitude = Attitude()
        self.gps_raw_int = GPSRawInt()
        self.gps_status = GPSStatus()
        self.radio_status = RadioStatus()
        self.rc_channel_raw = RcChannelsRaw()
        self.servo_output_raw = ServoOutputRaw()
        self.sys_status = SysStatus()
        self.mission_request_int = MissionRequestInt()
        self.mission_ack = MissionACK()
        self.mission_item_reached = MissionItemReached()
        self.command_ack = CommandACK()
        self.param_value = ParamValue()
        self.position_target_local_ned = PositionTargetLocalNED()
        self.home_position = HomePosition()
        self.local_position_ned = LocalPositionNED()
        self.nav_controller_output = NavControllerOutput()
        self.rc_channels = RCChannels()
        self.wind_cov = WindCov()
        self.encapsulated_data: "Queue[EncapsulatedData]" = Queue(maxsize=1)

    def process_mav_encapsulated_data(self, msg: MAVLink_message) -> None:
        try:
            if isinstance(msg, MAVLink_encapsulated_data_message):
                dict_msg = msg.to_dict()
                data_size = int(msg.data[0])
                data = bytes(msg.data[1 : data_size + 1])
                dict_msg["data"] = data

                en_data_obj = EncapsulatedData.parse_obj(dict_msg)
                en_data_obj.timestamp_ms = int(time() * 1000)

                if self.encapsulated_data.full():
                    self.encapsulated_data.get()
                self.encapsulated_data.put(en_data_obj)
                logger.debug("received message type: %s", en_data_obj.mavpackettype)
        except AttributeError:
            logger.debug("could not parse message type: %s", msg.get_type())

    def process_mav_telem(self, msg: MAVLink_message) -> None:
        try:
            if not isinstance(msg, MAVLink_encapsulated_data_message):
                msg_class: MavMessage = getattr(self, msg.get_type().lower()).__class__
                new_obj = msg_class.parse_obj(msg.to_dict())
                new_obj.timestamp_ms = int(time() * 1000)
                setattr(self, msg.get_type().lower(), new_obj)
                logger.debug("received message type: %s", new_obj.mavpackettype)
        except AttributeError:
            logger.debug("could not parse message type: %s", msg.get_type())
