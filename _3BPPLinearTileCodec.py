from TileCodecs import TileCodec

class _3BPPLinearTileCodec(TileCodec):

    def __init__(self, stride=0):
        """
        Constructor for 3BPPLinearTileCodec
        
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
            b1 = bits[pos+0] # byte 1: 0001 1122
            b2 = bits[pos+1] # byte 2: 2333 4445
            b3 = bits[pos+2] # byte 3: 5566 6777
            pixels.append((b1 >> 5) & 7)
            pixels.append((b1 >> 2) & 7)
            pixels.append(((b1 & 3) << 1) | ((b2 >> 7) & 1))
            pixels.append((b2 >> 4) & 7)
            pixels.append((b2 >> 1) & 7)
            pixels.append(((b2 & 1) << 2) | ((b3 >> 6) & 3))
            pixels.append((b3 >> 3) & 7)
            pixels.append(b3 & 7)

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
        
        self.checkBitLength(bits, ofs)
        
        for i_row in range(8):
            # do one row
            pos = i_row * self.bytes_per_row + i_row * self.stride
            pxpos = i_row * 8
            b1 = (pixels[pxpos+0] & 7) << 5
            b1 |= (pixels[pxpos+1] & 7) << 2
            b1 |= (pixels[pxpos+1] & 6) >> 1
            b2 = (pixels[pxpos+2] & 1) << 7
            b2 |= (pixels[pxpos+3] & 7) << 4
            b2 |= (pixels[pxpos+4] & 7) << 1
            b2 |= (pixels[pxpos+4] & 4) >> 2
            b3 = (pixels[pxpos+5] & 3) << 6
            b3 |= (pixels[pxpos+6] & 7) << 3
            b3 |= (pixels[pxpos+7] & 7)
            bits[pos+0] = b1; # byte 1: 0001 1122
            bits[pos+1] = b2; # byte 2: 2333 4445
            bits[pos+2] = b3; # byte 3: 5566 6777
        
        return bits
