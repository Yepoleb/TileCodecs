from TileCodecs import TileCodec

class _3BPPLinearCodec(TileCodec):
    """
    Linear palette-indexed 8x8 tile codec for 3bpp.
    """


    def __init__(self, stride=0):
        """
        Constructor for 3BPPLinearCodec

        Arguments:
        stride - 0 for MODE_1D, -1 + (# of tile columns in your final image)
                 for MODE_2D. I have no idea why this exists
        """
        TileCodec.__init__(self, 3, stride)

    def decode(self, bits, ofs=0):
        """
        Decodes a tile.

        Arguments:
        bits - A bytes-like object of encoded tile data
        ofs - Start offset of tile in bits
        """
        self.checkBitsLength(bits, ofs)

        pixels = []
        for i_row in range(8):
            # do one row
            pos = i_row * self.bytes_per_row + i_row * self.stride
            byte1 = bits[pos+0] # byte 1: 0001 1122
            byte2 = bits[pos+1] # byte 2: 2333 4445
            byte3 = bits[pos+2] # byte 3: 5566 6777
            pixels.append((byte1 >> 5) & 7)
            pixels.append((byte1 >> 2) & 7)
            pixels.append(((byte1 & 3) << 1) | ((byte2 >> 7) & 1))
            pixels.append((byte2 >> 4) & 7)
            pixels.append((byte2 >> 1) & 7)
            pixels.append(((byte2 & 1) << 2) | ((byte3 >> 6) & 3))
            pixels.append((byte3 >> 3) & 7)
            pixels.append(byte3 & 7)

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
            # do one row
            pos = i_row * self.bytes_per_row + i_row * self.stride
            pxpos = i_row * 8
            byte1 = (pixels[pxpos+0] & 7) << 5
            byte1 |= (pixels[pxpos+1] & 7) << 2
            byte1 |= (pixels[pxpos+1] & 6) >> 1
            byte2 = (pixels[pxpos+2] & 1) << 7
            byte2 |= (pixels[pxpos+3] & 7) << 4
            byte2 |= (pixels[pxpos+4] & 7) << 1
            byte2 |= (pixels[pxpos+4] & 4) >> 2
            byte3 = (pixels[pxpos+5] & 3) << 6
            byte3 |= (pixels[pxpos+6] & 7) << 3
            byte3 |= (pixels[pxpos+7] & 7)
            bits[pos+0] = byte1 # byte 1: 0001 1122
            bits[pos+1] = byte2 # byte 2: 2333 4445
            bits[pos+2] = byte3 # byte 3: 5566 6777

        return bits
