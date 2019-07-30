# Script that quickly decompresses milo files found in GH/RB games.
import gzip
import os
import struct
import sys
import zlib

def Help():
    h = "This script will decompress(inflate) milo files found in GH/RB games. "
    h += "Output files will have \"dec_\" added to their names."
    h += "\nUsage: inflate_milo <input type> <input>"
    h += "\nOption: -f = File"
    h += "\n        -d = Directory"
    h += "\n        -n = None (Use excuted .py location)"
    h += "\nExample: inflate_milo -f \"E:\\RB3Stuff\\splash.milo_xbox\""
    return h

def Main():
    extFilter = (".gh", ".kr", ".rnd", ".rnd_gc", ".rnd_gz", ".rnd_ps2", ".rnd_xbox", ".milo", ".milo_ps2", ".milo_ps3", ".milo_wii", ".milo_xbox")
    '''
    if (len(sys.argv) < 2):
        print(Help())
    else:
        o = sys.argv[1].lower()
        if o == "-f":
            pass
        elif o == "-d":
            pass
        elif o == "-n":
            pass
        else:
            print("Invalid input type.")
            return
        pass
    '''

    input = os.path.dirname(os.sys.argv[0])

    if os.path.isdir(input):
        files = []

        for (dirpath, dirnames, filenames) in os.walk(input):
            for name in filenames:
                # Filter out non-milo files.
                if not name.lower().endswith(extFilter):
                    continue
                elif name.lower().startswith("dec_"):
                    continue
                files.extend([name])
            break # Prevents it from getting sub-directories/files.

        if (len(files) < 1):
            print("Found no milo files in directory.")
            return
        else:
            print("Found", len(files), "files.")

        for name in files:
            with open(os.path.join(input, name), "rb") as file:
                milo = MiloFile(file)
                if milo.version != 'Z':
                    out = open(os.path.join(input, "dec_" + name), "wb")
                    out.write(milo.rawData)
                    out.close();
                    print(name + " inflated.")
                else:
                    print(name + " skipped.")

        pass
    elif os.path.isfile(input):
        print("This is a file.")
        InflateMilo(input)
        pass
    else:
        return

def InflateMilo(path):
    if os.path.exists(path) == False:
        return 0

    try:
        with open(path, "rb") as file:
            milo = MiloFile(file)
        print("Compression Type: " + milo.version)

        return 1
    finally:
        return 0

class MiloFile:
    def GetMeshVersion(self, magic):
        check = str(magic)

        if check == "b'\\xaf\\xde\\xbe\\xca'":
            return 'A'
        elif check == "b'\\xaf\\xde\\xbe\\xcb'":
            return 'B'
        elif check == "b'\\xaf\\xde\\xbe\\xcc'":
            return 'C'
        elif check == "b'\\xaf\\xde\\xbe\\xcd'":
            return 'D'
        else:
            return 'Z'

    def __init__(self, file):
        self.version = self.GetMeshVersion(file.read(4))
        if self.version == 'Z':
            print("This is not a milo file.")
            return

        # Zlib/GZip Offset, Count of Blocks, Size of Biggest Block (Inflated)
        head = struct.unpack("<III", file.read(12))

        # Size of each block.
        blocks = struct.unpack("<" + str(head[1]) + "I", file.read(4*head[1]))

        file.seek(head[0], 0)

        data = bytes()
        for i in range(0, len(blocks)):

            if self.version == 'A':
                block = file.read(blocks[i])

            elif self.version == 'B':
                block = file.read(blocks[i])
                z = zlib.decompressobj()
                z.decompress(bytes([0x78, 0x9c]))
                block = z.decompress(block)

            elif self.version == 'C':
                block = file.read(blocks[i])
                block = gzip.decompress(block)

            elif self.version == 'D':
                if blocks[i] >= 16777216: # Already decompressed
                    readSize = blocks[i] - 16777216
                    block = file.read(readSize)
                else:
                    file.read(4) # Not needed (Uncompressed Size)
                    block = file.read(blocks[i] - 4)
                    z = zlib.decompressobj()
                    z.decompress(bytes([0x78, 0x9c]))
                    block = z.decompress(block)

            data = data + block
        self.rawData = data
        return

if __name__ == '__main__':
    Main()
    input("Press Enter to continue...")