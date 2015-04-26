from TileCodecs import TileCodec

def msb(mask):
    """
    Gets the position of the most significant set bit in the given int.
    """
    for i in reversed(range(32)):
        if (mask & 0x80000000) != 0:
            return i
        mask <<= 1

    return -1  # no bits set


def getByteIntegralBitCount(bpp):
    """
    Gets the least number of whole bytes that are required to store
    <bpp> bits of information.
    """
    if (bpp % 8) != 0:
        return bpp - bpp % 8 + 8
    else:
        return bpp

class DirectColorCodec(TileCodec):
    """
    16, 24, and 32-bit direct-color (ARGB) tile codec.
    # of bits per color component must not exceed 8.
    The color component masks must be directly adjacent.
    """

    LITTLE_ENDIAN = 1
    BIG_ENDIAN = 2

    # Predefined masks
    MASK_15BPP_RGB_555 = [0x7C00, 0x03E0, 0x001F]
    MASK_15BPP_BGR_555 = [0x001F, 0x03E0, 0x7C00]
    MASK_16BPP_RGB_565 = [0xF800, 0x07E0, 0x001F]
    MASK_16BPP_BGR_565 = [0x001F, 0x07E0, 0xF800]
    MASK_16BPP_ARGB_1555 = [0x7C00, 0x03E0, 0x001F, 0x8000]
    MASK_16BPP_ABGR_1555 = [0x001F, 0x03E0, 0x7C00, 0x8000]
    MASK_16BPP_RGBA_5551 = [0xF800, 0x07C0, 0x003E, 0x0001]
    MASK_16BPP_BGRA_5551 = [0x003E, 0x07C0, 0xF800, 0x0001]
    MASK_24BPP_RGB_888 = [0xFF0000, 0x00FF00, 0x0000FF]
    MASK_24BPP_BGR_888 = [0x0000FF, 0x00FF00, 0xFF0000]
    MASK_32BPP_ARGB_8888 = [0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000]
    MASK_32BPP_ABGR_8888 = [0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000]
    MASK_32BPP_RGBA_8888 = [0xFF000000, 0x00FF0000, 0x0000FF00, 0x000000FF]
    MASK_32BPP_BGRA_8888 = [0x0000FF00, 0x00FF0000, 0xFF000000, 0x000000FF]

    def __init__(self, bpp, masks, endianness=LITTLE_ENDIAN, stride=0):
        """
        Creates a direct-color tile codec.

        Arguments:
        bpp - Bits per pixel
        endianness - Either LITTLE_ENDIAN or BIG_ENDIAN
        masks - Tuple describing the color mask in the format (r,g,b,a)
                Example: [0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000]
                The alpha value is optional
        stride - 0 for MODE_1D, -1 + (# of tile columns in your final image)
                 for MODE_2D. I have no idea why this exists
        """
        TileCodec.__init__(self, getByteIntegralBitCount(bpp), stride)
        self.bytes_per_pixel = self.bits_per_pixel // 8   # 2, 3 or 4

        if len(masks) < 3:
            raise ValueError("Mask needs to have at least 3 values, got {}"\
                    .format(len(masks)))
        elif len(masks) == 3:
            masks.append(0)
        self.masks = masks

        # calculate the shifts
        self.shifts = (
            23 - msb(self.masks[0]),
            15 - msb(self.masks[1]),
            7  - msb(self.masks[2]),
            31 - msb(self.masks[3]))

        self.setEndianness(endianness)


    def setEndianness(self, endianness):
        """
        Sets the endianness.
        """
        self.endianness = endianness
        if endianness == self.LITTLE_ENDIAN:
            self.start_shift = 0
            self.shift_step = 8
        else: # BIG_ENDIAN
            self.start_shift = (self.bytes_per_pixel-1) * 8
            self.shift_step = -8


    def decode(self, bits, ofs=0):
        """
        Decodes a tile. Has to be implemented by subclasses.

        Arguments:
        bits - A bytes-like object of encoded tile data
        ofs - Start offset of tile in bits
        """
        self.checkBitsLength(bits, ofs)

        pixels = []

        for i_row in range(8):
            # do one row of pixels
            for i_pixel in range(8):
                # get encoded pixel
                pixel_bytes = 0
                for i_byte in range(self.bytes_per_pixel):
                    shift = (self.start_shift + i_byte*self.shift_step)
                    pos = (ofs + (i_row*8 + i_pixel) * self.bytes_per_pixel +
                        self.stride*i_row + i_byte)
                    pixel_bytes |= bits[pos] << shift

                pixel = 0
                for i_mask in range(4):
                    mask = self.masks[i_mask]
                    shift = self.shifts[i_mask]
                    color = pixel_bytes & mask
                    if shift < 0:
                        color >>= -shift
                    else:
                        color <<= shift

                    pixel |= color

                pixels.append(pixel)

        return pixels


    def encode(self, pixels, bits=None, ofs=0):
        """
        Encodes a tile.

        Arguments:
        pixels - A list of decoded tile data
        bits - A bytearray object to encode the data into
        ofs - Start offset of tile in bits
        """
        if bits is None:
            bits = b"\x00" * (self.tile_size)
        bits = bytearray(bits)

        self.checkBitsLength(bits, ofs)

        for i_row in range(8):
            # do one row of pixels
            for i_pixel in range(8):
                # get decoded pixel
                pixel_pos = i_row * 8 + i_pixel

                argb = pixels[pixel_pos]
                bin_pixel = 0

                for i_mask in range(4):
                    mask = self.masks[i_mask]
                    shift = self.shifts[i_mask]
                    if shift < 0:
                        color = argb << (-shift)
                    else:
                        color = argb >> shift
                    bin_pixel |= color & mask

                # final value
                for i_byte in range(self.bytes_per_pixel):
                    shift = (self.start_shift + i_byte*self.shift_step)
                    pos = (ofs + (i_row*8 + i_pixel) * self.bytes_per_pixel +
                        self.stride*i_row + i_byte)
                    bits[pos] = (bin_pixel >> shift) & 0xFF

        return bits
