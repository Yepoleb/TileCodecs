from PIL import Image
import struct
import math

# Palette functions

PALETTE_FMT = "<16H"
PALETTE_SIZE = struct.calcsize(PALETTE_FMT)

def decode_color(color, alpha=False):
    """
    Decodes a 16bit int into its RGB components. If alpha is set to true, a
    transparency value is appended and set to 255. This can be used for images
    where one color is transparent and you have to use RGBA mode.
    """
    # The 3 left shifts scale the 5bit values to 8bit
    r = ((color >>  0) & 0b11111) << 3
    g = ((color >>  5) & 0b11111) << 3
    b = ((color >> 10) & 0b11111) << 3

    if alpha:
        return (r, g, g, 255)
    else:
        return (r, g, b)

def encode_color(rgb):
    """
    Encodes RGB components into a 16bit int value. Alpha values get stripped
    automatically.
    """
    if not all(0 <= c <= 255 for c in rgb):
        raise ValueError("RGB values have to be in range 0-255")

    r, g, b = rgb[:3] # strip alpha
    color = 0
    color |= ((r >> 3) & 0b11111) << 0
    color |= ((g >> 3) & 0b11111) << 5
    color |= ((b >> 3) & 0b11111) << 10
    return color

def decode_palette(data, alpha=False):
    """
    Decodes a 16 color palette into rgb(a) tuples.

    Arguments:
    data - A bytes-like object of encoded palette data
    alpha - If set to true, the first color is transparent and all tuples
            contain an alpha value
    """
    palette_colors = struct.unpack(PALETTE_FMT, data)
    palette_rgb = list(decode_color(c, alpha) for c in palette_colors)
    if alpha:
        palette_rgb[0] = (0,0,0,0) # Set alpha channel of first color
    return palette_rgb

def encode_palette(palette):
    """
    Encodes 16 rgb tuples into a palette. Alpha values get stripped
    automatically by the encode_color function.
    """
    if len(palette) != 16:
        raise ValueError("Palettes have to contain 16 colors")

    colors_encoded = (encode_color(c) for c in palette)
    palette_data = struct.pack(PALETTE_FMT, *colors_encoded)
    return palette_data

def iter_decode_palettes(data, alpha=False):
    """
    Decodes multiple palettes
    """
    if len(data) % PALETTE_SIZE != 0:
        raise ValueError("Data length has to be a multiple of PALETTE_SIZE")

    for i in range(0, len(data), PALETTE_SIZE):
        yield decode_palette(data[i:i+PALETTE_SIZE], alpha)

def iter_encode_palettes(palettes):
    """
    Encodes multiple palettes into a single bytearray.
    """
    data = bytearray()
    for pal in palettes:
        data += encode_palette(pal)
    return data


# Tile functions

def iter_decode_tiles(codec, data):
    """
    Decodes multiple tiles from a bytes-like object
    """
    for i in range(0, len(data), codec.getTileSize()):
        yield codec.decode(data, i)

def iter_encode_tiles(codec, tiles):
    """
    Encodes multiple tiles into a new bytearray
    """
    data = bytearray()
    for tile in tiles:
        data += codec.encode(tile)
    return data

def color_tile(tile, palette):
    """
    Replaces the pixel values with the colors from the palette
    """
    return [palette[c] for c in tile]

def iter_color_tiles(tiles, palette):
    """
    Colors multiple tiles
    """
    for tile in tiles:
        yield color_tile(tile, palette)

def tile_image(raw, alpha=False):
    """
    Creates a PIL Image from a colored tile
    """
    if alpha:
        mode = "RGBA"
    else:
        mode = "RGB"
    tile = Image.new(mode, (8,8))
    tile.putdata(raw)
    return tile

def iter_tile_images(raw, alpha=False):
    """
    Creates Images for multiple tiles
    """
    for raw_tile in raw:
        yield tile_image(raw_tile, alpha)

def combine_tiles(tiles, width):
    """
    Combines multiple tiles into a big image. The width is meassured in tiles,
    the height is calculated automatically.
    """
    height = int(math.ceil(len(tiles) / width))
    img = Image.new("RGBA", (width*8, height*8))
    for tile_i in range(len(tiles)):
        x = (tile_i % width) * 8
        y = (tile_i // width) * 8
        img.paste(tiles[tile_i], (x,y))

    return img

def decode_image(data, codec, palette, width):
    """
    Calls each tile function to decode a complete image.
    """
    raw_tiles = iter_decode_tiles(codec, data)
    colored_tiles = iter_color_tiles(raw_tiles, palette)
    img_tiles = iter_tile_images(colored_tiles)
    img = combine_tiles(tuple(img_tiles), width)
    return img

def decode_tilemap(tilemap, tiles, palettes):
    """
    Creates a list of colored tiles from a tilemap, raw tiles and a
    color palette
    """
    tilemap_tiles = []

    for char in struct.iter_unpack("<H", tilemap):
        char = char[0]
        # Layout: Section 9.3 at http://www.coranac.com/tonc/text/regbg.htm
        tile_id = char & ((1 << 10) - 1)
        flip_h = bool(char & (1 << 10))
        flip_v = bool(char & (1 << 11))
        pal_id = char >> 12

        pal = palettes[pal_id]
        tile = color_tile(tiles[tile_id], pal)
        tile_img = tile_image(tile)
        if flip_h:
            tile_img = tile_img.transpose(Image.FLIP_LEFT_RIGHT)
        if flip_v:
            tile_img = tile_img.transpose(Image.FLIP_TOP_BOTTOM)

        tilemap_tiles.append(tile_img)

    return tilemap_tiles
