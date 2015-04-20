from tilecodecs.TileCodec import TileCodec

"""
Comment from the original Tile Molester Code:

Linear palette-indexed 8x8 tile codec. Max. 8 bits per pixel.
bitsPerPixel mod 2 = 0 (so only 1, 2, 4, 8bpp possible).

Some notes on "pixel ordering":

I define pixel order for a row like so: 0 1 2 3 4 5 6 7.
In other words, pixels are numbered from leftmost to rightmost,
as they appear on screen.
I define bit order in a byte like so: 7 6 5 4 3 2 1 0.
In other words, bits are numbered from rightmost (high) to leftmost (low).

For formats with less than 8 bits per pixel, it is then an
issue how bits are extracted from the bytes of encoded tile data
to form the order of pixels stated above.

Note that this applies at the PIXEL-level, not bit-, byte- or row-level;
this is why ordering is not an issue for 8bpp tiles, since each byte
contains only one pixel. It is assumed that the bytes themselves are
always stored in-order (0, 1, 2, 3, ...). Similary, it is assumed that
the individual bits of a pixel are always stored from high -> low.

The familiar terms "little endian" and "big endian" are not appropriate to
use here, as I consider them to apply at the byte-level. To avoid any
confusion or ambiguity, I therefore use the expressions "in-order" and
"reverse-order" to refer to the ordering of pixels within a byte.
This is still a bit tricky since the order of pixels and bits above are
reverses of eachother to begin with, but shouldn't be too confusing:

I define "in-order" to mean that the order of pixel data as stored in a byte
complies with the order of pixels to be rendered, from left to right. For
1bpp, this is simple: in-order means that bit 7 corresponds to pixel 0,
bit 6 to pixel 1 and so on. Reverse-order means that bit 7 corresponds to
pixel 7, bit 6 corresponds to pixel 6 and so on (in other words, the bits
have to be reversed from left to right in order for the pixel order to be
correct). Diagrammatically:

Pixels: 01234567
        |||||||| (In-order)
Bits:   76543210

Pixels: 01234567
        |||||||| (Reverse-order)
Bits:   01234567

This extends quite intuitively to the cases of 2 and 4 bits per pixel.
I will give one example of each.

2bpp, in-order:

Pixels: 0  1  2  3
        |  |  |  |
Bits:   76 54 32 10

4bpp, reverse-order:

Pixels: 0     1
        |     |
Bits:   3210  7654
"""

class LinearTileCodec(TileCodec):
    """
    Linear palette-indexed 8x8 tile codec.
    """

    IN_ORDER=1
    REVERSE_ORDER=2

    def __init__(self, bpp, ordering=None, stride=0):
        """
        Constructor for LinearTileCodec
        
        Arguments:
        bpp - Bits per pixel
        ordering - See explanation above
        stride - I have no idea why this exists
        """
        TileCodec.__init__(self, bpp, stride)
        self.pixels_per_byte = 8 // self.bits_per_pixel
        self.pixel_mask = (1 << self.bits_per_pixel) - 0b1 # e.g. 0b1111 for 4bpp
        
        if ordering is None:
            ordering = IN_ORDER
        self.ordering = ordering

        if self.ordering == self.IN_ORDER:
            self.startPixel = self.pixels_per_byte-1
            self.boundary = -1
            self.step = -1

        else:  # REVERSE_ORDER
            self.startPixel = 0
            self.boundary = self.pixels_per_byte
            self.step = 1

    def decode(self, bits, ofs=0):
        """
        Decodes a tile.
        
        Arguments:
        bits - A bytes-like object of encoded tile data 
        ofs - Start offset of tile in bits
        """
        self.check_bit_length(bits, ofs)
        
        pixels = []
        for i_row in range(8):
            # do one row
            for i_byte in range(self.bytes_per_row):
                # do one byte
                pos = ofs + i_row*self.bytes_per_row + i_byte*self.stride + i_byte
                b = bits[pos]
                for i_pixel in range(self.startPixel, self.boundary, self.step):
                    # decode one pixel
                    pixel = (b >> self.bits_per_pixel*i_pixel) & self.pixel_mask
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
        self.check_bit_length(bits, ofs)
        
        if bits is None:
            bits = b"\x00" * (self.tile_size)
        bits = bytearray(bits)

        for i_row in range(8):
            # do one row
            for i_byte in range(self.bytes_per_row):
                # do one byte
                pos = ofs + i_row*self.bytes_per_row + i_byte*self.stride + i_byte
                b = 0
                for i_pixel in range(self.startPixel, self.boundary, self.step):
                    # encode one pixel
                    pixel_pos = i_row*8 + i_byte*self.pixels_per_byte + i_pixel
                    b = b | ((pixels[pixel_pos] & self.pixel_mask) << (
                            i_pixel*self.bits_per_pixel))
                bits[pos] = b
        
        return bits
