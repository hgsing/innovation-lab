import threading
try:
    import tomllib as tomli  # type: ignore
except ModuleNotFoundError:
    import tomli

from .information_provider import InformationProvider, RaspberryPiRelayInformationProvider, create_device


def update():
    for device in devices.values():
        device.periodic_update()
    repeat = threading.Timer(0.25, update)
    repeat.name = "Periodic Update"
    repeat.start()


# Control Panel : Reconnect
def connect_devices():
    for name, device in devices.items():
        threading.Thread(
            target=device.full_initialize, daemon=True, name=f"connect-{name}"
        ).start()


# Control Panel: Enable Logging
def enable_logging():
    for device in devices.values():
        device.enable_logging()


# Control Panel: Disable Logging
def disable_logging():
    for device in devices.values():
        device.disable_logging()


# Initialization Code
config_file = "config.toml"

with open(config_file, mode="rb") as fp:
    config = tomli.load(fp)

devices: dict[str, InformationProvider] = {
    d['id']: create_device(d, config) for d in config['devices']
}

PLC = devices.get("skill-boss-logistics")
if PLC:
    skill_boss: RaspberryPiRelayInformationProvider = PLC
else:
    raise RuntimeWarning("No PLC device. Check config file.")

connect_devices()

timer = threading.Timer(2, update)
timer.daemon = True
timer.start()

fault_file = "faults.toml"
