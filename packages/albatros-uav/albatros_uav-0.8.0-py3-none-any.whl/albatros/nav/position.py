"""Module containing functions related to position processing."""

import math
from dataclasses import dataclass, field


@dataclass
class PositionNED:
    """Dataclass for NED position format.

    Parameters:
        north: Meters from reference point in north direction
        east: Meters from reference point in east direction
        down: Meters from reference point in down
    """

    north: float = 0.0
    east: float = 0.0
    down: float = 0.0


@dataclass
class PositionGPS:
    """Dataclass for scaled position in WGS84 format.

    Parameters:
        lat: Latitude (deg)
        lon: Longitude (deg)
        alt_m: Altitude (m)
        lat_int: Latitude (degE7)
        lon_int: Longitude (degE7)
    """

    lat: float
    lon: float
    alt_m: float = 0.0
    lat_int: int = field(init=False)
    lon_int: int = field(init=False)

    def __post_init__(self) -> None:
        self.scale_global_position()

    def __hash__(self) -> int:
        return hash((self.lat_int, self.lon_int, self.alt_m))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PositionGPS):
            raise NotImplementedError
        return (self.lat_int, self.lon_int, self.alt_m) == (
            other.lat_int,
            other.lon_int,
            other.alt_m,
        )

    @classmethod
    def from_int(cls, lat: int, lon: int, alt_mm: int = 0) -> "PositionGPS":
        """Create ``PositionGPS`` from ``int`` position."""
        pos = cls(lat / 1.0e7, lon / 1.0e7, alt_mm / 1.0e3)
        pos.lat_int = lat
        pos.lon_int = lon
        return pos

    def get_global_position(self) -> tuple[float, float, float]:
        """Get position in WGS84 format."""
        return (self.lat, self.lon, self.alt_m)

    def scale_global_position(self) -> None:
        """Scale WGS84 position format to the integer position and store it."""

        self.lat_int = int(self.lat * 1.0e7)
        self.lon_int = int(self.lon * 1.0e7)

    def distance_to_point(self, point: "PositionGPS") -> float:
        """Calculate distance to the GPS points using the haversine formula.

        Parameters:
            point: GPS position.

        Return:
            The distance between the two points in meters.
        """
        # Convert latitude and longitude from degrees to radians
        lat1 = math.radians(self.lat)
        lon1 = math.radians(self.lon)
        lat2 = math.radians(point.lat)
        lon2 = math.radians(point.lon)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6378137 * c


def ned2geo(reference_point: PositionGPS, point: PositionNED) -> PositionGPS:
    """Convert GEO to NED coordinates.

    Parameters:
        reference_point: reference point (origin of the coordinate system)
        point: NED point to be converted to GEO

    Return:
        GEO coordinate of point
    """
    lat = (point.north / (40075704.0 / 360)) + reference_point.lat
    lon = (
        point.east / (math.cos(math.radians(reference_point.lat)) * (40075704.0 / 360))
    ) + reference_point.lon
    return PositionGPS(lat, lon, point.down)
