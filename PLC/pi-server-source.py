import json
import socket
import dataclasses
import time

from pycomm3 import LogixDriver, CommError
from pycomm3.logix_driver import ReadWriteReturnType

# Author: Aaron Rahman <cyber@umich.edu>
# Date: Summer 2022
# Updated: Hayden Singleton <hsinglet@gmu.edu>, Spring 2023

# commands
# tag
#    read <tag> -> simulink response, float as string
#    write <tag> <val> (repeating) -> simulink response, code if successful
#    all -> json response
#    read-all -> json response
# A simulink response is limited to 256 bytes, the first which must represent the size of the remainder (i.e. 3 before 'abc')


# Socket server parameters
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999
PLC_IP = "192.168.1.1"


# Error Codes
STATUS_UNKNOWN_COMMAND = '-27'
STATUS_INVALID_COMMAND_PARAMETERS = '-28'
STATUS_TAG_DOES_NOT_EXIST = '-29'
STATUS_TAG_VALUE_CAST_FAILED = '-30'
STATUS_ERROR_UNKNOWN = '-31'
STATUS_PLC_NOT_CONNECTED = '-32'
STATUS_READ_RETURNED_LIST = '-33'
STATUS_WRITE_OKAY = '99'


# Main code for parsing a command. Since the API is small it's just a list of if-else statements.
def parse_command(plc: LogixDriver, cmd: str):

    if not plc.connected:
        return STATUS_PLC_NOT_CONNECTED

    parsed = cmd.split()
    if parsed[0] != 'tag' or len(parsed) < 2:
        return STATUS_UNKNOWN_COMMAND

    match parsed[1]:
        case 'write':
            if len(parsed) < 4 or len(parsed) % 2 == 1:
                return STATUS_INVALID_COMMAND_PARAMETERS

            index = 2
            while len(parsed) > index + 1:
                write_result = write(plc, parsed[index], parsed[index + 1])
                if write_result == STATUS_TAG_VALUE_CAST_FAILED:
                    return write_result

                read = parse_read(write_result, command=cmd)
                if read.error:
                    return read.result

                index += 2
            return STATUS_WRITE_OKAY
        case 'read':
            if len(parsed) != 3:
                return STATUS_INVALID_COMMAND_PARAMETERS

            return parse_read(plc.read(parsed[2]), cmd).result
        case 'all':
            if len(parsed) != 2:
                return STATUS_INVALID_COMMAND_PARAMETERS

            info = get_tag_info(plc)
            return json.dumps(info)
        case 'read-all':
            if len(parsed) != 2:
                return STATUS_INVALID_COMMAND_PARAMETERS

            tags = read_all_tags(plc)
            return json.dumps(tags)
        case _:
            return STATUS_UNKNOWN_COMMAND


def get_tag_info(plc) -> dict:

    try:
        return get_tag_info.cache
    except AttributeError:
        pass

    tag_list = plc.get_tag_list()
    formatted = {}

    for datapoint in tag_list:
        formatted[datapoint["tag_name"]] = {
            "name": datapoint["tag_name"],
            "type": datapoint["data_type_name"],
            "dim": datapoint["dim"],
            "access": datapoint["external_access"]
        }

    get_tag_info.cache = formatted

    return get_tag_info.cache


def read_all_tags(plc):
    tag_info = get_tag_info(plc)
    values = plc.read(*tag_info)
    result = {}

    for val in values:
        if val.error is not None:
            result[val.tag] = None
        else:
            result[val.tag] = str(val.value)

    return result


def write(plc, tag: str, value: str):
    try:
        val = float(value)
        return plc.write((tag, val))
    except ValueError:
        pass
    except OSError:
        pass
    return STATUS_TAG_VALUE_CAST_FAILED


@dataclasses.dataclass
class ParsedRead:
    error: bool
    result: str


def parse_read(read_result: ReadWriteReturnType, command: str):
    if isinstance(read_result, list):
        return ParsedRead(True, STATUS_READ_RETURNED_LIST)

    if read_result.error is not None:
        if "Tag doesn't exist" == read_result.error.strip():
            return ParsedRead(True, STATUS_TAG_DOES_NOT_EXIST)

        print("ERROR " +
              read_result.error + " for command " + command)
        return ParsedRead(True, STATUS_ERROR_UNKNOWN)

    try:
        val = float(read_result.value)
        if val.is_integer():
            val = int(val)
        return ParsedRead(False, str(val))
    except ValueError:
        return ParsedRead(True, STATUS_TAG_VALUE_CAST_FAILED)


def connect_plc() -> tuple([LogixDriver, bool]):
    plc = None
    try:
        plc = LogixDriver(PLC_IP)
        plc.open()
    except CommError:
        pass
    return plc


def run_loop(plc: LogixDriver, conn: socket.socket):
    while True:
        data = conn.recv(1024)
        if not data:
            break

        data = data.decode('utf-8')

        if data == 'plc_status':
            if not plc.connected:
                plc = connect_plc()

            if plc.connected:
                reply = "plc_online"
                get_tag_info(plc)
            else:
                reply = "plc_offline"
        else:
            reply = parse_command(plc, data)

            if data not in ['tag read-all', 'tag all']:
                print("Cmd:", data)
                print("Ok" if reply == '99' else f"Status: {reply}")

        reply = reply.encode('utf-8')

        length = f'{len(reply):<8}'
        length = length.encode('utf-8')

        conn.sendall(length)
        time.sleep(0)
        conn.sendall(reply)


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((SERVER_IP, SERVER_PORT))
            server.listen(1)
            print("Listening for connections on:", SERVER_IP)

            plc = connect_plc()

            while True:
                try:
                    conn, _ = server.accept()
                    with conn:
                        run_loop(plc, conn)

                except OSError:
                    print("Resetting server")

    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()
