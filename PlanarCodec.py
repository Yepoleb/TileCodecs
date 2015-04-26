from TileCodecs import TileCodec

class PlanarCodec(TileCodec):
    """
    Planar, palette-indexed 8x8 tile codec. Max. 8 bitplanes.
    Planes for each row must be stored sequentially.
    """

    PLANEORDER = [0, 1, 2, 3, 4, 5, 6, 7]

    def __init__(self, bpp=None, bp_offsets=None, stride=0):
        """
        Creates a planar codec. Only one of bpp and bp_offsets can be used.

        Arguments:
        bpp - Bits per pixel
        bp_offsets - Relative offsets for the bitplane values in a row (8 pixels)
                     of encoded tile data. The length of this array is the number
                     of bitplanes in a tile row, which is equal to the # of bits
                     per pixel.
        stride - 0 for MODE_1D, -1 + (# of tile columns in your final image)
                 for MODE_2D. I have no idea why this exists
        """

        if (bpp is not None) and (bp_offsets is not None):
            raise ValueError("Only one of bpp or bp_offsets can be given")
        elif bp_offsets is not None:
            bpp = len(bp_offsets)
        elif bpp is not None:
            bp_offsets = self.PLANEORDER[:bpp]
        else:
            raise ValueError("No bpp or bp_offset value given")

        TileCodec.__init__(self, bpp, stride)
        self.bp_offsets = bp_offsets

        # Precalculate all bit patterns
        self.pixels_lookup = []
        for i in range(8):
            self.pixels_lookup.append([])
            # do one bitplane
            for j in range(265):
                self.pixels_lookup[i].append([])
                # do one byte
                for k in range(8):
                    # do one pixel
                    self.pixels_lookup[i][j].append(((j >> (7-k)) & 1) << i)


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
            # do one row of pixels
            bitplane = []
            pos = ofs + i_row * (self.bytes_per_row + self.stride)
            for i_byte in range(self.bytes_per_row):
                # get bits for bitplane j
                bitplane.append(bits[pos+self.bp_offsets[i_byte]])

            for i_pixel in range(8):
                # decode one pixel
                pixel = 0
                for k in range(self.bits_per_pixel):
                    # add bitplane k
                    pixel |= self.pixels_lookup[k][bitplane[k]][i_pixel]
                pixels.append(pixel)

        return pixels


    def encode(self, pixels, bits=None, ofs=0):
        """
        Encodes a bitplaned tile.

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
            pos = ofs + i_row * (self.bytes_per_row + self.stride)
            for i_byte in range(self.bytes_per_row):
                # reset bits of bitplane j
                bits[pos+self.bp_offsets[i_byte]] = 0

            for i_pixel in range(8):
                # encode one pixel
                pixel_pos = i_row*8 + i_pixel
                pixel = pixels[pixel_pos]
                for k in range(self.bits_per_pixel):
                    # add bitplane k
                    bits[pos+self.bp_offsets[k]] |= ((pixel >> k) & 0x01) << \
                            (7-i_pixel)

        return bits
