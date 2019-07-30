import sys
import os
import zlib

def decompress(block):
    z = zlib.decompressobj()
    return z.decompress(block)

def compress(block):
    z = zlib.compressobj()
    return zlib.compress(block)

def main(argv):
    if len(argv) < 2:
        print("Args: inputPath [outputPath]")
        return
    
    inFile_path = argv[1]
    ext = os.path.splitext(inFile_path)[1]
    compressed = ext.lower() == ".z"

    # Reads data
    inFile = open(inFile_path, "rb")
    inData = inFile.read()
    inFile.close()

    outData = decompress(inData) if compressed else compress(inData)
    outFile_path = os.path.splitext(inFile_path)[0] if compressed else inFile_path + ".z"

    # Writes data
    outFile = open(outFile_path, "wb")
    outFile.write(outData)
    outFile.close()

    print("Wrote output to", outFile_path)

if __name__ == "__main__":
    main(sys.argv)