#TileCodecs
Python library of ported Tile Molester image codecs. Currently only contains the LinearTileCodec.

##Install
Copy this folder into your project root. (If this repo gets 3 stars, I'll add a proper install script :wink:)

##Credits
Kent Hansen (SnowBro) - He created the original java codecs, which this library is based on.

##Example
```python
from TileCodecs import LinearTileCodec
from PIL import Image

data = b"\x12\x34\x56\x78" * 8
palette = [(0x00, 0x00, 0x00), (0xA0, 0x40, 0x20), (0xD0, 0xA0, 0x50), (0xF0, 0xF0, 0x80)]

codec = LinearTileCodec(2, LinearTileCodec.REVERSE_ORDER)

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
img.paste(tiles[0], (8,0))
img.paste(tiles[0], (0,8))
img.paste(tiles[0], (8,8))

img.save("example.png")
```

