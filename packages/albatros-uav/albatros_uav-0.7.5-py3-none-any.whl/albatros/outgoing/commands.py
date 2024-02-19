from pymavlink.dialects.v20.ardupilotmega import (
    MAVLink_command_int_message,
    MAVLink_command_long_message,
    MAVLink_mission_clear_all_message,
    MAVLink_mission_count_message,
    MAVLink_mission_item_int_message,
    MAVLink_set_position_target_local_ned_message,
)

from albatros.enums import MavFrame, MissionType


def get_command_long_message(
    target_system: int,
    target_component: int,
    command: int,
    confirmation: int = 0,
    param1: float = 0,
    param2: float = 0,
    param3: float = 0,
    param4: float = 0,
    param5: float = 0,
    param6: float = 0,
    param7: float = 0,
) -> MAVLink_command_long_message:
    """MAVLink command long message wraper.

    :param target_system: message target system id
    :param target_component: message target component id
    :param command: command number
    :param confirmation: Defaults to 0.
    :param param1: Defaults to 0.
    :param param2: Defaults to 0.
    :param param3: Defaults to 0.
    :param param4: Defaults to 0.
    :param param5: Defaults to 0.
    :param param6: Defaults to 0.
    :param param7: Defaults to 0.

    :returns: MAVLink_command_long_message: message object
    """
    return MAVLink_command_long_message(
        target_system,
        target_component,
        command,
        confirmation,
        param1,
        param2,
        param3,
        param4,
        param5,
        param6,
        param7,
    )


def get_command_int_message(
    target_system: int,
    target_component: int,
    command: int,
    x: int = 0,  # pylint: disable=invalid-name
    y: int = 0,  # pylint: disable=invalid-name
    z: float = float("NaN"),  # pylint: disable=invalid-name
    frame: MavFrame = MavFrame.GLOBAL_RELATIVE_ALT,
    current: int = 0,
    autocontinue: int = 0,
    param1: float = 0,
    param2: float = 0,
    param3: float = 0,
    param4: float = 0,
) -> MAVLink_command_int_message:
    """MAVLink command int message wraper.

    :param target_system: message target system id
    :param target_component: message target component id
    :param command: command number
    :param x: local: x position in meters * 1e4, global: latitude in degrees * 10^7
    :param y: local: y position in meters * 1e4, global: longitude in degrees * 10^7
    :param z: z position: global: altitude in meters (relative or absolute, depending on frame).
    :param frame: The coordinate system of the COMMAND. Defaults GLOBAL_RELATIVE_ALT_INT.
    :param current: Not used.
    :param autocontinue: Not used.
    :param param1: Defaults to 0.
    :param param2: Defaults to 0.
    :param param3: Defaults to 0.
    :param param4: Defaults to 0.

    :returns: MAVLink_command_int_message: message object
    """
    return MAVLink_command_int_message(
        target_system,
        target_component,
        frame.value,
        command,
        current,
        autocontinue,
        param1,
        param2,
        param3,
        param4,
        x,
        y,
        z,
    )


def get_mission_count_message(
    target_system: int,
    target_component: int,
    count: int,
    mission_type: MissionType = MissionType.MISSION,
) -> MAVLink_mission_count_message:
    """MAVLink mission count message wraper.

    :param target_system: message target system id,
    :param target_component: message target component id,
    :param count: Number of mission items in the sequence,
    :param mission_type: Mission type.

    :returns: MAVLink_mission_count_message: message object
    """
    return MAVLink_mission_count_message(
        target_system, target_component, count, mission_type.value
    )


def get_mission_item_int(
    target_system: int,
    target_component: int,
    seq: int,
    command: int,
    param1: float = 0,
    param2: float = 0,
    param3: float = 0,
    param4: float = 0,
    x: int = 0,
    y: int = 0,
    z: float = 0,
    current: int = 0,
    autocontinue: int = 1,
    frame: MavFrame = MavFrame.GLOBAL_RELATIVE_ALT,
    mission_type: MissionType = MissionType.MISSION,
) -> MAVLink_mission_item_int_message:
    """MAVLink mission item int message wraper.

    :param target_system: System ID.
    :param target_component: Component ID.
    :param seq: Waypoint ID (sequence number). Starts at zero. Increases monotonically for each waypoint, no gaps in the sequence (0, 1, 2, 3, 4).
    :param frame: The coordinate system of the waypoint (MAV_FRAME).
    :param command: The scheduled action for the waypoint (MAV_CMD).
    :param current: Indicates if this waypoint is the current one in the mission (false: 0, true: 1).
    :param autocontinue: Indicates whether to autocontinue to the next waypoint (0: false, 1: true). Set false to pause the mission after the item completes.
    :param param1: PARAM1,
    :param param2: PARAM2,
    :param param3: PARAM3,
    :param param4: PARAM4,
    :param x: PARAM5 / local: x position in meters * 1e4, global: latitude in degrees * 10^7,
    :param y: PARAM6 / y position: local: x position in meters * 1e4, global: longitude in degrees * 10^7,
    :param z: PARAM7 / z position: global: altitude in meters (relative or absolute, depending on the frame).
    :param mission_type: Mission type (TYPE).

    :returns: MAVLink_command_int_message: message object
    """
    return MAVLink_mission_item_int_message(
        target_system,
        target_component,
        seq,
        frame.value,
        command,
        current,
        autocontinue,
        param1,
        param2,
        param3,
        param4,
        x,
        y,
        z,
        mission_type.value,
    )


def get_mission_clear_message(
    target_system: int,
    target_component: int,
    mission_type: MissionType = MissionType.MISSION,
) -> MAVLink_mission_clear_all_message:
    """Delete all mission items at once.

    :param target_system: message target system id,
    :param target_component: message target component id,
    :param mission_type (MavMissionType): Mission type.

    :returns: MAVLink_mission_clear_all_message: message object
    """
    return MAVLink_mission_clear_all_message(
        target_system, target_component, mission_type.value
    )


def get_set_position_target_local_ned_message(
    target_system: int,
    target_component: int,
    north_m: float,
    east_m: float,
    alt_m: float,
    yaw_rad: float,
    yaw_rate: float,
    frame: MavFrame,
) -> MAVLink_set_position_target_local_ned_message:
    """Sets a desired vehicle position in a local north-east-down coordinate frame.
    Used by an external controller to command the vehicle (manual controller or other system).

    :param target_system: message target system id,
    :param target_component: message target component id,
    :param north_m: X Position in NED frame,
    :param east_m: Y Position in NED frame,
    :param alt_m: altitude in meters relative to start point,
    :param yaw_rad: yaw setpoint (rad),
    :param yaw_rate: yaw rate setpoint (rad/s),
    :param frame: coordinate frame,


    :returns: MAVLink_set_position_target_local_ned_message: message object
    """
    return MAVLink_set_position_target_local_ned_message(
        42,
        target_system,
        target_component,
        frame.value,
        int(0b010111111000),
        north_m,
        east_m,
        -alt_m,
        0,
        0,
        0,
        0,
        0,
        0,
        yaw_rad,
        yaw_rate,
    )
