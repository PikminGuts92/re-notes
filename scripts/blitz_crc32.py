import sys

MAX_INT = (2 ** 31) - 1
B_CRC_TABLE = None

def init_table():
    table = [1] * 0x100
    v2 = 0

    for i in range(0, 0x100):
        v3 = v2 << 0x18

        for _ in range(0, 8):
            #if v3 > MAX_INT:
            #    v3 = (v3 << 1) ^ 0x4c11db7
            #else:
            #    v3 = v3 << 1
            v3 = (v3 << 1) ^ 0x4c11db7 if v3 & 0x80000000 else v3 << 1

        table[i] = v3 & 0xffffffff
        v2 = i + 1

    return table

def bk_string_crc(str_value: str, hash: int):
    for c in str_value:
        print(c)
        hash = hash << 8 ^ (B_CRC_TABLE[(hash >> 0x18 ^ ord(c)) & 0xff])
        hash = hash & 0xffffffff

    return hash

if __name__ == '__main__':
    str_value = sys.argv[1]
    table = B_CRC_TABLE = init_table()
    result = bk_string_crc(str_value, 0)

    print(table)
    print(str_value)
    print(f'0x{result:08X}')