from tilecodecs import TileCodec
from tilecodecs import PlanarCodec

"""
Comment from the original Tile Molester Code:

Composite tile codec.
A composite tile is a tile that is built up of several
standard tiles. As an example, consider a 3bpp tile that consists
of a single 2bpp non-interleaved tile followed by a single 1bpp tile.
Such a format cannot be accommodated by the standard planar tile codec
(PlanarCodec). However, it can be accommodated by instantiating several
PlanarCodecs, decoding planar tiles separately and then "overlaying" them
on top of each other. This class provides just this kind of functionality.
It allows more flexibility in the tile formats, but is probably a bit
slower.
"""

class CompositeCodec(TileCodec):

    def __init__(self, codecs, stride=0):
        """
        Creates a composite tile codec.

        Arguments:
        bpp - Bits per pixel
        codecs - A list of codecs that will be used to build
                 a tile, going from low to high bitplanes.
        """
        bpp = sum(c.getBitsPerPixel() for c in codecs)

        TileCodec.__init__(self, bpp, stride)
        self.codecs = codecs


    def decode(self, bits, ofs=0):
        """
        Decodes a tile.

        Arguments:
        bits - A bytes-like object of encoded tile data
        ofs - Start offset of tile in bits
        """
        self.checkBitsLength(bits, ofs)

        # decode the first sub-tile
        pixels = self.codecs[0].decode(bits, ofs)
        # decode remaining sub-tiles
        shift = self.codecs[0].getBitsPerPixel()
        pos = ofs
        for i in range(1, len(self.codecs)):
            pos += (self.stride+1) * self.codecs[i-1].getTileSize()
            tile_pixels = self.codecs[i].decode(bits, pos)
            # "overlay" the tile
            for i_pixel in range(64):
                pixels[i_pixel] |= tile_pixels[i_pixel] << shift

            shift += self.codecs[i].getBitsPerPixel()

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

        # encode the first sub-tile
        bits = self.codecs[0].encode(pixels, bits, ofs)
        # encode remaining sub-tiles
        shift = self.codecs[0].getBitsPerPixel()
        pos = ofs
        for i in range(1, len(self.codecs)):
            pos += (self.stride+1) * self.codecs[i-1].getTileSize()
            # shift the tile pixels
            for i_pixel in range(64):
                pixels[i_pixel] >>= shift

            bits = self.codecs[i].encode(pixels, bits, pos)
            shift += self.codecs[i].getBitsPerPixel()

        return bits



class PlanarCompositeCodec(CompositeCodec):
    """
    Creates a CompositeCodec with a predefined list of planar codecs,
    which matches the given bpp value.
    """

    PREDEFINES = {2: [1, 1], 3: [2, 1], 4: [2, 2], 8: [2, 2, 2, 2]}

    def __init__(self, bpp, stride=0):
        if bpp not in self.PREDEFINES:
            raise ValueError("Unknown BPP value. Use CompositeCodec "
                "for custom codecs.")
        codecs = list(PlanarCodec(x) for x in self.PREDEFINES[bpp])
        CompositeCodec.__init__(self, codecs, stride)
