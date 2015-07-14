from tilecodecs.TileCodec import TileCodec
from tilecodecs.PlanarCodec import PlanarCodec
from tilecodecs.LinearCodec import LinearCodec
from tilecodecs._3BPPLinearCodec import _3BPPLinearCodec
from tilecodecs.CompositeCodec import CompositeCodec, PlanarCompositeCodec
from tilecodecs.DirectColorCodec import DirectColorCodec
from tilecodecs.Pixmap import Pixmap

try:
    from tilecodecs import gba
except:
    pass
