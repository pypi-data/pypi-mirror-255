# spymarine

A library for spying on Simarine devices and their sensor values using asyncio and Python

Based on the fantastic reverse engineering work of https://github.com/htool/pico2signalk

Only tested with Simarine Pico rev2

## Getting Started

Run the following code on the same network that the Simarine device is connected to:

```python
import spymarine

# Print all devices and their latest sensor values every second
async with spymarine.DeviceReader() as reader:
    while True:
        await reader.read_sensors()
        print(reader.devices)
        await asyncio.sleep(1)
```

## Author

Christopher Strack
