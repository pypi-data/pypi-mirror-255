import logging
from typing import Optional

from pymavlink.dialects.v20.ardupilotmega import (
    MAV_CMD_DO_SET_MODE,
    MAV_CMD_NAV_LAND,
    MAV_CMD_NAV_TAKEOFF,
    MAVLINK_MSG_ID_POSITION_TARGET_LOCAL_NED,
)

from albatros.enums import CommandResult, ConnectionType, CopterFlightModes, MavFrame
from albatros.telem import ComponentAddress
from albatros.telem.message_models import PositionTargetLocalNED
from albatros.uav import UAV

from .outgoing.commands import (
    get_command_long_message,
    get_set_position_target_local_ned_message,
)

logger = logging.getLogger(__name__)


class Copter(UAV):
    """Provides copter specific actions."""

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
        self.set_parameter("FENCE_ENABLE", 1)

    def set_mode(self, mode: CopterFlightModes) -> bool:
        """Set system mode.

        Parameters:
            mode: ardupilot flight mode you want to set.

        Returns:
            `True` if command was accepted

        Raises:
            `TimeoutError`: if the response time is exceeded.
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

    def takeoff(self, alt_m: float, yaw: float = float("NaN")) -> bool:
        """Takeoff copter. Set `GUIDED` mode and send takeoff command.

        Parameters:
            alt_m: The altitude to which the Copter is to ascend
            yaw: Yaw angle (if magnetometer present), ignored without magnetometer.
                NaN to use the current system yaw heading mode (e.g. yaw towards next waypoint,
                yaw to home, etc.).

        Returns:
            `True` if command was accepted

        Raises:
            `TimeoutError`: if the response time is exceeded.
        """
        self.set_parameter("FENCE_ENABLE", 0)

        if not self.set_mode(CopterFlightModes.GUIDED):
            logger.error("Unable to set GUIDED mode, aborting")
            return False

        msg = get_command_long_message(
            self._uav_addr.system_id,
            self._uav_addr.component_id,
            MAV_CMD_NAV_TAKEOFF,
            param4=yaw,
            param7=alt_m,
        )

        self._driver.send(msg)
        logger.info("Takeoff command sent")

        if self.wait_command_ack().result != CommandResult.ACCEPTED:
            return False
        return True

    def land(self) -> bool:
        """Land copter in the place where it is currently located. Works only in `GUIDED` mode.

        Returns:
            `True` if command was accepted

        Raises:
            `TimeoutError`: if the response time is exceeded.
        """

        msg = get_command_long_message(
            self._uav_addr.system_id,
            self._uav_addr.component_id,
            MAV_CMD_NAV_LAND,
        )

        self._driver.send(msg)
        logger.info("Land command sent")

        if self.wait_command_ack().result != CommandResult.ACCEPTED:
            return False
        return True

    def fly_to_local_position(
        self,
        north_m: float,
        east_m: float,
        alt_m: float,
        yaw_rad: float = 0,
        yaw_rate_rad: float = 0,
    ) -> bool:
        """Move copter to the NED location relative to origin of the coordinate system.

        Works only in `GUIDED` mode.

        Parameters:
            north_m: meters to the north,
            east_m: meters to the east,
            alt_m: altitude in meters relative to start point.
            yaw_rad: yaw setpoint (rad)
            yaw_rate_rad: yaw rate setpoint (rad/s)

        Returns:
            `True` if command was accepted

        Raises:
            `TimeoutError`: if the response time is exceeded.
        """

        msg = get_set_position_target_local_ned_message(
            self._uav_addr.system_id,
            self._uav_addr.component_id,
            north_m,
            east_m,
            alt_m,
            yaw_rad,
            yaw_rate_rad,
            MavFrame.LOCAL_NED,
        )

        self._driver.send(msg)
        logger.info("Flight to point command sent.")

        if (
            self.request_message(MAVLINK_MSG_ID_POSITION_TARGET_LOCAL_NED)
            != CommandResult.ACCEPTED
        ):
            return False

        try:
            target = self.wait_message(PositionTargetLocalNED())
            if target.x == north_m and target.y == east_m:
                return True
            return False

        except TimeoutError:
            return False

    def fly_to_local_offset_position(
        self,
        north_m: float,
        east_m: float,
        relative_alt_m: float,
        yaw_rad: float = 0,
        yaw_rate_rad: float = 0,
    ) -> bool:
        """Move copter to the NED location relative to the current position.

        Works only in `GUIDED` mode.

        Parameters:
            north_m: meters to the north,
            east_m: meters to the east,
            relative_alt_m: altitude in meters relative to current altitude.
            yaw_rad: yaw setpoint (rad)
            yaw_rate_rad: yaw rate setpoint (rad/s)

        Returns:
            `True` if command was accepted

        Raises:
            `TimeoutError`: if the response time is exceeded.
        """

        msg = get_set_position_target_local_ned_message(
            self._uav_addr.system_id,
            self._uav_addr.component_id,
            north_m,
            east_m,
            relative_alt_m,
            yaw_rad,
            yaw_rate_rad,
            MavFrame.LOCAL_OFFSET_NED,
        )

        self._driver.send(msg)
        logger.info("Flight to point command sent.")

        if (
            self.request_message(MAVLINK_MSG_ID_POSITION_TARGET_LOCAL_NED)
            != CommandResult.ACCEPTED
        ):
            return False

        try:
            target = self.wait_message(PositionTargetLocalNED())
            if target.x == north_m and target.y == east_m:
                return True
            return False

        except TimeoutError:
            return False
