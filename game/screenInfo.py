import math
from dataclasses import dataclass

@dataclass
class ScreenInfo:
    width: int
    height: int

    @property
    def ratio(self):
        gcd = math.gcd(self.width, self.height)
        return (self.width // gcd, self.height // gcd)

    def scaleWidth(self, value: int|float|tuple):
        return self._scale(value, self.width, 1920, 1680)

    def scaleHeight(self, value: int|float|tuple):
        return self._scale(value, self.height, 1080, 1050)

    def _scale(self, value, dimension, base16_9, base8_5):
        if isinstance(value, tuple):
            if len(value) == 2:
                v16_9, v8_5 = value
            elif len(value) == 3:
                v16_9 = value[0] + (value[2][0] if isinstance(value[2], tuple) else value[2])
                v8_5 = value[1] + (value[2][1] if isinstance(value[2], tuple) else value[2])
        else:
            v16_9 = v8_5 = value

        if self.ratio == (8, 5):
            if not isinstance(value, tuple): base8_5 = base16_9
            return int(v8_5 / base8_5 * dimension)
        
        return int(v16_9 / base16_9 * dimension)