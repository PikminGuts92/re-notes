import os
import struct
import sys

def Main():
    extFilter = (".bmp_xbox", ".png_xbox")

    input = os.path.dirname(os.sys.argv[0])
    if os.path.isdir(input):
        files = []

        for (dirpath, dirnames, filenames) in os.walk(input):
            for name in filenames:
                # Filter out non-milo files.
                if not name.lower().endswith(extFilter):
                    continue
                files.extend([name])
            break # Prevents it from getting sub-directories/files.

        if (len(files) < 1):
            print("Found no texture files in directory.")
            return
        else:
            print("Found", len(files), "files.")

        for name in files:
            tex = HMXTexture(os.path.join(input, name))
            tex.SaveAsDDS(os.path.join(input, os.path.splitext(name)[0] + ".dds"))
            print(name + " converted.")
        pass
    elif os.path.isfile(input):
        print("This is a file.")
        pass
    else:
        return

class HMXTexture:
    def SaveAsDDS(self, outPath):
        inFile = open(self.path, "rb")
        outFile = open(outPath, "wb")

        size = inFile.seek(0, 2)
        inFile.seek(self.ddsOffset, 0)

        outFile.write(self.BuildDDSHeader(self.width[0], self.height[0], self.version[0]))

        # Shuffles bytes only for Xbox.
        while (inFile.tell() < size):
            buf1 = inFile.read(1)
            buf2 = inFile.read(1)

            if self.xbox:
                outFile.write(buf2)
                outFile.write(buf1)
            else:
                outFile.write(buf1)
                outFile.write(buf2)

        inFile.close()
        outFile.close()
        return

    def __init__(self, path):
        if not os.path.isfile(path):
            return

        if os.path.splitext(path)[1].lower() == ".png_xbox":
            self.xbox = True
        elif os.path.splitext(path)[1].lower() == ".bmp_xbox":
            self.xbox = True
        else:
            self.xbox = False

        self.path = path
        with open(self.path, "rb") as file:
            self.SetHeaderInfo(file.read(32))
        return

    def SetHeaderInfo(self, data):
        self.version = struct.unpack_from("<i", data, 2)
        self.width = struct.unpack_from("<h", data, 7)
        self.height = struct.unpack_from("<h", data, 9)
        self.ddsOffset = 32;
        return

    def BuildDDSHeader(self, width, height, version):
        if (version == 8): # DXT1
            v = bytes([ 0x44, 0x58, 0x54, 0x31])
        elif (version == 32): # ATI2
            v = bytes([ 0x41, 0x54, 0x49, 0x32])
        else: # DXT5
            v = bytes([ 0x44, 0x58, 0x54, 0x35])

        h = struct.pack("<I", height)
        w = struct.pack("<I", width)

        dds = bytes([
            0x44, 0x44, 0x53, 0x20, 0x7C, 0x00, 0x00, 0x00, 0x07, 0x10, 0x0A, 0x00, h[0], h[1], h[2], h[3],
            w[0], w[1], w[2], w[3], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00,
            0x04, 0x00, 0x00, 0x00, v[0], v[1], v[2], v[3], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
                ])
        return dds

if __name__ == '__main__':
    Main()
    input("Press Enter to continue...")