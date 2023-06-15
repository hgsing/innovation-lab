import csv
import json
import os
import socket
import struct
from abc import abstractmethod
from datetime import datetime

from pycomm3 import CommError, LogixDriver
from pycomm3.tag import Tag


class InformationProvider:
    """Abstract base class for retrieving and displaying device data"""

    data: dict
    """
    stores the most recent data for a device. keys should be datapoint names, and the value should be a
    dictionary representing different properties of the value. the 'value' property is mandatory for this and
    should contain the raw value. Examples of supplemental properties would be data-type and dimensionality.

    sample data dictionary:
    {
      "length" : {"value" : 3, "type" : "INT" },
      "color" : {"value" : "#FF0000", "type" : "COLOR"}
    }
    """

    def __init__(self, name: str, _id: str, ip: str, port: int):
        self.name = name
        self.id = _id
        self.ip = ip
        self.port = int(port)
        self.data = {}
        self.active_connection = False
        self.log = False
        self.init = False

    def __str__(self) -> str:
        return ", ".join([self.name, self.id, self.ip, str(self.port)])

    @abstractmethod
    def initialize_data(self) -> None:
        """functionality that should be run before getting data from a target device for the first time. example: figuring
        out what data needs to be gotten in the first place. After this method, 'data' should contain real or dummy data.
        """

    @abstractmethod
    def update_data(self) -> None:
        """
        refreshes the data with up-to-date information from the device.
        """

    @abstractmethod
    def connect(self) -> None:
        """Attempt to connect to the target device when this method is called."""

    @property
    @abstractmethod
    def connected(self) -> bool:
        """Returns true when the devices can send valid data"""

    def log_header(self):
        """logs a header row to the CSV file storing the data for this device over time"""
        writer = csv.writer(
            open(
                os.path.join("ecosystem", "logs", self.id + ".csv"),
                "a",
                newline="",
                encoding="utf-8",
            )
        )

        if not self.active_connection:
            writer.writerow(["Err no connection"])
            return

        row = ["Date"]
        for datapoint_key in self.data:
            row.append(datapoint_key)

        writer.writerow(row)

    def log_row(self):
        """logs a data row to the CSV file storing the data for this device over time"""
        if not self.active_connection:
            return

        now = datetime.now().strftime("%H:%M:%S %f")
        row = [now]

        for datapoint in self.data.values():
            row.append(datapoint["value"])
        writer = csv.writer(
            open(
                os.path.join("ecosystem", "logs", self.id + ".csv"),
                "a",
                newline="",
                encoding="utf-8",
            )
        )
        writer.writerow(row)

    def to_attr_dict(self) -> dict:
        """Display basic device attributes as a dictionary"""

        return {
            "name": self.name,
            "id": self.id,
            "ip": self.ip,
            "port": self.port,
            "connected": self.active_connection,
        }

    @staticmethod
    @abstractmethod
    def get_data_value_headings() -> dict:
        """
        Returns the format of datapoint values as a dictionary where keys are datapoint value keys and values are their
        display names. each key represents a datapoint, but how the information stored in the value dictionary is
        represented here. 
        For example, if a sample datapoint is "client_name" : {"value: "tim", "type" : "STRING", "dimension": (1,3)}, 
        this method should return {"value" : "Value", "type" : "Type", "dimension" : "Dimensionality"}
        """

    def enable_logging(self):
        """enables logging for this device"""
        self.log = True
        self.log_header()

    def disable_logging(self):
        """disables logging for this device"""
        self.log = False

    def full_initialize(self):
        """connects to device and initializes data"""
        self.connect()
        self.initialize_data()
        self.init = True

    def periodic_update(self):
        """refreshes data and logs if applicable"""
        if not self.init:
            return

        if self.active_connection:
            self.update_data()
        if self.active_connection and self.log:
            self.log_row()


class QuanserInformationProvider(InformationProvider):
    """Implementation class for interfacing with Quanser Devices"""

    client: socket.socket
    DOUBLE_BYTES = 8

    def __init__(
        self, name: str, _id: str, ip: str, port: int, _type: str, datapoints: list
    ):
        super().__init__(name, _id, ip, port)
        self.type = _type
        self.datapoints = datapoints

    def get_datapoints(self) -> list[str]:
        return self.datapoints

    def connect(self):
        if self.active_connection:
            return

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(3)

        try:
            client.connect((self.ip, int(self.port)))
            self.active_connection = True
        except OSError:
            self.active_connection = False

        self.client = client

    @property
    def connected(self) -> bool:
        return self.active_connection

    def initialize_data(self):
        datapoints = self.get_datapoints()
        bytestream: bytes = self.get_data()

        if not self.active_connection:
            return

        for i, datapoint in enumerate(datapoints):
            self.data[datapoint] = {
                "type": "DOUBLE",
                "value": struct.unpack_from("d", bytestream, i * 8)[0],
            }

    def get_data(self):
        if not self.active_connection:
            return b""

        datapoints = self.get_datapoints()

        try:
            bytestream = self.client.recv(
                len(datapoints) * QuanserInformationProvider.DOUBLE_BYTES
            )
            return bytestream
        except OSError:
            print('Quanser device "' + self.name + '" is not supplying data.')
            self.active_connection = False
            return b""

    def update_data(self):
        self.initialize_data()

    @staticmethod
    def get_data_value_headings():
        return {"type": "Type", "value": "Value"}


class AllenBradleyInformationProvider(InformationProvider):
    """Implementation class for interfacing with Allen Bradley PLCs directly (not via raspberry pi relay)"""

    plc: LogixDriver

    def connect(self):
        if self.active_connection:
            return

        try:
            plc = LogixDriver(self.ip)
            self.active_connection = plc.open()
            self.plc = plc
        except CommError:
            self.active_connection = False
            self.plc = None

    @property
    def connected(self) -> bool:
        return self.active_connection

    def initialize_data(self):
        if not self.active_connection:
            return
        raw_data: list[dict]

        try:
            raw_data = self.plc.get_tag_list()
        except CommError:
            self.active_connection = False
            return

        for tag in raw_data:
            if "external_access" not in tag:
                continue
            external_access = str(tag["external_access"])
            if "read" not in external_access.lower():
                continue
            self.data[tag["tag_name"]] = {
                "type": tag["data_type_name"],
                "dimension": tag["dim"],
                "access": tag["external_access"],
                "value": "unknown",
            }

    def update_data(self):
        values: list[Tag | str | None]

        if len(self.data.keys()) == 0:
            return

        try:
            values = list(self.plc.read(*self.data.keys()))
        except CommError:
            self.active_connection = False
            return

        for val in values:
            if isinstance(val, Tag):
                if val.error is not None:
                    self.data[val.tag]["value"] = None
                else:
                    self.data[val.tag]["value"] = str(val.value)

    @staticmethod
    def get_data_value_headings():
        return {
            "type": "Type",
            "dimension": "Dimension",
            "access": "Access",
            "value": "Value",
        }


class RaspberryPiRelayInformationProvider(InformationProvider):
    """Implementation class for interfacing with a raspberry PI server that communicates with PLCs"""

    client: socket.socket
    plc_online: bool = False

    def connect(self):
        if self.active_connection:
            return

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(2)

        try:
            self.client.connect((self.ip, self.port))
        except OSError:
            pass
        else:
            self.active_connection = True
            self.connect_to_plc()

    def connect_to_plc(self):
        if not self.active_connection or self.plc_online:
            return

        try:
            self.client.sendall("plc_status".encode())
            length = int(self.client.recv(8).decode("utf-8"))
            response = self.client.recv(length).decode("utf-8")

            if length and response == "plc_online":
                self.plc_online = True

        except OSError:
            pass

    @property
    def connected(self) -> bool:
        return self.active_connection and self.plc_online

    def disconnect(self):
        if self.active_connection:
            self.client.close()

        self.active_connection = False
        self.plc_online = False

    commands: dict[str, list[str]] = {
        "system_start": ["SystemStartPB 1 SystemStopPB 0 System_Pause 0"],
        "system_stop": ["SystemStartPB 0 SystemStopPB 1 System_Pause 0"],
        "system_pause": ["SystemStartPB 0 SystemStopPB 0 System_Pause 1"],
        "cycle_stop": ["CycleStopPB 1"],
        "master_speed": ["MasterSpdSetting"],
        "induction_roller_on": [
            "InductionRoller1_ManRunPB 1",
            "InductionRoller1_ManStopPB 0",
        ],
        "induction_roller_off": [
            "InductionRoller1_ManRunPB 0",
            "InductionRoller1_ManStopPB 1",
            "InductionRoller1_Jog 0",
        ],
        "induction_roller_jog": [
            "InductionRoller1_ManRunPB 0",
            "InductionRoller1_Jog 1",
            "InductionRoller1_ManStopPB 0",
        ],
        "induction_roller_speed": ["InductionRollerSpdOffset"],
        "induction_conveyor_on": [
            "InductionConveyor_ManRunPB 1",
            "InductionConveyor_ManStopPB 0",
        ],
        "induction_conveyor_off": [
            "InductionConveyor_ManRunPB 0",
            "InductionConveyor_ManStopPB 1",
            "InductionConveyor_FwdJog 0",
        ],
        "induction_conveyor_jog": [
            "InductionConveyor_ManStopPB 0",
            "InductionConveyor_FwdJog 1",
        ],
        "induction_conveyor_speed": ["InductionConveyorSpdOffset"],
        "vertical_conveyor_on": [
            "VerticalSorterConveyor_ManRunPB 1",
            "VerticalSorterConv_ManStopPB 0",
        ],
        "vertical_conveyor_off": [
            "VerticalSorterConveyor_ManRunPB 0",
            "VerticalSorterConv_ManStopPB 1",
            "VerticalSorterConveyor_Jog 0",
        ],
        "vertical_conveyor_jog": [
            "VerticalSorterConv_ManStopPB 0",
            "VerticalSorterConveyor_Jog 1",
        ],
        "vertical_conveyor_raise": [
            "VerticalSorterConveyor_ManRunPB 0",
            "VerticalSorterConv_ManStopPB 1",
            "VerticalSorterConveyor_Jog 0",
            "VerticalSorterConveyor_RaisePB 1",
            "VerticalSorterConv_LowerPB 0",
        ],
        "vertical_conveyor_lower": [
            "VerticalSorterConveyor_ManRunPB 0",
            "VerticalSorterConv_ManStopPB 1",
            "VerticalSorterConveyor_Jog 0",
            "VerticalSorterConveyor_RaisePB 0",
            "VerticalSorterConv_LowerPB 1",
        ],
        "rework_conveyor_on": ["ReworkConveyor_ManStopPB 0", "ReworkConveyor_ManRunPB 1"],
        "rework_conveyor_off": [
            "ReworkConveyor_ManRunPB 0",
            "ReworkConveyor_ManStopPB 1",
            "ReworkConveyor_Jog 0",
        ],
        "rework_conveyor_jog": [
            "ReworkConveyor_ManStopPB 0",
            "ReworkConveyor_Jog 1",
        ],
        "distribution_conveyor_on": [
            "DistributionConv_ManRunPB 1",
            "DistributionConv_ManStopPB 0",
            "DistributionConveyor_RevJog 0",
            "DistributionConveyor_FwdJog 0",
        ],
        "distribution_conveyor_off": [
            "DistributionConv_ManRunPB 0",
            "DistributionConv_ManStopPB 1",
            "DistributionConveyor_RevJog 0",
            "DistributionConveyor_FwdJog 0",
        ],
        "distribution_conveyor_fjog": [
            "DistributionConv_ManRunPB 0",
            "DistributionConv_ManStopPB 0",
            "DistributionConveyor_FwdJog 1",
            "DistributionConveyor_RevJog 0",
        ],
        "distribution_conveyor_rjog": [
            "DistributionConv_ManRunPB 0",
            "DistributionConv_ManStopPB 0",
            "DistributionConveyor_FwdJog 0",
            "DistributionConveyor_RevJog 1",
        ],
        "distribution_conveyor_speed": ["DistributionConveyorSetSpeedFPM"],
        "diverter_1_on": [
            "Sorter1_DivertToTray 1",
            "Sorter1_DivertToTrayPB 1",
        ],
        "diverter_1_off": [
            "Sorter1_DivertToTray 0",
            "Sorter1_DivertToTrayPB 0",
        ],
        "diverter_2_on": [
            "Sorter2_DivertToTray 1",
            "Sorter2_DivertToTrayPB 1",
        ],
        "diverter_2_off": [
            "Sorter2_DivertToTray 0",
            "Sorter2_DivertToTrayPB 0",
        ],
        "diverter_3_raise": ["PickandPlace_RaisePB 1", "PickandPlace_LowerPB 0"],
        "diverter_3_lower": ["PickandPlace_LowerPB 1", "PickandPlace_RaisePB 0"],
        "diverter_3_extend": [
            "PickandPlace_MoveToTrayPB 1",
            "PickandPlace_MoveToConveyorPB 0",
        ],
        "diverter_3_retract": [
            "PickandPlace_MoveToConveyorPB 1",
            "PickandPlace_MoveToTrayPB 0",
        ],
        "diverter_3_off": ["PickandPlace_ManualVacuum 0"],
        "diverter_3_on": ["PickandPlace_ManualVacuum 1"],
    }

    def send_command(self, cmd: str, value: str = None):
        msg = "tag write "

        if cmd in self.commands:
            msg += " ".join(self.commands[cmd])
        else:
            msg += cmd

        if value:
            msg += value

        return self.send(msg)

    def send(self, msg: str):
        if self.active_connection:
            try:
                self.client.sendall(msg.encode("utf-8"))

                length = int(self.client.recv(8).decode("utf-8"))
                response = self.client.recv(length).decode("utf-8")

                if length == 3 and response == "-32":
                    self.plc_online = False
                else:
                    return response

            except OSError:
                self.plc_online = False

            except ValueError:
                pass

        return None

    def initialize_data(self):
        if not self.plc_online:
            return

        response = self.send("tag all")
        if response:
            try:
                info = json.loads(response)
                for tag in info.keys():
                    info[tag]["value"] = "Unknown"

                self.data = info
            except json.JSONDecodeError:
                print("ERROR initializing data\n")
            except TypeError:
                print("ERROR info was none", response)

    def update_data(self) -> None:
        if not self.active_connection:
            self.connect()
            return

        if not self.plc_online:
            return

        response = self.send("tag read-all")
        if response:
            try:
                values = json.loads(response)
                if isinstance(values, int):
                    # Comand response code recived instead of JSON data
                    # Ignore for now (todo handle on different threads)
                    return

                for tag in values.keys():
                    if tag in self.data:
                        self.data[tag]["value"] = str(values[tag])
            except json.JSONDecodeError:
                print("ERROR updating data\n")
                self.disconnect()
                self.connect()

    @staticmethod
    def get_data_value_headings():
        return {
            "type": "Type",
            "dim": "Dimension",
            "access": "Access",
            "value": "Value",
        }


class OccupancyInformationProvider(InformationProvider):
    """Interface with occupancy sensors. Display data when recived"""

    def connect(self):
        self.active_connection = False

    @property
    def connected(self) -> bool:
        return self.active_connection

    def initialize_data(self):
        if not self.active_connection:
            return

        self.data["date"] = {"value": "Unknown"}
        self.data["time"] = {"value": "Unknown"}

    def update_data(self):

        self.data["date"] = {
            "type": "DATE",
            "value": datetime.now().strftime("%h/%d/%y"),
        }
        self.data["time"] = {
            "type": "TIME",
            "value": datetime.now().strftime("%I:%M:%S"),
        }

    @staticmethod
    def get_data_value_headings():
        return {"type": "Type", "value": "Value"}


def create_device(d, cfg) -> InformationProvider:
    device_type = d['type']
    name = d['name']
    _id = d['id']
    ip = d['ip']
    port = d['port']

    match device_type:
        case "skill-boss-logistics":
            return AllenBradleyInformationProvider(name, _id, ip, port)
        case "qarm" | "qbot" | "rotatory":
            return QuanserInformationProvider(name, _id, ip, port, device_type, cfg['datapoints'][device_type])
        case "pi-plc-server":
            return RaspberryPiRelayInformationProvider(name, _id, ip, port)
        case "occupancy":
            return OccupancyInformationProvider(name, _id, ip, port)
        case _:
            raise AttributeError("Invalid device type " +
                                 device_type + " in config")
