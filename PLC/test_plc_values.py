
import pycomm3

with pycomm3.LogixDriver("192.168.1.1") as plc:

    test = plc.read('TestBit').value
    print("TestBit:", test)

    while flag := input('continue ? (blank = exit): '):
        print("Writing", test)
        plc.write('TestBit', test)
        print("Now TestBit = ", plc.read('TestBit').value)
        
        test = not bool(test)
