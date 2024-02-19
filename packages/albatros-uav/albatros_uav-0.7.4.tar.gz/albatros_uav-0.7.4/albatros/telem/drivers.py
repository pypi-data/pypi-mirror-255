"""
UAV connection handling module.
"""

import logging
from abc import ABC, abstractmethod

from pymavlink import mavutil
from pymavlink.dialects.v20.ardupilotmega import MAVLink, MAVLink_message
from redis import Redis

from .models import ComponentAddress
from .receive_loop import DirectReceiveLoop
from .uav_data import UAVData

logger = logging.getLogger(__name__)


class TelemDriver(ABC):
    def __init__(self, my_addr: ComponentAddress, data: UAVData) -> None:
        self.data = data
        self.my_addr = my_addr
        self.mav = MAVLink(0, my_addr.system_id, my_addr.component_id)

    def _pack(self, message: MAVLink_message) -> bytes:
        packed_message: bytes = message.pack(self.mav)
        return packed_message

    @abstractmethod
    def make_connection(self) -> bool:
        pass

    @abstractmethod
    def send(self, message: MAVLink_message) -> None:
        pass


class DirectConnectionDriver(TelemDriver):
    """Telemetry driver for direct connection"""

    def __init__(
        self, my_addr: ComponentAddress, data: UAVData, device: str, baud_rate: int
    ) -> None:
        super().__init__(my_addr, data)
        self.direct_connection: mavutil.mavudp
        self.device = device
        self.baud_rate = baud_rate

    def make_connection(self) -> bool:
        """Create a direct data link to the UAV."""
        self.direct_connection = mavutil.mavlink_connection(
            self.device,
            self.baud_rate,
            self.my_addr.system_id,
            self.my_addr.component_id,
        )
        if self.direct_connection.wait_heartbeat(timeout=10):
            logger.info("heartbeat recived")

            # starts a thread that receives telemetry
            receive_telem_loop = DirectReceiveLoop(self.direct_connection, self.data)
            receive_telem_loop.start()
            return True
        return False

    def send(self, message: MAVLink_message) -> None:
        message._header.srcSystem = self.my_addr.system_id
        message._header.srcComponent = self.my_addr.component_id
        packed_message = self._pack(message)
        self.direct_connection.write(packed_message)


class RedisConnectionDriver(TelemDriver):
    """Telemetry driver for redis connection"""

    def __init__(
        self, my_addr: ComponentAddress, data: UAVData, host: str, port: int
    ) -> None:
        super().__init__(my_addr, data)
        self.redis_connection: Redis
        self.host = host
        self.port = port

    def make_connection(self) -> bool:
        """Create a connection to the UAV via Redis (Pub/Sub)."""
        self.redis_connection = Redis(self.host, self.port)
        return True

    def send(self, message: MAVLink_message) -> None:
        packed_message = self._pack(message)
        self.redis_connection.xadd("commands", {"commands": packed_message})


class TestDriver(TelemDriver):
    def __init__(self, my_addr: ComponentAddress, data: UAVData) -> None:
        super().__init__(my_addr, data)

    def make_connection(self) -> bool:
        return True

    def send(self, message: MAVLink_message) -> None:
        pass
