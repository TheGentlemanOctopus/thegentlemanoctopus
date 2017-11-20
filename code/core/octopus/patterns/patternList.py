from shambalaPattern import ShambalaPattern

from simplePattern import SimplePattern
from rpcTestPattern import RpcTestPattern
from eqPattern import EqPattern
from rainbowPlaidPattern import RainbowPlaidPattern
from rainbowPlaidEqPattern import RainbowPlaidEqPattern
from spiralOutFast import SpiralOutFast
from spiralInFast import SpiralInFast
from lavaLampPattern import LavaLampPattern
from lavaLampPattern2 import LavaLampPattern2
from carouselPattern import CarouselPattern
from eqPatternColourful import EqPatternColourful


patterns = [
    ShambalaPattern(),
    EqPattern(),
    SpiralInFast(),
    SpiralOutFast(),
    LavaLampPattern(),
    RpcTestPattern(),
    RainbowPlaidEqPattern(),
    LavaLampPattern2(),
    CarouselPattern(),
    EqPatternColourful()
]

pattern_dict = {}
for pattern in patterns:
    pattern_dict[pattern.__class__.__name__] = pattern