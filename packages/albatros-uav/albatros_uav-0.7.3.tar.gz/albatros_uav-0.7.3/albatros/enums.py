from enum import Enum


class ConnectionType(Enum):
    DIRECT = 1
    REDIS = 2
    TEST = 3


class PlaneFlightModes(Enum):
    """Available flight modes for the plane."""

    MANUAL = 0
    CIRCLE = 1
    STABILIZE = 2
    TRAINING = 3
    ACRO = 4
    FBWA = 5
    FBWB = 6
    CRUISE = 7
    AUTOTUNE = 8
    AUTO = 10
    RTL = 11
    LOITER = 12
    TAKEOFF = 13
    AVOID_ADSB = 14
    GUIDED = 15
    QSTABILIZE = 17
    QHOVER = 18
    QLOITER = 19
    QLAND = 20
    QRTL = 21
    QAUTOTUNE = 22
    QACRO = 23


class CopterFlightModes(Enum):
    """Available flight modes for the copter."""

    STABILIZE = 0
    ACRO = 1
    ALT_HOLD = 2
    AUTO = 3
    GUIDED = 4
    LOITER = 5
    RTL = 6
    CIRCLE = 7
    LAND = 9
    DRIFT = 11
    FLIP = 14
    AUTOTUNE = 15
    POSHOLD = 16
    BRAKE = 17
    THROW = 18
    AVOID_ADSB = 19
    GUIDED_NOGPS = 20
    SMART_RTL = 21
    FLOWHOLD = 22
    ZIGZAG = 24


class MissionType(Enum):
    """Enumeration of MAVLink mission types."""

    MISSION = 0
    FENCE = 1
    RALLY = 2
    ALL = 255


class MavFrame(Enum):
    """Enumeration of coordinate frames used by MAVLink."""

    GLOBAL = 0  # doc: Global (WGS84) coordinate frame + MSL altitude.
    LOCAL_NED = 1  # doc: NED local tangent frame (x: North, y: East, z: Down) with origin fixed relative to earth.
    MISSION = 2  # doc: NOT a coordinate frame, indicates a mission command.
    GLOBAL_RELATIVE_ALT = 3  # doc: Global (WGS84) coordinate frame + altitude relative to the home position.
    LOCAL_ENU = 4  # doc: ENU local tangent frame (x: East, y: North, z: Up) with origin fixed relative to earth.
    GLOBAL_INT = 5  # doc: Global (WGS84) coordinate frame (scaled) + MSL altitude.
    GLOBAL_RELATIVE_ALT_INT = 6  # doc: Global (WGS84) coordinate frame (scaled) + altitude relative to the home position.
    LOCAL_OFFSET_NED = 7  # doc: NED local tangent frame (x: North, y: East, z: Down) with origin that travels with the vehicle.
    GLOBAL_TERRAIN_ALT = 10  # doc: Global (WGS84) coordinate frame with AGL altitude (at the waypoint coordinate).
    GLOBAL_TERRAIN_ALT_INT = 11  # doc: Global (WGS84) coordinate frame (scaled) with AGL altitude (at the waypoint coordinate).
    BODY_FRD = 12  # doc: FRD local frame aligned to the vehicle's attitude (x: Forward, y: Right, z: Down) with an origin that travels with the vehicle.
    LOCAL_FRD = 20  # doc: FRD local tangent frame (x: Forward, y: Right, z: Down) with origin fixed relative to earth.
    LOCAL_FLU = 21  # doc: FLU local tangent frame (x: Forward, y: Left, z: Up) with origin fixed relative to earth.


class MissionResult(Enum):
    """Enumeration of mission results in a MISSION_ACK message."""

    ACCEPTED = 0
    ERROR = 1
    UNSUPPORTED_FRAME = 2
    UNSUPPORTED = 3
    NO_SPACE = 4
    INVALID = 5
    INVALID_PARAM1 = 6
    INVALID_PARAM2 = 7
    INVALID_PARAM3 = 8
    INVALID_PARAM4 = 9
    INVALID_PARAM5_X = 10
    INVALID_PARAM6_Y = 11
    INVALID_PARAM7 = 12
    INVALID_SEQUENCE = 13
    DENIED = 14
    OPERATION_CANCELLED = 15
    NOT_RECEIVED = 16


class CommandResult(Enum):
    """
    Command execution result.
    """

    ACCEPTED = 0
    TEMPORARILY_REJECTED = 1
    DENIED = 2
    UNSUPPORTED = 3
    FAILED = 4
    IN_PROGRESS = 5
    CANCELLED = 6
    COMMAND_LONG_ONLY = 7
    COMMAND_INT_ONLY = 8
    COMMAND_UNSUPPORTED_MAV_FRAME = 9
    NOT_RECEIVED = 10
