"""
A module that provides high-level functions to perform actions on UAVs.
"""

import logging
import time
from copy import deepcopy
from typing import Optional, TypeVar

from pymavlink.dialects.v20.ardupilotmega import (
    MAV_CMD_COMPONENT_ARM_DISARM,
    MAV_CMD_DO_REPOSITION,
    MAV_CMD_DO_SET_SERVO,
    MAV_CMD_REQUEST_MESSAGE,
    MAV_DATA_STREAM_ALL,
    MAV_DATA_STREAM_EXTENDED_STATUS,
    MAV_DATA_STREAM_POSITION,
    MAV_DATA_STREAM_RAW_CONTROLLER,
    MAV_DATA_STREAM_RAW_SENSORS,
    MAV_DATA_STREAM_RC_CHANNELS,
    MAV_MODE_FLAG_SAFETY_ARMED,
    MAVLINK_MSG_ID_HOME_POSITION,
    MAVLink_encapsulated_data_message,
    MAVLink_message,
    MAVLink_request_data_stream_message,
)

from albatros.enums import ConnectionType
from albatros.telem import ComponentAddress
from albatros.telem.drivers import (
    DirectConnectionDriver,
    RedisConnectionDriver,
    TelemDriver,
    TestDriver,
)

from .enums import CommandResult
from .nav.position import PositionGPS, PositionNED, ned2geo
from .outgoing.commands import get_command_int_message, get_command_long_message
from .outgoing.param_messages import (
    get_param_request_list_message,
    get_param_request_read_message,
    get_param_set_message,
)
from .telem.message_models import (
    CommandACK,
    EncapsulatedData,
    Heartbeat,
    HomePosition,
    MavMessage,
    NavControllerOutput,
    ParamValue,
)
from .telem.uav_data import UAVData

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="MavMessage")


TIMEOUT_S = 0.5
HEARTBEAT_TIMEOUT_S = 5
CHECK_PERIOD_S = 0.01

MAX_DATA_SIZE_BYTES = 252


class UAV:
    """Provides generic UAV activities that are common to drones and planes."""

    def __init__(
        self,
        uav_addr: ComponentAddress = ComponentAddress(system_id=1, component_id=1),
        my_addr: ComponentAddress = ComponentAddress(system_id=1, component_id=191),
        connection_type: ConnectionType = ConnectionType.DIRECT,
        device: Optional[str] = "udpin:0.0.0.0:14550",
        baud_rate: Optional[int] = 115200,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        self._uav_addr = uav_addr
        self._my_addr = my_addr
        self._driver: TelemDriver
        self.data = UAVData(uav_addr)

        if connection_type == ConnectionType.DIRECT:
            if not device or not baud_rate:
                raise ValueError
            self._driver = DirectConnectionDriver(
                self._my_addr, self.data, device, baud_rate
            )

        elif connection_type == ConnectionType.REDIS:
            if not host or not port:
                raise ValueError
            self._driver = RedisConnectionDriver(self._my_addr, self.data, host, port)

        elif connection_type == ConnectionType.TEST:
            self._driver = TestDriver(self._my_addr, self.data)
        else:
            raise NotImplementedError

        if not self._driver.make_connection():
            raise TimeoutError

        self.request_data_stream(MAV_DATA_STREAM_ALL, 1)
        self.request_data_stream(MAV_DATA_STREAM_POSITION, 10)
        self.request_data_stream(MAV_DATA_STREAM_RAW_CONTROLLER, 10)
        self.request_data_stream(MAV_DATA_STREAM_RAW_SENSORS, 2)
        self.request_data_stream(MAV_DATA_STREAM_EXTENDED_STATUS, 2)
        self.request_data_stream(MAV_DATA_STREAM_RC_CHANNELS, 2)

    def is_armed(self) -> bool:
        """Check whether the UAV is armed.

        Returns:
            `True` if vehicle is armed.
        """
        armed_flag = self.data.heartbeat.base_mode & MAV_MODE_FLAG_SAFETY_ARMED
        return bool(armed_flag)

    def wait_gps_fix(self) -> None:
        """Wait for GPS 3D fix.

        Fix type must be at least `3D_FIX`.
        """
        while self.data.gps_raw_int.fix_type < 3 or self.data.gps_raw_int.lat == 0:
            time.sleep(CHECK_PERIOD_S)

    def wait_heartbeat(self) -> Heartbeat:
        """Wait for next heartbeat message.

        Raises:
            `TimeoutError`: if there is no `Heartbeat` for 5 seconds.
        """
        clock_start = time.time()
        while time.time() - clock_start < HEARTBEAT_TIMEOUT_S:
            time_dif = time.time() - self.data.heartbeat.timestamp_ms / 1_000.0

            if time_dif < CHECK_PERIOD_S:
                heartbeat = deepcopy(self.data.heartbeat)
                self.data.heartbeat.timestamp_ms = 0
                return heartbeat
            time.sleep(CHECK_PERIOD_S)

        raise TimeoutError

    def wait_command_ack(self) -> CommandACK:
        """Wait for command execution status.

        Raises:
            `TimeoutError`: if the response time is exceeded.
        """
        return self.wait_message(CommandACK())

    def wait_message(self, message_obj: T) -> T:
        """Wait for next message.

        Parameters:
            message_obj: object of the message to wait for.

        Returns:
            T: requested message object.

        Raises:
            `TimeoutError`: if the response time is exceeded.
        """
        if not hasattr(self.data, message_obj.get_object_name()):
            raise AttributeError(
                f"UAVData has no attribute with class name {message_obj.__name__}"  # type: ignore
            )

        clock_start = time.time()
        while time.time() - clock_start < TIMEOUT_S:
            msg: MavMessage = getattr(self.data, message_obj.get_object_name())
            time_since_last_message = time.time() - msg.timestamp_ms / 1_000.0

            if time_since_last_message < CHECK_PERIOD_S:
                coppied_msg = deepcopy(msg)
                msg.timestamp_ms = 0
                setattr(self, message_obj.get_object_name(), msg)
                return coppied_msg  # type: ignore
            time.sleep(CHECK_PERIOD_S)

        raise TimeoutError

    def arm(self) -> bool:
        """Arms motors."""
        msg = get_command_long_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            command=MAV_CMD_COMPONENT_ARM_DISARM,
            param1=1,
        )

        self._driver.send(msg)
        logger.info("Arm command sent.")
        self.wait_heartbeat()

        return self.is_armed()

    def disarm(self) -> bool:
        """Disarms motors."""
        msg = get_command_long_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            command=MAV_CMD_COMPONENT_ARM_DISARM,
            param1=0,
        )

        self._driver.send(msg)
        logger.info("Disarm command sent.")

        if self.wait_command_ack().result != CommandResult.ACCEPTED:
            return False
        return True

    def set_servo(self, instance_number: int, pwm: int) -> bool:
        """Set a servo to a desired `PWM` value.

        Parameters:
            instance_number: servo number.
            pwm: `PWM` value to set.
        """
        msg = get_command_long_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            command=MAV_CMD_DO_SET_SERVO,
            param1=instance_number,
            param2=pwm,
        )

        self._driver.send(msg)
        logger.info("Set servo command sent.")

        if self.wait_command_ack().result != CommandResult.ACCEPTED:
            return False
        return True

    def fly_to_gps_position(self, lat_int: int, lon_int: int, alt_m: float) -> bool:
        """Reposition the vehicle to a specific WGS84 global position.

        Parameters:
            lat_int: Latitude of the target point.
            lon_int: Longitude of the target point.
            alt_m: Altitude of the target point in meters.

        Works only in `Guided` mode.
        """
        msg = get_command_int_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            command=MAV_CMD_DO_REPOSITION,
            x=lat_int,
            y=lon_int,
            z=alt_m,
        )

        self._driver.send(msg)
        logger.info("Flight to point command sent.")

        if self.wait_command_ack().result != CommandResult.ACCEPTED:
            return False
        return True

    def get_corrected_position(self) -> PositionGPS:
        """Get the vehicle position corrected for the distance
        the vehicle traveled after the message was received.
        """
        movement_time = time.time() - self.data.global_position_int.timestamp_ms / 1000
        north_shift = movement_time * self.data.global_position_int.vx / 100
        east_shift = movement_time * self.data.global_position_int.vy / 100
        z_shift = movement_time * self.data.global_position_int.vz / 100
        corrected_altitude = z_shift + self.data.global_position_int.relative_alt / 1000
        last_known_position = PositionGPS(
            self.data.global_position_int.lat,
            self.data.global_position_int.lon,
        )
        shift_vector = PositionNED(north_shift, east_shift, corrected_altitude)
        return ned2geo(last_known_position, shift_vector)

    def fetch_one_param(self, param_id: str) -> ParamValue:
        """Fetch single parameter from UAV

        Parameters:
            param_id: string that identifies the parameter.
        """
        msg = get_param_request_read_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            param_id=param_id.encode("ascii"),
            param_index=-1,
        )

        self._driver.send(msg)
        logger.debug("Param request read message sent.")
        return self.wait_message(ParamValue())

    def request_all_parameters(self) -> None:
        """Send a command to request values of every parameter from the uav.
        If you need specific parameters, you should use request_one_parameter instead
        """
        msg = get_param_request_list_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
        )

        self._driver.send(msg)
        logger.debug("Param request list message sent.")

    def set_parameter(self, param_id: str, new_value: float) -> bool:
        """Set a parameter to the specified value.

        Parameters:
            param_id: string that identifies the parameter.
            new_value: new parameter value.
        """
        msg = get_param_set_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            param_id=param_id.encode("ascii"),
            param_value=new_value,
        )

        self._driver.send(msg)
        logger.debug("Param set message sent.")
        return abs(self.wait_message(ParamValue()).param_value - new_value) < 0.0001

    def request_data_stream(self, stream_id: int, message_rate_hz: int) -> None:
        """Request a messages stream.

        Parameters:
            stream_id: ID of the requested data stream,
            message_rate_hz: requested message rate in Hz,
        """
        msg = MAVLink_request_data_stream_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            req_stream_id=stream_id,
            req_message_rate=message_rate_hz,
            start_stop=1,
        )
        logger.debug("Data stream requested.")
        self._driver.send(msg)

    def request_message(self, message_id: int) -> CommandResult:
        """Request single message from UAV.
        Message will be send to requester address.

        Parameters:
            message_id: ID of requested message.
        """
        msg = get_command_long_message(
            self._uav_addr.system_id,
            self._uav_addr.component_id,
            MAV_CMD_REQUEST_MESSAGE,
            param1=message_id,
            param7=1,
        )

        self._driver.send(msg)
        logger.debug("Message requested.")
        return self.wait_command_ack().result

    def fetch_home_position(self) -> PositionGPS:
        """Fetch home location"""
        if self.request_message(MAVLINK_MSG_ID_HOME_POSITION) != CommandResult.ACCEPTED:
            raise RuntimeError

        response = self.wait_message(HomePosition())
        return PositionGPS(response.latitude, response.longitude, response.altitude)

    def send_raw_mavlink_message(self, msg: MAVLink_message) -> None:
        """Send raw MAVLink message.

        Parameters:
            msg: raw MAVLink messae to send.
        """
        self._driver.send(msg)

    def send_encapsulated_data(self, data: bytes, seq: int = 0) -> None:
        """Send encapsulated data to boradcast.

        Parameters:
            data: data bytes.
            seq: sequence number (starting with 0 on every transmission).
        """

        data_size_bytes = len(data)
        if data_size_bytes > MAX_DATA_SIZE_BYTES:
            raise ValueError(f"Max allowed data size is {MAX_DATA_SIZE_BYTES}")

        bytes_to_send = bytes([data_size_bytes])
        bytes_to_send += data
        bytes_to_send += bytes([0x42]) * (MAX_DATA_SIZE_BYTES - data_size_bytes)
        msg = MAVLink_encapsulated_data_message(seq, bytes_to_send)

        logger.debug("Encapsulated data message sent.")
        self._driver.send(msg)

    def wait_encapsulated_data(
        self, timeout_s: Optional[float] = None
    ) -> EncapsulatedData:
        """Wait for next encapsulated data."""

        return self.data.encapsulated_data.get(timeout=timeout_s)

    def fetch_wp_dist(self) -> int:
        """Fetch distance to the next waypoint.

        Returns:
            distance to next waypoint in meters.

        Raises:
            `TimeoutError`: if the response time is exceeded.
        """
        return self.wait_message(NavControllerOutput()).wp_dist
