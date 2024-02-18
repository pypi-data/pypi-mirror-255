import logging
import time
from typing import Optional

from pymavlink.dialects.v20.ardupilotmega import (
    MAV_CMD_DO_SET_MODE,
    MAV_CMD_NAV_LOITER_TIME,
    MAV_CMD_NAV_LOITER_UNLIM,
    MAV_CMD_NAV_RETURN_TO_LAUNCH,
    MAV_CMD_NAV_TAKEOFF,
    MAV_CMD_NAV_WAYPOINT,
)

from albatros.enums import ConnectionType
from albatros.telem import ComponentAddress

from .enums import CommandResult, MissionResult, PlaneFlightModes
from .outgoing.commands import (
    get_command_long_message,
    get_mission_clear_message,
    get_mission_count_message,
    get_mission_item_int,
)
from .telem.message_models import MissionACK
from .uav import UAV

logger = logging.getLogger(__name__)


class Plane(UAV):
    """Class that provides actions the plane can perform."""

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
        super().__init__(
            uav_addr,
            my_addr,
            connection_type,
            device,
            baud_rate,
            host,
            port,
        )
        self._mission_count = 0

    def set_mode(self, mode: PlaneFlightModes) -> bool:
        """Set system mode.

        Parameters:
            mode: ardupilot flight mode you want to set.
        """
        msg = get_command_long_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            command=MAV_CMD_DO_SET_MODE,
            param1=1,
            param2=mode.value,
        )

        self._driver.send(msg)
        logger.info("Set mode command sent")

        if self.wait_command_ack().result != CommandResult.ACCEPTED:
            return False
        return True

    def wait_next_mission_item_id(self) -> int:
        """Wait for a message requesting the next mission item.

        :returns: ID of next mission item.
        """
        clock_start = time.time()
        while True:
            time_dif = time.time() * 1000 - self.data.mission_request_int.timestamp_ms
            if time_dif < 100:
                self.data.mission_request_int.timestamp_ms = 0
                return self.data.mission_request_int.seq
            time.sleep(0.1)
            if time.time() - clock_start > 0.250:
                raise TimeoutError

    def get_mission_ack(self) -> MissionACK:
        """Get uploaded mission status code.

        :returns: MisionACK object containing a status code.
        """
        clock_start = time.time()
        while True:
            time_dif = time.time() * 1000 - self.data.mission_ack.timestamp_ms
            if time_dif < 100:
                self.data.mission_ack.timestamp_ms = 0
                return self.data.mission_ack
            time.sleep(0.1)
            if time.time() - clock_start > 0.250:
                raise TimeoutError

    def send_mission_takeoff_item(
        self,
        pitch: float,
        altitude: float,
        yaw: float = float("NaN"),
    ) -> None:
        """Send takeoff item.

        Parameters:
            pitch: Minimum pitch (if airspeed sensor present), desired pitch without sensor.
            yaw: Yaw angle (if magnetometer present), ignored without magnetometer.
                NaN to use the current system yaw heading mode (e.g. yaw towards next waypoint, yaw to home, etc.).
            altitude: target altitude in meters
        """
        seq = self.wait_next_mission_item_id()

        msg = get_mission_item_int(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            seq=seq,
            command=MAV_CMD_NAV_TAKEOFF,
            param1=pitch,
            param4=yaw,
            z=altitude,
        )

        self._driver.send(msg)
        logger.info("mission_takeoff message sent.")

    def send_mission_count(self, mission_elements_count: int) -> None:
        """Send the number of items in a mission. This is used to initiate mission upload.

        Parameters:
            mission_elements_count: Number of mission items in the sequence.
        """
        msg = get_mission_count_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            count=mission_elements_count + 1,
        )

        self._driver.send(msg)
        logger.info("mission_count message sent.")

        self.send_mission_waypoint_item(0, 0, 0, 0)
        self._mission_count = mission_elements_count

    def clear_mission(self) -> bool:
        """Clear the previously uploaded mission."""
        msg = get_mission_clear_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
        )

        self._driver.send(msg)
        logger.info("mission_clear_all message sent.")

        try:
            if self.get_mission_ack().type == MissionResult.ACCEPTED:
                self._mission_count = 0
                return True
            return False
        except TimeoutError:
            return False

    def send_mission_waypoint_item(
        self,
        lat_int: int,
        lon_int: int,
        alt_m: float,
        accept_radius_m: float,
        hold_time_s: float = 0,
        pass_radius_m: float = 0,
        yaw_deg: float = 0,
    ) -> None:
        """Send a mission waypoint to navigate to.

        Parameters:
            lat_int: Latitude of the waypoint.
            lon_int: Longitude of the waypoint.
            alt_m: Altitude of the waypoint in meters.
            accept_radius_m: Acceptance radius. If the sphere with this radius is hit, the waypoint counts as reached.
            hold_time_s: Hold time at the waypoint in seconds. Ignored by fixed-wing vehicles. Defaults to 0.
            pass_radius_m: Pass radius. If > 0, it specifies the radius to pass by the waypoint.
                Allows trajectory control. Positive value for clockwise orbit, negative value for counterclockwise orbit. Defaults to 0.
            yaw_deg: Desired yaw angle at the waypoint for rotary-wing vehicles.
                Set to NaN to use the current system yaw heading mode. Defaults to None.
        """
        seq = self.wait_next_mission_item_id()

        msg = get_mission_item_int(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            seq=seq,
            command=MAV_CMD_NAV_WAYPOINT,
            param1=hold_time_s,
            param2=accept_radius_m,
            param3=pass_radius_m,
            param4=yaw_deg,
            x=lat_int,
            y=lon_int,
            z=alt_m,
        )

        self._driver.send(msg)
        logger.info("mission_waypoint message sent.")

    def send_mission_loiter_unlim_item(
        self,
        lat_int: int,
        lon_int: int,
        alt_m: float,
        radius_m: float,
        yaw_deg: float = 0,
    ) -> None:
        """Loiter around this waypoint an unlimited amount of time

        Parameters:
            lat_int: Latitude.
            lon_int: Longitude.
            alt_m: Altitude in meters.
            radius_m: Loiter radius around waypoint for forward-only moving vehicles (not multicopters).
                If positive loiter clockwise, else counter-clockwise
            yaw_deg: Desired yaw angle at the waypoint for rotary-wing vehicles.
                Set to NaN to use the current system yaw heading mode. Defaults to None.
        """
        seq = self.wait_next_mission_item_id()

        msg = get_mission_item_int(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            seq=seq,
            command=MAV_CMD_NAV_LOITER_UNLIM,
            param3=radius_m,
            param4=yaw_deg,
            x=lat_int,
            y=lon_int,
            z=alt_m,
        )

        self._driver.send(msg)
        logger.info("mission_loiter_unlim message sent.")

    def send_mission_loiter_time_item(
        self,
        time_s: float,
        lat_int: int,
        lon_int: int,
        alt_m: float,
        radius_m: float,
        straight_to_wp: bool = True,
    ) -> None:
        """Loiter around this waypoint an unlimited amount of time

        Parameters:
            time_s: Loiter time in seconds.
            lat_int: Latitude.
            lon_int: Longitude.
            alt_m: Altitude in meters.
            radius_m: Loiter radius around waypoint for forward-only moving vehicles (not multicopters).
                If positive loiter clockwise, else counter-clockwise.
            straight_to_wp: Quit the loiter while on the straight to the next waypoint.
        """
        seq = self.wait_next_mission_item_id()

        msg = get_mission_item_int(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            seq=seq,
            command=MAV_CMD_NAV_LOITER_TIME,
            param1=time_s,
            param2=0,
            param3=radius_m,
            param4=straight_to_wp,
            x=lat_int,
            y=lon_int,
            z=alt_m,
        )

        self._driver.send(msg)
        logger.info("mission_loiter_time message sent.")

    def send_mission_rtl_item(self) -> None:
        """Send a mission return to launch location."""
        seq = self.wait_next_mission_item_id()

        msg = get_mission_item_int(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            seq=seq,
            command=MAV_CMD_NAV_RETURN_TO_LAUNCH,
        )

        self._driver.send(msg)
        logger.info("mission_rtl message sent.")

    def wait_mission_item_reached(self, mission_item_no: int) -> None:
        """Wait till designated waypoint is reached.

        Parameters:
            mission_item_no: number of mission item to wait until it's reached (numbering starts from '1')
        """
        if mission_item_no > self._mission_count or mission_item_no < 1:
            raise ValueError("Incorrect mission item number")

        while self.data.mission_item_reached.seq != mission_item_no:
            time.sleep(1)
