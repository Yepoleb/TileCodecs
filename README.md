#TileCodecs
Python library for decoding retro console images. The codecs are ported from Tile Molester.

##Installation
Clone and run
`# python3 setup.py install`

##Credits
Kent Hansen (SnowBro) - He created the original java codecs, which this library is based on.

##Example
```python
from tilecodecs import LinearCodec
from PIL import Image

data = b"\x12\x34\x56\x78" * 16
palette = [(0x00, 0x00, 0x00), (0xA0, 0x40, 0x20), (0xD0, 0xA0, 0x50), (0xF0, 0xF0, 0x80)]

codec = LinearCodec(2, LinearCodec.REVERSE_ORDER)

tiles = []
for i in range(0, len(data), codec.getTileSize()):
    tile_raw = codec.decode(data, i)
    tile_colored = []
    for pixel in tile_raw:
        tile_colored.append(palette[pixel])
    tile_img = Image.new("RGB", (8,8))
    tile_img.putdata(tile_colored)
    tiles.append(tile_img)

img = Image.new("RGB", (16,16))
img.paste(tiles[0], (0,0))
img.paste(tiles[1], (8,0))
img.paste(tiles[2], (0,8))
img.paste(tiles[3], (8,8))

img.save("example.png")
```


