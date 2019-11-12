from discord import Colour


class HexColor(Colour):
    """
    Extends discord.py's Colour class -- and changes a few things.
    Colors map to X11 color names: https://en.wikipedia.org/wiki/X11_color_names
    """

    # RED COLORS
    @classmethod
    def indian_red(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xcd5c5c``."""
        return cls(0xCD5C5C)

    @classmethod
    def light_coral(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf08080``."""
        return cls(0xF08080)

    @classmethod
    def salmon(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfa8072``."""
        return cls(0xFA8072)

    @classmethod
    def dark_salmon(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xe9967a``."""
        return cls(0xE9967A)

    @classmethod
    def light_salmon(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffa07a``."""
        return cls(0xFFA07A)

    @classmethod
    def crimson(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xdc143c``."""
        return cls(0xDC143C)

    @classmethod
    def red(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xff0000``."""
        return cls(0xFF0000)

    @classmethod
    def fire_brick(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xb22222``."""
        return cls(0xB22222)

    @classmethod
    def dark_red(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x8b0000``."""
        return cls(0x8B0000)

    # PINK COLORS
    @classmethod
    def pink(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffc0cb``."""
        return cls(0xFFC0CB)

    @classmethod
    def light_pink(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffb6c1``."""
        return cls(0xFFB6C1)

    @classmethod
    def hot_pink(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xff69b4``."""
        return cls(0xFF69B4)

    @classmethod
    def deep_pink(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xff1493``."""
        return cls(0xFF1493)

    @classmethod
    def medium_violet_red(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xc71585``."""
        return cls(0xC71585)

    @classmethod
    def pale_violet_red(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xdb7093``."""
        return cls(0xDB7093)

    # ORANGE COLORS
    @classmethod
    def coral(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xff7f50``."""
        return cls(0xFF7F50)

    @classmethod
    def tomato(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xff6347``."""
        return cls(0xFF6347)

    @classmethod
    def orange_red(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xff4500``."""
        return cls(0xFF4500)

    @classmethod
    def dark_orange(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xff8c00``."""
        return cls(0xFF8C00)

    @classmethod
    def orange(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffa500``."""
        return cls(0xFFA500)

    # YELLOW COLORS
    @classmethod
    def gold(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffd700``."""
        return cls(0xFFD700)

    @classmethod
    def yellow(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffff00``."""
        return cls(0xFFFF00)

    @classmethod
    def light_yellow(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffffe0``."""
        return cls(0xFFFFE0)

    @classmethod
    def lemon_chiffon(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfffacd``."""
        return cls(0xFFFACD)

    @classmethod
    def light_goldenrod_yellow(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfafad2``."""
        return cls(0xFAFAD2)

    @classmethod
    def papaya_whip(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffefd5``."""
        return cls(0xFFEFD5)

    @classmethod
    def moccasin(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffe4b5``."""
        return cls(0xFFE4B5)

    @classmethod
    def peach_puff(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffdab9``."""
        return cls(0xFFDAB9)

    @classmethod
    def pale_goldenrod(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xeee8aa``."""
        return cls(0xEEE8AA)

    @classmethod
    def khaki(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf0e68c``."""
        return cls(0xF0E68C)

    @classmethod
    def dark_khaki(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xbdb76b``."""
        return cls(0xBDB76B)

    # PURPLE COLORS
    @classmethod
    def lavender(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xe6e6fa``."""
        return cls(0xE6E6FA)

    @classmethod
    def thistle(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xd8bfd8``."""
        return cls(0xD8BFD8)

    @classmethod
    def plum(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xdda0dd``."""
        return cls(0xDDA0DD)

    @classmethod
    def violet(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xee82ee``."""
        return cls(0xEE82EE)

    @classmethod
    def orchid(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xda70d6``."""
        return cls(0xDA70D6)

    @classmethod
    def fuchsia(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xff00ff``."""
        return cls(0xFF00FF)

    @classmethod
    def medium_orchid(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xba55d3``."""
        return cls(0xBA55D3)

    @classmethod
    def medium_purple(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x9370db``."""
        return cls(0x9370DB)

    @classmethod
    def rebecca_purple(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x663399``."""
        return cls(0x663399)

    @classmethod
    def blue_violet(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x8a2be2``."""
        return cls(0x8A2BE2)

    @classmethod
    def dark_violet(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x9400d3``."""
        return cls(0x9400D3)

    @classmethod
    def dark_orchid(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x9932cc``."""
        return cls(0x9932CC)

    @classmethod
    def dark_magenta(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x8b008b``."""
        return cls(0x8B008B)

    @classmethod
    def purple(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x800080``."""
        return cls(0x800080)

    @classmethod
    def indigo(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x4b0082``."""
        return cls(0x4B0082)

    @classmethod
    def slate_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x6a5acd``."""
        return cls(0x6A5ACD)

    @classmethod
    def dark_slate_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x483d8b``."""
        return cls(0x483D8B)

    @classmethod
    def medium_slate_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x7b68ee``."""
        return cls(0x7B68EE)

    # GREEN COLORS
    @classmethod
    def green_yellow(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xadff2f``."""
        return cls(0xADFF2F)

    @classmethod
    def chartreuse(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x7fff00``."""
        return cls(0x7FFF00)

    @classmethod
    def lawn_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x7cfc00``."""
        return cls(0x7CFC00)

    @classmethod
    def lime(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x00ff00``."""
        return cls(0x00FF00)

    @classmethod
    def lime_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x32cd32``."""
        return cls(0x32CD32)

    @classmethod
    def pale_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x98fb98``."""
        return cls(0x98FB98)

    @classmethod
    def light_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x90ee90``."""
        return cls(0x90EE90)

    @classmethod
    def medium_spring_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x00fa9a``."""
        return cls(0x00FA9A)

    @classmethod
    def spring_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x00ff7f``."""
        return cls(0x00FF7F)

    @classmethod
    def medium_sea_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x3cb371``."""
        return cls(0x3CB371)

    @classmethod
    def sea_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x2e8b57``."""
        return cls(0x2E8B57)

    @classmethod
    def forest_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x228b22``."""
        return cls(0x228B22)

    @classmethod
    def green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x008000``."""
        return cls(0x008000)

    @classmethod
    def dark_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x006400``."""
        return cls(0x006400)

    @classmethod
    def yellow_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x9acd32``."""
        return cls(0x9ACD32)

    @classmethod
    def olive_drab(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x6b8e23``."""
        return cls(0x6B8E23)

    @classmethod
    def olive(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x808000``."""
        return cls(0x808000)

    @classmethod
    def dark_olive_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x556b2f``."""
        return cls(0x556B2F)

    @classmethod
    def medium_aquamarine(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x66cdaa``."""
        return cls(0x66CDAA)

    @classmethod
    def dark_sea_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x8fbc8b``."""
        return cls(0x8FBC8B)

    @classmethod
    def light_sea_green(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x20b2aa``."""
        return cls(0x20B2AA)

    @classmethod
    def dark_cyan(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x008b8b``."""
        return cls(0x008B8B)

    @classmethod
    def teal(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x008080``."""
        return cls(0x008080)

    # BLUE COLORS
    @classmethod
    def aqua(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x00ffff``."""
        return cls(0x00FFFF)

    @classmethod
    def light_cyan(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xe0ffff``."""
        return cls(0xE0FFFF)

    @classmethod
    def pale_turquoise(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xafeeee``."""
        return cls(0xAFEEEE)

    @classmethod
    def aquamarine(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x7fffd4``."""
        return cls(0x7FFFD4)

    @classmethod
    def turquoise(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x40e0d0``."""
        return cls(0x40E0D0)

    @classmethod
    def medium_turquoise(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x48d1cc``."""
        return cls(0x48D1CC)

    @classmethod
    def dark_turquoise(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x00ced1``."""
        return cls(0x00CED1)

    @classmethod
    def cadet_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x5f9ea0``."""
        return cls(0x5F9EA0)

    @classmethod
    def steel_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x4682b4``."""
        return cls(0x4682B4)

    @classmethod
    def light_steel_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xb0c4de``."""
        return cls(0xB0C4DE)

    @classmethod
    def powder_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xb0e0e6``."""
        return cls(0xB0E0E6)

    @classmethod
    def light_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xadd8e6``."""
        return cls(0xADD8E6)

    @classmethod
    def sky_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x87ceeb``."""
        return cls(0x87CEEB)

    @classmethod
    def light_sky_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x87cefa``."""
        return cls(0x87CEFA)

    @classmethod
    def deep_sky_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x00bfff``."""
        return cls(0x00BFFF)

    @classmethod
    def dodger_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x1e90ff``."""
        return cls(0x1E90FF)

    @classmethod
    def cornflower_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x6495ed``."""
        return cls(0x6495ED)

    @classmethod
    def royal_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x4169e1``."""
        return cls(0x4169E1)

    @classmethod
    def blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x0000ff``."""
        return cls(0x0000FF)

    @classmethod
    def medium_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x0000cd``."""
        return cls(0x0000CD)

    @classmethod
    def dark_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x00008b``."""
        return cls(0x00008B)

    @classmethod
    def navy(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x000080``."""
        return cls(0x000080)

    @classmethod
    def midnight_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x191970``."""
        return cls(0x191970)

    # BROWN COLORS
    @classmethod
    def cornsilk(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfff8dc``."""
        return cls(0xFFF8DC)

    @classmethod
    def blanched_almond(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffebcd``."""
        return cls(0xFFEBCD)

    @classmethod
    def bisque(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffe4c4``."""
        return cls(0xFFE4C4)

    @classmethod
    def navajo_white(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffdead``."""
        return cls(0xFFDEAD)

    @classmethod
    def wheat(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf5deb3``."""
        return cls(0xF5DEB3)

    @classmethod
    def burly_wood(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xdeb887``."""
        return cls(0xDEB887)

    @classmethod
    def tan(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xd2b48c``."""
        return cls(0xD2B48C)

    @classmethod
    def rosy_brown(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xbc8f8f``."""
        return cls(0xBC8F8F)

    @classmethod
    def sandy_brown(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf4a460``."""
        return cls(0xF4A460)

    @classmethod
    def goldenrod(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xdaa520``."""
        return cls(0xDAA520)

    @classmethod
    def dark_goldenrod(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xb8860b``."""
        return cls(0xB8860B)

    @classmethod
    def peru(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xcd853f``."""
        return cls(0xCD853F)

    @classmethod
    def chocolate(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xd2691e``."""
        return cls(0xD2691E)

    @classmethod
    def saddle_brown(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x8b4513``."""
        return cls(0x8B4513)

    @classmethod
    def sienna(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xa0522d``."""
        return cls(0xA0522D)

    @classmethod
    def brown(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xa52a2a``."""
        return cls(0xA52A2A)

    @classmethod
    def maroon(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x800000``."""
        return cls(0x800000)

    # WHITE COLORS
    @classmethod
    def white(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffffff``."""
        return cls(0xFFFFFF)

    @classmethod
    def snow(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfffafa``."""
        return cls(0xFFFAFA)

    @classmethod
    def honey_dew(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf0fff0``."""
        return cls(0xF0FFF0)

    @classmethod
    def mint_cream(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf5fffa``."""
        return cls(0xF5FFFA)

    @classmethod
    def azure(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf0ffff``."""
        return cls(0xF0FFFF)

    @classmethod
    def alice_blue(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf0f8ff``."""
        return cls(0xF0F8FF)

    @classmethod
    def ghost_white(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf8f8ff``."""
        return cls(0xF8F8FF)

    @classmethod
    def white_smoke(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf5f5f5``."""
        return cls(0xF5F5F5)

    @classmethod
    def sea_shell(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfff5ee``."""
        return cls(0xFFF5EE)

    @classmethod
    def beige(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xf5f5dc``."""
        return cls(0xF5F5DC)

    @classmethod
    def old_lace(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfdf5e6``."""
        return cls(0xFDF5E6)

    @classmethod
    def floral_white(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfffaf0``."""
        return cls(0xFFFAF0)

    @classmethod
    def ivory(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfffff0``."""
        return cls(0xFFFFF0)

    @classmethod
    def antique_white(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfaebd7``."""
        return cls(0xFAEBD7)

    @classmethod
    def linen(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfaf0e6``."""
        return cls(0xFAF0E6)

    @classmethod
    def lavender_blush(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xfff0f5``."""
        return cls(0xFFF0F5)

    @classmethod
    def misty_rose(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xffe4e1``."""
        return cls(0xFFE4E1)

    # GRAY COLORS
    @classmethod
    def gainsboro(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xdcdcdc``."""
        return cls(0xDCDCDC)

    @classmethod
    def light_gray(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xd3d3d3``."""
        return cls(0xD3D3D3)

    @classmethod
    def silver(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xc0c0c0``."""
        return cls(0xC0C0C0)

    @classmethod
    def dark_gray(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0xa9a9a9``."""
        return cls(0xA9A9A9)

    @classmethod
    def gray(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x808080``."""
        return cls(0x808080)

    @classmethod
    def dim_gray(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x696969``."""
        return cls(0x696969)

    @classmethod
    def light_slate_gray(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x778899``."""
        return cls(0x778899)

    @classmethod
    def slate_gray(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x708090``."""
        return cls(0x708090)

    @classmethod
    def dark_slate_gray(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x2f4f4f``."""
        return cls(0x2F4F4F)

    @classmethod
    def black(cls):
        """A factory method that returns a :class:`HexColor` with a value of ``0x000000``."""
        return cls(0x000000)

    # COMMON MAPPINGS
    @staticmethod
    def success():
        return HexColor.lime()

    @staticmethod
    def error():
        return HexColor.red()

    @staticmethod
    def warning():
        return HexColor.gold()

    @staticmethod
    def info():
        return HexColor.deep_sky_blue()
