import os

BYTESIZE = 8

def calculateBytes(w, h, bpp):
	return int((w * h * bpp) / BYTESIZE)

def main(args):
	# Args: (width, height, bpp, mipmap)
	
	if (args == None or len(args) < 4):
		width = int(input("Enter width: "))
		height = int(input("Enter height: "))
		bpp = int(input("Enter Bits Per Pixel: "))
		mipmap = int(input("Enter Mipmaps: "))
	else:
		width = int(args[0])
		height = int(args[1])
		bpp = int(args[2])
		mipmap = int(args[3])
	
	size = calculateBytes(width, height, bpp)

	while(mipmap > 0):
		# Halves resolution
		width = width >> 1
		height = height >> 1
		
		if (width == 0):
			width = 1
		
		if (height == 0):
			height = 1
	
		# Adds mipmap size
		size += calculateBytes(width, height, bpp)
		mipmap -= 1
	
	# Prints number of bytes
	print("")
	print("Total byte size is:", size)

if __name__ == '__main__':
    main(os.sys.argv[1:]) # Passes all but first arg