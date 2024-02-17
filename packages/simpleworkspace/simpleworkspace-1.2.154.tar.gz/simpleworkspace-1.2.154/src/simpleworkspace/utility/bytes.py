def IsPotentiallyBinary(data:bytes, sniffLen=1024):
    data = data[:sniffLen]
    textchars = bytearray([7,8,9,10,12,13,27]) + bytearray(range(32, 127)) + bytearray(range(128, 256))
    return any(byte not in textchars for byte in data)