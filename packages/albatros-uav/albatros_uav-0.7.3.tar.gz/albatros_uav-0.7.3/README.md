# Albatros UAV

A python library that provides high-level functions for UAVs based on MAVLink. It allows to easily handle communication with the flight controller to create friendly mission management systems. Albatros supports direct communication with UAVs as well as via Redis (WIP)

### Supported functionalities

*Plane:*

- arming vehicle,
- setting flight mode,
- setting servos positions,
- flying in `GUIDED` mode,
- uploading mission and flying in `AUTO` mode,
- param protocol.

*Copter:*

- arming vehicle,
- setting flight mode,
- setting servos positions,
- flying in `GUIDED` mode,
- param protocol,
- __comming soon:__ uploading mission and flying in `AUTO` mode.

*Access to UAV telemetry via `UAV.data`*

### Supported MAVLink telemetry messages

- `Attitude`
- `GlobalPositionInt`
- `GPSRawInt`
- `GPSStatus`
- `Heartbeat`
- `CommandACK`
- `MissionACK`
- `MissionRequestInt`
- `RadioStatus`
- `RcChannelsRaw`
- `ServoOutputRaw`
- `SysStatus`
- `MissionItemReached`
- `ParamValue`
- `PositionTargetLocalNED`
- `HomePosition`
- `LocalPositionNED`
- `NavControllerOutput`

## Examples

### Creating connection
```python
from albatros import Plane, ConnectionType
from albatros.telem import ComponentAddress

# SITL connection is default
plane = Plane() 

# Direct connection to the flight controller
plane = Plane(device="/dev/tty/USB0/", baud_rate=57600)

# You can also specify the ID of the vehicle you want to connect to and the ID of your system
# read more about MAVLink Routing in ArduPilot: https://ardupilot.org/dev/docs/mavlink-routing-in-ardupilot.html
plane_addr = ComponentAddress(system_id=1, component_id=1)
gcs_addr = ComponentAddress(system_id=255, component_id=1)
plane = Plane(uav_addr=plane_addr, my_addr=gcs_addr)
```

### Arming vehicle (SITL simulation)

```bash
$ python -m examples.arming_vehicle
```

```python
from albatros import UAV

vehicle = UAV()

while not vehicle.arm():
    print("Waiting vehicle to arm")
print("Vehicle armed")

if not vehicle.disarm():
    print("Disarm vehicle failed")
print("Vehicle disarmed")
```
