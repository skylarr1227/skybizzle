from seplib.tests.data.hexcolors import HexColors
from seplib.utils import HexColor


class TestHexColor(object):
    def test_indian_red(self):
        assert HexColor.indian_red().value == HexColors.IndianRed.value

    def test_light_coral(self):
        assert HexColor.light_coral().value == HexColors.LightCoral.value

    def test_salmon(self):
        assert HexColor.salmon().value == HexColors.Salmon.value

    def test_dark_salmon(self):
        assert HexColor.dark_salmon().value == HexColors.DarkSalmon.value

    def test_light_salmon(self):
        assert HexColor.light_salmon().value == HexColors.LightSalmon.value

    def test_crimson(self):
        assert HexColor.crimson().value == HexColors.Crimson.value

    def test_red(self):
        assert HexColor.red().value == HexColors.Red.value

    def test_fire_brick(self):
        assert HexColor.fire_brick().value == HexColors.FireBrick.value

    def test_dark_red(self):
        assert HexColor.dark_red().value == HexColors.DarkRed.value

    def test_pink(self):
        assert HexColor.pink().value == HexColors.Pink.value

    def test_light_pink(self):
        assert HexColor.light_pink().value == HexColors.LightPink.value

    def test_hot_pink(self):
        assert HexColor.hot_pink().value == HexColors.HotPink.value

    def test_deep_pink(self):
        assert HexColor.deep_pink().value == HexColors.DeepPink.value

    def test_medium_violet_red(self):
        assert HexColor.medium_violet_red().value == HexColors.MediumVioletRed.value

    def test_pale_violet_red(self):
        assert HexColor.pale_violet_red().value == HexColors.PaleVioletRed.value

    def test_coral(self):
        assert HexColor.coral().value == HexColors.Coral.value

    def test_tomato(self):
        assert HexColor.tomato().value == HexColors.Tomato.value

    def test_orange_red(self):
        assert HexColor.orange_red().value == HexColors.OrangeRed.value

    def test_dark_orange(self):
        assert HexColor.dark_orange().value == HexColors.DarkOrange.value

    def test_orange(self):
        assert HexColor.orange().value == HexColors.Orange.value

    def test_gold(self):
        assert HexColor.gold().value == HexColors.Gold.value

    def test_yellow(self):
        assert HexColor.yellow().value == HexColors.Yellow.value

    def test_light_yellow(self):
        assert HexColor.light_yellow().value == HexColors.LightYellow.value

    def test_lemon_chiffon(self):
        assert HexColor.lemon_chiffon().value == HexColors.LemonChiffon.value

    def test_light_goldenrod_yellow(self):
        assert HexColor.light_goldenrod_yellow().value == HexColors.LightGoldenrodYellow.value

    def test_papaya_whip(self):
        assert HexColor.papaya_whip().value == HexColors.PapayaWhip.value

    def test_moccasin(self):
        assert HexColor.moccasin().value == HexColors.Moccasin.value

    def test_peach_puff(self):
        assert HexColor.peach_puff().value == HexColors.PeachPuff.value

    def test_pale_goldenrod(self):
        assert HexColor.pale_goldenrod().value == HexColors.PaleGoldenrod.value

    def test_khaki(self):
        assert HexColor.khaki().value == HexColors.Khaki.value

    def test_dark_khaki(self):
        assert HexColor.dark_khaki().value == HexColors.DarkKhaki.value

    def test_lavender(self):
        assert HexColor.lavender().value == HexColors.Lavender.value

    def test_thistle(self):
        assert HexColor.thistle().value == HexColors.Thistle.value

    def test_plum(self):
        assert HexColor.plum().value == HexColors.Plum.value

    def test_violet(self):
        assert HexColor.violet().value == HexColors.Violet.value

    def test_orchid(self):
        assert HexColor.orchid().value == HexColors.Orchid.value

    def test_fuchsia(self):
        assert HexColor.fuchsia().value == HexColors.Fuchsia.value

    def test_medium_orchid(self):
        assert HexColor.medium_orchid().value == HexColors.MediumOrchid.value

    def test_medium_purple(self):
        assert HexColor.medium_purple().value == HexColors.MediumPurple.value

    def test_rebecca_purple(self):
        assert HexColor.rebecca_purple().value == HexColors.RebeccaPurple.value

    def test_blue_violet(self):
        assert HexColor.blue_violet().value == HexColors.BlueViolet.value

    def test_dark_violet(self):
        assert HexColor.dark_violet().value == HexColors.DarkViolet.value

    def test_dark_orchid(self):
        assert HexColor.dark_orchid().value == HexColors.DarkOrchid.value

    def test_dark_magenta(self):
        assert HexColor.dark_magenta().value == HexColors.DarkMagenta.value

    def test_purple(self):
        assert HexColor.purple().value == HexColors.Purple.value

    def test_indigo(self):
        assert HexColor.indigo().value == HexColors.Indigo.value

    def test_slate_blue(self):
        assert HexColor.slate_blue().value == HexColors.SlateBlue.value

    def test_dark_slate_blue(self):
        assert HexColor.dark_slate_blue().value == HexColors.DarkSlateBlue.value

    def test_medium_slate_blue(self):
        assert HexColor.medium_slate_blue().value == HexColors.MediumSlateBlue.value

    def test_green_yellow(self):
        assert HexColor.green_yellow().value == HexColors.GreenYellow.value

    def test_chartreuse(self):
        assert HexColor.chartreuse().value == HexColors.Chartreuse.value

    def test_lawn_green(self):
        assert HexColor.lawn_green().value == HexColors.LawnGreen.value

    def test_lime(self):
        assert HexColor.lime().value == HexColors.Lime.value

    def test_lime_green(self):
        assert HexColor.lime_green().value == HexColors.LimeGreen.value

    def test_pale_green(self):
        assert HexColor.pale_green().value == HexColors.PaleGreen.value

    def test_light_green(self):
        assert HexColor.light_green().value == HexColors.LightGreen.value

    def test_medium_spring_green(self):
        assert HexColor.medium_spring_green().value == HexColors.MediumSpringGreen.value

    def test_spring_green(self):
        assert HexColor.spring_green().value == HexColors.SpringGreen.value

    def test_medium_sea_green(self):
        assert HexColor.medium_sea_green().value == HexColors.MediumSeaGreen.value

    def test_sea_green(self):
        assert HexColor.sea_green().value == HexColors.SeaGreen.value

    def test_forest_green(self):
        assert HexColor.forest_green().value == HexColors.ForestGreen.value

    def test_green(self):
        assert HexColor.green().value == HexColors.Green.value

    def test_dark_green(self):
        assert HexColor.dark_green().value == HexColors.DarkGreen.value

    def test_yellow_green(self):
        assert HexColor.yellow_green().value == HexColors.YellowGreen.value

    def test_olive_drab(self):
        assert HexColor.olive_drab().value == HexColors.OliveDrab.value

    def test_olive(self):
        assert HexColor.olive().value == HexColors.Olive.value

    def test_dark_olive_green(self):
        assert HexColor.dark_olive_green().value == HexColors.DarkOliveGreen.value

    def test_medium_aquamarine(self):
        assert HexColor.medium_aquamarine().value == HexColors.MediumAquamarine.value

    def test_dark_sea_green(self):
        assert HexColor.dark_sea_green().value == HexColors.DarkSeaGreen.value

    def test_light_sea_green(self):
        assert HexColor.light_sea_green().value == HexColors.LightSeaGreen.value

    def test_dark_cyan(self):
        assert HexColor.dark_cyan().value == HexColors.DarkCyan.value

    def test_teal(self):
        assert HexColor.teal().value == HexColors.Teal.value

    def test_aqua(self):
        assert HexColor.aqua().value == HexColors.Aqua.value

    def test_light_cyan(self):
        assert HexColor.light_cyan().value == HexColors.LightCyan.value

    def test_pale_turquoise(self):
        assert HexColor.pale_turquoise().value == HexColors.PaleTurquoise.value

    def test_aquamarine(self):
        assert HexColor.aquamarine().value == HexColors.Aquamarine.value

    def test_turquoise(self):
        assert HexColor.turquoise().value == HexColors.Turquoise.value

    def test_medium_turquoise(self):
        assert HexColor.medium_turquoise().value == HexColors.MediumTurquoise.value

    def test_dark_turquoise(self):
        assert HexColor.dark_turquoise().value == HexColors.DarkTurquoise.value

    def test_cadet_blue(self):
        assert HexColor.cadet_blue().value == HexColors.CadetBlue.value

    def test_steel_blue(self):
        assert HexColor.steel_blue().value == HexColors.SteelBlue.value

    def test_light_steel_blue(self):
        assert HexColor.light_steel_blue().value == HexColors.LightSteelBlue.value

    def test_powder_blue(self):
        assert HexColor.powder_blue().value == HexColors.PowderBlue.value

    def test_light_blue(self):
        assert HexColor.light_blue().value == HexColors.LightBlue.value

    def test_sky_blue(self):
        assert HexColor.sky_blue().value == HexColors.SkyBlue.value

    def test_light_sky_blue(self):
        assert HexColor.light_sky_blue().value == HexColors.LightSkyBlue.value

    def test_deep_sky_blue(self):
        assert HexColor.deep_sky_blue().value == HexColors.DeepSkyBlue.value

    def test_dodger_blue(self):
        assert HexColor.dodger_blue().value == HexColors.DodgerBlue.value

    def test_cornflower_blue(self):
        assert HexColor.cornflower_blue().value == HexColors.CornflowerBlue.value

    def test_royal_blue(self):
        assert HexColor.royal_blue().value == HexColors.RoyalBlue.value

    def test_blue(self):
        assert HexColor.blue().value == HexColors.Blue.value

    def test_medium_blue(self):
        assert HexColor.medium_blue().value == HexColors.MediumBlue.value

    def test_dark_blue(self):
        assert HexColor.dark_blue().value == HexColors.DarkBlue.value

    def test_navy(self):
        assert HexColor.navy().value == HexColors.Navy.value

    def test_midnight_blue(self):
        assert HexColor.midnight_blue().value == HexColors.MidnightBlue.value

    def test_cornsilk(self):
        assert HexColor.cornsilk().value == HexColors.Cornsilk.value

    def test_blanched_almond(self):
        assert HexColor.blanched_almond().value == HexColors.BlanchedAlmond.value

    def test_bisque(self):
        assert HexColor.bisque().value == HexColors.Bisque.value

    def test_navajo_white(self):
        assert HexColor.navajo_white().value == HexColors.NavajoWhite.value

    def test_wheat(self):
        assert HexColor.wheat().value == HexColors.Wheat.value

    def test_burly_wood(self):
        assert HexColor.burly_wood().value == HexColors.BurlyWood.value

    def test_tan(self):
        assert HexColor.tan().value == HexColors.Tan.value

    def test_rosy_brown(self):
        assert HexColor.rosy_brown().value == HexColors.RosyBrown.value

    def test_sandy_brown(self):
        assert HexColor.sandy_brown().value == HexColors.SandyBrown.value

    def test_goldenrod(self):
        assert HexColor.goldenrod().value == HexColors.Goldenrod.value

    def test_dark_goldenrod(self):
        assert HexColor.dark_goldenrod().value == HexColors.DarkGoldenrod.value

    def test_peru(self):
        assert HexColor.peru().value == HexColors.Peru.value

    def test_chocolate(self):
        assert HexColor.chocolate().value == HexColors.Chocolate.value

    def test_saddle_brown(self):
        assert HexColor.saddle_brown().value == HexColors.SaddleBrown.value

    def test_sienna(self):
        assert HexColor.sienna().value == HexColors.Sienna.value

    def test_brown(self):
        assert HexColor.brown().value == HexColors.Brown.value

    def test_maroon(self):
        assert HexColor.maroon().value == HexColors.Maroon.value

    def test_white(self):
        assert HexColor.white().value == HexColors.White.value

    def test_snow(self):
        assert HexColor.snow().value == HexColors.Snow.value

    def test_honey_dew(self):
        assert HexColor.honey_dew().value == HexColors.HoneyDew.value

    def test_mint_cream(self):
        assert HexColor.mint_cream().value == HexColors.MintCream.value

    def test_azure(self):
        assert HexColor.azure().value == HexColors.Azure.value

    def test_alice_blue(self):
        assert HexColor.alice_blue().value == HexColors.AliceBlue.value

    def test_ghost_white(self):
        assert HexColor.ghost_white().value == HexColors.GhostWhite.value

    def test_white_smoke(self):
        assert HexColor.white_smoke().value == HexColors.WhiteSmoke.value

    def test_sea_shell(self):
        assert HexColor.sea_shell().value == HexColors.SeaShell.value

    def test_beige(self):
        assert HexColor.beige().value == HexColors.Beige.value

    def test_old_lace(self):
        assert HexColor.old_lace().value == HexColors.OldLace.value

    def test_floral_white(self):
        assert HexColor.floral_white().value == HexColors.FloralWhite.value

    def test_ivory(self):
        assert HexColor.ivory().value == HexColors.Ivory.value

    def test_antique_white(self):
        assert HexColor.antique_white().value == HexColors.AntiqueWhite.value

    def test_linen(self):
        assert HexColor.linen().value == HexColors.Linen.value

    def test_lavender_blush(self):
        assert HexColor.lavender_blush().value == HexColors.LavenderBlush.value

    def test_misty_rose(self):
        assert HexColor.misty_rose().value == HexColors.MistyRose.value

    def test_gainsboro(self):
        assert HexColor.gainsboro().value == HexColors.Gainsboro.value

    def test_light_gray(self):
        assert HexColor.light_gray().value == HexColors.LightGray.value

    def test_silver(self):
        assert HexColor.silver().value == HexColors.Silver.value

    def test_dark_gray(self):
        assert HexColor.dark_gray().value == HexColors.DarkGray.value

    def test_gray(self):
        assert HexColor.gray().value == HexColors.Gray.value

    def test_dim_gray(self):
        assert HexColor.dim_gray().value == HexColors.DimGray.value

    def test_light_slate_gray(self):
        assert HexColor.light_slate_gray().value == HexColors.LightSlateGray.value

    def test_slate_gray(self):
        assert HexColor.slate_gray().value == HexColors.SlateGray.value

    def test_dark_slate_gray(self):
        assert HexColor.dark_slate_gray().value == HexColors.DarkSlateGray.value

    def test_black(self):
        assert HexColor.black().value == HexColors.Black.value

    def test_success(self):
        assert HexColor.success().value == HexColor.lime().value

    def test_error(self):
        assert HexColor.error().value == HexColor.red().value

    def test_warning(self):
        assert HexColor.warning().value == HexColor.gold().value

    def test_info(self):
        assert HexColor.info().value == HexColor.deep_sky_blue().value
