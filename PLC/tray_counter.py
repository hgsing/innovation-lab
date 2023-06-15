import struct
import socket
import time
import sys
import pycomm3


class Connection:

    def __init__(self, sock, server):
        self.sock = sock
        self.server = server
        self.length = 0

    def reset_connection(self):
        self.sock.close()
        self.sock, _ = self.server.accept()

    def send(self, msg):
        self.sock.sendall(msg)

    def recv(self, expected_len=None) -> bytes:

        if not expected_len:
            expected_len = self.length

        resp = self.sock.recv(expected_len)

        if resp == b'':
            raise RuntimeError("socket connection broken")
        else:
            self.reset_connection()

        return resp


def get_tray_values(plc: pycomm3.LogixDriver):
    if plc is None:
        values = input('Values: ').split()[0:3]
        if values:
            return {i: int(v) for i, v in enumerate(values)}
        else:
            exit(0)

    counts: dict[int] = dict()
    for t in ['Tray1_Counter', 'Tray2_Counter', 'Tray3_Counter']:
        tag = plc.read(t)

        # tag value is a dict with fields "PRE, ACC, CU, CD, DN, OV, UN"
        counts[t] = tag.value['ACC']

    return counts


def notify_tray_changes(plc: pycomm3.LogixDriver, conn: Connection):
    boxes = [None, 0, 0, 0]
    prev = [None, 0, 0, 0]

    while True:
        msg = struct.pack('<2d', 0, 0)
        print("msg:", msg)
        conn.send(msg)

        info = get_tray_values(plc)

        if any(boxes):
            print("Tray values:", info.values())

        stack = []
        trigger = 0

        for tray, count in enumerate(info.values(), start=1):

            if prev[tray] != count:
                prev[tray] = count
                boxes[tray] += 1
                stack.append(tray)
                trigger = 1

        # Put the largest count on top of stack
        stack.sort(reverse=True)

        if stack and boxes[stack[-1]] > 0:
            print("stack:", ', '.join([f'{s}:{boxes[s]}' for s in stack]))
            tray = stack[-1]
            print(
                f"{boxes[tray]} {'boxes' if boxes[tray] != 1 else 'box'} in tray", tray)

            print(f"sending [{trigger}, {tray}]")
            data = struct.pack('<2d', trigger, tray)

            v1 = v2 = 0
            while not v1:
                conn.send(data)
                time.sleep(0.1)

                resp = conn.recv(len(data))
                v1, v2 = struct.unpack('<2d', resp)

                time.sleep(0.1)

            data = struct.pack('<2d', 0, 0)

            while not v2:
                conn.send(data)
                time.sleep(0.1)

                resp = conn.recv(len(data))
                v1, v2 = struct.unpack('<2d', resp)
                # print(v1, _v2)

                time.sleep(0.1)

            stack.pop()

            print(f"response: {v1},{v2}")
            if boxes[tray] > 0:
                boxes[tray] -= 1

            if boxes[tray]:
                print(f"{boxes[tray]} Boxes left in tray {tray}:")
            else:
                print(f"Tray {tray} empty.")

        time.sleep(1)


def use_plc(plc: pycomm3.LogixDriver):
    if plc:
        plc.write("Reset_CountersPB", True)
        plc.write("Reset_CountersPB", False)

        print(f"PLC connected")

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(('192.168.2.4', 9997))
            server.listen(1)
            print('Waiting for QARM connection..')
            conn, address = server.accept()
            print("Connected with {}:{}".format(*address))
            with conn:
                notify_tray_changes(plc, Connection(conn, server))
                print("Waiting for new connection")


try:
    with pycomm3.LogixDriver("192.168.1.1") as plc:
        if len(sys.argv) > 1:
            raise pycomm3.exceptions.CommError

        use_plc(plc)

except pycomm3.exceptions.CommError:
    print("Using test values.")
    use_plc(None)
