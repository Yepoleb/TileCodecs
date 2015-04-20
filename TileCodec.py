class TileCodec:
    """
    Abstract class for 8x8 ("atomic") tile codecs.
    To add a new tile format, simply extend this class and implement 
    decode() and encode().
    """

    MODE_1D=1
    MODE_2D=2

    def __init__(self, bpp, stride=0):
        """
        Base class constructor. Every subclass must call this with argument bpp.
        
        Arguments:
        bpp - Bits per pixel
        stride - 0 for MODE_1D, -1 + (# of tile columns in your final image)
                 for MODE_2D. I have no idea why this exists
        """
        self.bits_per_pixel = bpp
        self.bytes_per_row = bpp # 8 pixel per row / 8 bits per byte
        self.stride = stride * self.bytes_per_row
        self.tile_size = (self.bytes_per_row + self.stride) * 8 # 8 rows per tile
        self.color_count = 1 << bpp


    def decode(self, bits, ofs=0):
        """
        Decodes a tile. Has to be implemented by subclasses.
        
        Arguments:
        bits - A bytes-like object or int list of encoded tile data 
               (has to return the value of a byte using the [] operator)
        ofs - Start offset of tile in bits array
        """
        raise NotImplementedError
        
        
    def encode(self, pixels, bits=None, ofs=0):
        """
        Encodes a tile. Has to be implemented by subclasses.
        
        Arguments:
        pixels - A list of decoded tile data
        bits - A bytearray object to encode the data into
        ofs - Start offset of tile in bits
        """
        raise NotImplementedError

    def check_bit_length(self, bits, ofs):
        if len(bits) - ofs < self.tile_size:
            raise IndexError("Bits input too short. Required {}b, got {}b".format(
                    ofs+self.tile_size, len(bits)))

    def getBitsPerPixel(self):
        """
        Gets the # of bits per pixel for the tile format.
        """
        return self.bits_per_pixel


    def getBytesPerRow(self):
        """
        Gets the # of bytes per row (8 pixels) for the tile format.
        """
        return self.bytes_per_row


    def getColorCount(self):
        """
        Gets the # of colors for the tile format
        """
        return self.color_count


    def getTileSize(self):
        """
        Gets the size in bytes of one tile encoded in this format.
        """
        return self.tile_size
