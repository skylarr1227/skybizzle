from fontTools.misc.py23 import *
from fontTools.misc import sstruct
from fontTools.misc.textTools import safeEval, num2binary, binary2num
from fontTools.ttLib.tables import DefaultTable
import logging


log = logging.getLogger(__name__)

# panose classification

panoseFormat = """
	bFamilyType:        B
	bSerifStyle:        B
	bWeight:            B
	bProportion:        B
	bContrast:          B
	bStrokeVariation:   B
	bArmStyle:          B
	bLetterForm:        B
	bMidline:           B
	bXHeight:           B
"""

class Panose(object):

	def toXML(self, writer, ttFont):
		formatstring, names, fixes = sstruct.getformat(panoseFormat)
		for name in names:
			writer.simpletag(name, value=getattr(self, name))
			writer.newline()

	def fromXML(self, name, attrs, content, ttFont):
		setattr(self, name, safeEval(attrs["value"]))


# 'sfnt' OS/2 and Windows Metrics table - 'OS/2'

OS2_format_0 = """
	>   # big endian
	version:                H       # version
	xAvgCharWidth:          h       # average character width
	usWeightClass:          H       # degree of thickness of strokes
	usWidthClass:           H       # aspect ratio
	fsType:                 H       # type flags
	ySubscriptXSize:        h       # subscript horizontal font size
	ySubscriptYSize:        h       # subscript vertical font size
	ySubscriptXOffset:      h       # subscript x offset
	ySubscriptYOffset:      h       # subscript y offset
	ySuperscriptXSize:      h       # superscript horizontal font size
	ySuperscriptYSize:      h       # superscript vertical font size
	ySuperscriptXOffset:    h       # superscript x offset
	ySuperscriptYOffset:    h       # superscript y offset
	yStrikeoutSize:         h       # strikeout size
	yStrikeoutPosition:     h       # strikeout position
	sFamilyClass:           h       # font family class and subclass
	panose:                 10s     # panose classification number
	ulUnicodeRange1:        L       # character range
	ulUnicodeRange2:        L       # character range
	ulUnicodeRange3:        L       # character range
	ulUnicodeRange4:        L       # character range
	achVendID:              4s      # font vendor identification
	fsSelection:            H       # font selection flags
	usFirstCharIndex:       H       # first unicode character index
	usLastCharIndex:        H       # last unicode character index
	sTypoAscender:          h       # typographic ascender
	sTypoDescender:         h       # typographic descender
	sTypoLineGap:           h       # typographic line gap
	usWinAscent:            H       # Windows ascender
	usWinDescent:           H       # Windows descender
"""

OS2_format_1_addition =  """
	ulCodePageRange1:   L
	ulCodePageRange2:   L
"""

OS2_format_2_addition =  OS2_format_1_addition + """
	sxHeight:           h
	sCapHeight:         h
	usDefaultChar:      H
	usBreakChar:        H
	usMaxContext:       H
"""

OS2_format_5_addition =  OS2_format_2_addition + """
	usLowerOpticalPointSize:    H
	usUpperOpticalPointSize:    H
"""

bigendian = "	>	# big endian\n"

OS2_format_1 = OS2_format_0 + OS2_format_1_addition
OS2_format_2 = OS2_format_0 + OS2_format_2_addition
OS2_format_5 = OS2_format_0 + OS2_format_5_addition
OS2_format_1_addition = bigendian + OS2_format_1_addition
OS2_format_2_addition = bigendian + OS2_format_2_addition
OS2_format_5_addition = bigendian + OS2_format_5_addition


class table_O_S_2f_2(DefaultTable.DefaultTable):

	"""the OS/2 table"""

	dependencies = ["head"]

	def decompile(self, data, ttFont):
		dummy, data = sstruct.unpack2(OS2_format_0, data, self)

		if self.version == 1:
			dummy, data = sstruct.unpack2(OS2_format_1_addition, data, self)
		elif self.version in (2, 3, 4):
			dummy, data = sstruct.unpack2(OS2_format_2_addition, data, self)
		elif self.version == 5:
			dummy, data = sstruct.unpack2(OS2_format_5_addition, data, self)
			self.usLowerOpticalPointSize /= 20
			self.usUpperOpticalPointSize /= 20
		elif self.version != 0:
			from fontTools import ttLib
			raise ttLib.TTLibError("unknown format for OS/2 table: version %s" % self.version)
		if len(data):
			log.warning("too much 'OS/2' table data")

		self.panose = sstruct.unpack(panoseFormat, self.panose, Panose())

	def compile(self, ttFont):
		self.updateFirstAndLastCharIndex(ttFont)
		panose = self.panose
		head = ttFont["head"]
		if (self.fsSelection & 1) and not (head.macStyle & 1<<1):
			log.warning("fsSelection bit 0 (italic) and "
				"head table macStyle bit 1 (italic) should match")
		if (self.fsSelection & 1<<5) and not (head.macStyle & 1):
			log.warning("fsSelection bit 5 (bold) and "
				"head table macStyle bit 0 (bold) should match")
		if (self.fsSelection & 1<<6) and (self.fsSelection & 1 + (1<<5)):
			log.warning("fsSelection bit 6 (regular) is set, "
				"bits 0 (italic) and 5 (bold) must be clear")
		if self.version < 4 and self.fsSelection & 0b1110000000:
			log.warning("fsSelection bits 7, 8 and 9 are only defined in "
				"OS/2 table version 4 and up: version %s", self.version)
		self.panose = sstruct.pack(panoseFormat, self.panose)
		if self.version == 0:
			data = sstruct.pack(OS2_format_0, self)
		elif self.version == 1:
			data = sstruct.pack(OS2_format_1, self)
		elif self.version in (2, 3, 4):
			data = sstruct.pack(OS2_format_2, self)
		elif self.version == 5:
			d = self.__dict__.copy()
			d['usLowerOpticalPointSize'] = round(self.usLowerOpticalPointSize * 20)
			d['usUpperOpticalPointSize'] = round(self.usUpperOpticalPointSize * 20)
			data = sstruct.pack(OS2_format_5, d)
		else:
			from fontTools import ttLib
			raise ttLib.TTLibError("unknown format for OS/2 table: version %s" % self.version)
		self.panose = panose
		return data

	def toXML(self, writer, ttFont):
		writer.comment(
			"The fields 'usFirstCharIndex' and 'usLastCharIndex'\n"
			"will be recalculated by the compiler")
		writer.newline()
		if self.version == 1:
			format = OS2_format_1
		elif self.version in (2, 3, 4):
			format = OS2_format_2
		elif self.version == 5:
			format = OS2_format_5
		else:
			format = OS2_format_0
		formatstring, names, fixes = sstruct.getformat(format)
		for name in names:
			value = getattr(self, name)
			if name=="panose":
				writer.begintag("panose")
				writer.newline()
				value.toXML(writer, ttFont)
				writer.endtag("panose")
			elif name in ("ulUnicodeRange1", "ulUnicodeRange2",
					"ulUnicodeRange3", "ulUnicodeRange4",
					"ulCodePageRange1", "ulCodePageRange2"):
				writer.simpletag(name, value=num2binary(value))
			elif name in ("fsType", "fsSelection"):
				writer.simpletag(name, value=num2binary(value, 16))
			elif name == "achVendID":
				writer.simpletag(name, value=repr(value)[1:-1])
			else:
				writer.simpletag(name, value=value)
			writer.newline()

	def fromXML(self, name, attrs, content, ttFont):
		if name == "panose":
			self.panose = panose = Panose()
			for element in content:
				if isinstance(element, tuple):
					name, attrs, content = element
					panose.fromXML(name, attrs, content, ttFont)
		elif name in ("ulUnicodeRange1", "ulUnicodeRange2",
				"ulUnicodeRange3", "ulUnicodeRange4",
				"ulCodePageRange1", "ulCodePageRange2",
				"fsType", "fsSelection"):
			setattr(self, name, binary2num(attrs["value"]))
		elif name == "achVendID":
			setattr(self, name, safeEval("'''" + attrs["value"] + "'''"))
		else:
			setattr(self, name, safeEval(attrs["value"]))

	def updateFirstAndLastCharIndex(self, ttFont):
		if 'cmap' not in ttFont:
			return
		codes = set()
		for table in getattr(ttFont['cmap'], 'tables', []):
			if table.isUnicode():
				codes.update(table.cmap.keys())
		if codes:
			minCode = min(codes)
			maxCode = max(codes)
			# USHORT cannot hold codepoints greater than 0xFFFF
			self.usFirstCharIndex = min(0xFFFF, minCode)
			self.usLastCharIndex = min(0xFFFF, maxCode)

	# misspelled attributes kept for legacy reasons

	@property
	def usMaxContex(self):
		return self.usMaxContext

	@usMaxContex.setter
	def usMaxContex(self, value):
		self.usMaxContext = value

	@property
	def fsFirstCharIndex(self):
		return self.usFirstCharIndex

	@fsFirstCharIndex.setter
	def fsFirstCharIndex(self, value):
		self.usFirstCharIndex = value

	@property
	def fsLastCharIndex(self):
		return self.usLastCharIndex

	@fsLastCharIndex.setter
	def fsLastCharIndex(self, value):
		self.usLastCharIndex = value

	def getUnicodeRanges(self):
		""" Return the set of 'ulUnicodeRange*' bits currently enabled. """
		bits = set()
		ul1, ul2 = self.ulUnicodeRange1, self.ulUnicodeRange2
		ul3, ul4 = self.ulUnicodeRange3, self.ulUnicodeRange4
		for i in range(32):
			if ul1 & (1 << i):
				bits.add(i)
			if ul2 & (1 << i):
				bits.add(i + 32)
			if ul3 & (1 << i):
				bits.add(i + 64)
			if ul4 & (1 << i):
				bits.add(i + 96)
		return bits

	def setUnicodeRanges(self, bits):
		""" Set the 'ulUnicodeRange*' fields to the specified 'bits'. """
		ul1, ul2, ul3, ul4 = 0, 0, 0, 0
		for bit in bits:
			if 0 <= bit < 32:
				ul1 |= (1 << bit)
			elif 32 <= bit < 64:
				ul2 |= (1 << (bit - 32))
			elif 64 <= bit < 96:
				ul3 |= (1 << (bit - 64))
			elif 96 <= bit < 123:
				ul4 |= (1 << (bit - 96))
			else:
				raise ValueError('expected 0 <= int <= 122, found: %r' % bit)
		self.ulUnicodeRange1, self.ulUnicodeRange2 = ul1, ul2
		self.ulUnicodeRange3, self.ulUnicodeRange4 = ul3, ul4

	def recalcUnicodeRanges(self, ttFont, pruneOnly=False):
		""" Intersect the codepoints in the font's Unicode cmap subtables with
		the Unicode block ranges defined in the OpenType specification (v1.7),
		and set the respective 'ulUnicodeRange*' bits if there is at least ONE
		intersection.
		If 'pruneOnly' is True, only clear unused bits with NO intersection.
		"""
		unicodes = set()
		for table in ttFont['cmap'].tables:
			if table.isUnicode():
				unicodes.update(table.cmap.keys())
		if pruneOnly:
			empty = intersectUnicodeRanges(unicodes, inverse=True)
			bits = self.getUnicodeRanges() - empty
		else:
			bits = intersectUnicodeRanges(unicodes)
		self.setUnicodeRanges(bits)
		return bits


# Unicode ranges data from the OpenType OS/2 table specification v1.7

OS2_UNICODE_RANGES = (
	(('Basic Latin',                              (0x0000, 0x007F)),),
	(('Latin-1 Supplement',                       (0x0080, 0x00FF)),),
	(('Latin Extended-A',                         (0x0100, 0x017F)),),
	(('Latin Extended-B',                         (0x0180, 0x024F)),),
	(('IPA Extensions',                           (0x0250, 0x02AF)),
	 ('Phonetic Extensions',                      (0x1D00, 0x1D7F)),
	 ('Phonetic Extensions Supplement',           (0x1D80, 0x1DBF))),
	(('Spacing Modifier Letters',                 (0x02B0, 0x02FF)),
	 ('Modifier Tone Letters',                    (0xA700, 0xA71F))),
	(('Combining Diacritical Marks',              (0x0300, 0x036F)),
	 ('Combining Diacritical Marks Supplement',   (0x1DC0, 0x1DFF))),
	(('Greek and Coptic',                         (0x0370, 0x03FF)),),
	(('Coptic',                                   (0x2C80, 0x2CFF)),),
	(('Cyrillic',                                 (0x0400, 0x04FF)),
	 ('Cyrillic Supplement',                      (0x0500, 0x052F)),
	 ('Cyrillic Extended-A',                      (0x2DE0, 0x2DFF)),
	 ('Cyrillic Extended-B',                      (0xA640, 0xA69F))),
	(('Armenian',                                 (0x0530, 0x058F)),),
	(('Hebrew',                                   (0x0590, 0x05FF)),),
	(('Vai',                                      (0xA500, 0xA63F)),),
	(('Arabic',                                   (0x0600, 0x06FF)),
	 ('Arabic Supplement',                        (0x0750, 0x077F))),
	(('NKo',                                      (0x07C0, 0x07FF)),),
	(('Devanagari',                               (0x0900, 0x097F)),),
	(('Bengali',                                  (0x0980, 0x09FF)),),
	(('Gurmukhi',                                 (0x0A00, 0x0A7F)),),
	(('Gujarati',                                 (0x0A80, 0x0AFF)),),
	(('Oriya',                                    (0x0B00, 0x0B7F)),),
	(('Tamil',                                    (0x0B80, 0x0BFF)),),
	(('Telugu',                                   (0x0C00, 0x0C7F)),),
	(('Kannada',                                  (0x0C80, 0x0CFF)),),
	(('Malayalam',                                (0x0D00, 0x0D7F)),),
	(('Thai',                                     (0x0E00, 0x0E7F)),),
	(('Lao',                                      (0x0E80, 0x0EFF)),),
	(('Georgian',                                 (0x10A0, 0x10FF)),
	 ('Georgian Supplement',                      (0x2D00, 0x2D2F))),
	(('Balinese',                                 (0x1B00, 0x1B7F)),),
	(('Hangul Jamo',                              (0x1100, 0x11FF)),),
	(('Latin Extended Additional',                (0x1E00, 0x1EFF)),
	 ('Latin Extended-C',                         (0x2C60, 0x2C7F)),
	 ('Latin Extended-D',                         (0xA720, 0xA7FF))),
	(('Greek Extended',                           (0x1F00, 0x1FFF)),),
	(('General Punctuation',                      (0x2000, 0x206F)),
	 ('Supplemental Punctuation',                 (0x2E00, 0x2E7F))),
	(('Superscripts And Subscripts',              (0x2070, 0x209F)),),
	(('Currency Symbols',                         (0x20A0, 0x20CF)),),
	(('Combining Diacritical Marks For Symbols',  (0x20D0, 0x20FF)),),
	(('Letterlike Symbols',                       (0x2100, 0x214F)),),
	(('Number Forms',                             (0x2150, 0x218F)),),
	(('Arrows',                                   (0x2190, 0x21FF)),
	 ('Supplemental Arrows-A',                    (0x27F0, 0x27FF)),
	 ('Supplemental Arrows-B',                    (0x2900, 0x297F)),
	 ('Miscellaneous Symbols and Arrows',         (0x2B00, 0x2BFF))),
	(('Mathematical Operators',                   (0x2200, 0x22FF)),
	 ('Supplemental Mathematical Operators',      (0x2A00, 0x2AFF)),
	 ('Miscellaneous Mathematical Symbols-A',     (0x27C0, 0x27EF)),
	 ('Miscellaneous Mathematical Symbols-B',     (0x2980, 0x29FF))),
	(('Miscellaneous Technical',                  (0x2300, 0x23FF)),),
	(('Control Pictures',                         (0x2400, 0x243F)),),
	(('Optical Character Recognition',            (0x2440, 0x245F)),),
	(('Enclosed Alphanumerics',                   (0x2460, 0x24FF)),),
	(('Box Drawing',                              (0x2500, 0x257F)),),
	(('Block Elements',                           (0x2580, 0x259F)),),
	(('Geometric Shapes',                         (0x25A0, 0x25FF)),),
	(('Miscellaneous Symbols',                    (0x2600, 0x26FF)),),
	(('Dingbats',                                 (0x2700, 0x27BF)),),
	(('CJK Symbols And Punctuation',              (0x3000, 0x303F)),),
	(('Hiragana',                                 (0x3040, 0x309F)),),
	(('Katakana',                                 (0x30A0, 0x30FF)),
	 ('Katakana Phonetic Extensions',             (0x31F0, 0x31FF))),
	(('Bopomofo',                                 (0x3100, 0x312F)),
	 ('Bopomofo Extended',                        (0x31A0, 0x31BF))),
	(('Hangul Compatibility Jamo',                (0x3130, 0x318F)),),
	(('Phags-pa',                                 (0xA840, 0xA87F)),),
	(('Enclosed CJK Letters And Months',          (0x3200, 0x32FF)),),
	(('CJK Compatibility',                        (0x3300, 0x33FF)),),
	(('Hangul Syllables',                         (0xAC00, 0xD7AF)),),
	(('Non-Plane 0 *',                            (0xD800, 0xDFFF)),),
	(('Phoenician',                               (0x10900, 0x1091F)),),
	(('CJK Unified Ideographs',                   (0x4E00, 0x9FFF)),
	 ('CJK Radicals Supplement',                  (0x2E80, 0x2EFF)),
	 ('Kangxi Radicals',                          (0x2F00, 0x2FDF)),
	 ('Ideographic Description Characters',       (0x2FF0, 0x2FFF)),
	 ('CJK Unified Ideographs Extension A',       (0x3400, 0x4DBF)),
	 ('CJK Unified Ideographs Extension B',       (0x20000, 0x2A6DF)),
	 ('Kanbun',                                   (0x3190, 0x319F))),
	(('Private Use Area (plane 0)',               (0xE000, 0xF8FF)),),
	(('CJK Strokes',                              (0x31C0, 0x31EF)),
	 ('CJK Compatibility Ideographs',             (0xF900, 0xFAFF)),
	 ('CJK Compatibility Ideographs Supplement',  (0x2F800, 0x2FA1F))),
	(('Alphabetic Presentation Forms',            (0xFB00, 0xFB4F)),),
	(('Arabic Presentation Forms-A',              (0xFB50, 0xFDFF)),),
	(('Combining Half Marks',                     (0xFE20, 0xFE2F)),),
	(('Vertical Forms',                           (0xFE10, 0xFE1F)),
	 ('CJK Compatibility Forms',                  (0xFE30, 0xFE4F))),
	(('Small Form Variants',                      (0xFE50, 0xFE6F)),),
	(('Arabic Presentation Forms-B',              (0xFE70, 0xFEFF)),),
	(('Halfwidth And Fullwidth Forms',            (0xFF00, 0xFFEF)),),
	(('Specials',                                 (0xFFF0, 0xFFFF)),),
	(('Tibetan',                                  (0x0F00, 0x0FFF)),),
	(('Syriac',                                   (0x0700, 0x074F)),),
	(('Thaana',                                   (0x0780, 0x07BF)),),
	(('Sinhala',                                  (0x0D80, 0x0DFF)),),
	(('Myanmar',                                  (0x1000, 0x109F)),),
	(('Ethiopic',                                 (0x1200, 0x137F)),
	 ('Ethiopic Supplement',                      (0x1380, 0x139F)),
	 ('Ethiopic Extended',                        (0x2D80, 0x2DDF))),
	(('Cherokee',                                 (0x13A0, 0x13FF)),),
	(('Unified Canadian Aboriginal Syllabics',    (0x1400, 0x167F)),),
	(('Ogham',                                    (0x1680, 0x169F)),),
	(('Runic',                                    (0x16A0, 0x16FF)),),
	(('Khmer',                                    (0x1780, 0x17FF)),
	 ('Khmer Symbols',                            (0x19E0, 0x19FF))),
	(('Mongolian',                                (0x1800, 0x18AF)),),
	(('Braille Patterns',                         (0x2800, 0x28FF)),),
	(('Yi Syllables',                             (0xA000, 0xA48F)),
	 ('Yi Radicals',                              (0xA490, 0xA4CF))),
	(('Tagalog',                                  (0x1700, 0x171F)),
	 ('Hanunoo',                                  (0x1720, 0x173F)),
	 ('Buhid',                                    (0x1740, 0x175F)),
	 ('Tagbanwa',                                 (0x1760, 0x177F))),
	(('Old Italic',                               (0x10300, 0x1032F)),),
	(('Gothic',                                   (0x10330, 0x1034F)),),
	(('Deseret',                                  (0x10400, 0x1044F)),),
	(('Byzantine Musical Symbols',                (0x1D000, 0x1D0FF)),
	 ('Musical Symbols',                          (0x1D100, 0x1D1FF)),
	 ('Ancient Greek Musical Notation',           (0x1D200, 0x1D24F))),
	(('Mathematical Alphanumeric Symbols',        (0x1D400, 0x1D7FF)),),
	(('Private Use (plane 15)',                   (0xF0000, 0xFFFFD)),
	 ('Private Use (plane 16)',                   (0x100000, 0x10FFFD))),
	(('Variation Selectors',                      (0xFE00, 0xFE0F)),
	 ('Variation Selectors Supplement',           (0xE0100, 0xE01EF))),
	(('Tags',                                     (0xE0000, 0xE007F)),),
	(('Limbu',                                    (0x1900, 0x194F)),),
	(('Tai Le',                                   (0x1950, 0x197F)),),
	(('New Tai Lue',                              (0x1980, 0x19DF)),),
	(('Buginese',                                 (0x1A00, 0x1A1F)),),
	(('Glagolitic',                               (0x2C00, 0x2C5F)),),
	(('Tifinagh',                                 (0x2D30, 0x2D7F)),),
	(('Yijing Hexagram Symbols',                  (0x4DC0, 0x4DFF)),),
	(('Syloti Nagri',                             (0xA800, 0xA82F)),),
	(('Linear B Syllabary',                       (0x10000, 0x1007F)),
	 ('Linear B Ideograms',                       (0x10080, 0x100FF)),
	 ('Aegean Numbers',                           (0x10100, 0x1013F))),
	(('Ancient Greek Numbers',                    (0x10140, 0x1018F)),),
	(('Ugaritic',                                 (0x10380, 0x1039F)),),
	(('Old Persian',                              (0x103A0, 0x103DF)),),
	(('Shavian',                                  (0x10450, 0x1047F)),),
	(('Osmanya',                                  (0x10480, 0x104AF)),),
	(('Cypriot Syllabary',                        (0x10800, 0x1083F)),),
	(('Kharoshthi',                               (0x10A00, 0x10A5F)),),
	(('Tai Xuan Jing Symbols',                    (0x1D300, 0x1D35F)),),
	(('Cuneiform',                                (0x12000, 0x123FF)),
	 ('Cuneiform Numbers and Punctuation',        (0x12400, 0x1247F))),
	(('Counting Rod Numerals',                    (0x1D360, 0x1D37F)),),
	(('Sundanese',                                (0x1B80, 0x1BBF)),),
	(('Lepcha',                                   (0x1C00, 0x1C4F)),),
	(('Ol Chiki',                                 (0x1C50, 0x1C7F)),),
	(('Saurashtra',                               (0xA880, 0xA8DF)),),
	(('Kayah Li',                                 (0xA900, 0xA92F)),),
	(('Rejang',                                   (0xA930, 0xA95F)),),
	(('Cham',                                     (0xAA00, 0xAA5F)),),
	(('Ancient Symbols',                          (0x10190, 0x101CF)),),
	(('Phaistos Disc',                            (0x101D0, 0x101FF)),),
	(('Carian',                                   (0x102A0, 0x102DF)),
	 ('Lycian',                                   (0x10280, 0x1029F)),
	 ('Lydian',                                   (0x10920, 0x1093F))),
	(('Domino Tiles',                             (0x1F030, 0x1F09F)),
	 ('Mahjong Tiles',                            (0x1F000, 0x1F02F))),
)


_unicodeRangeSets = []

def _getUnicodeRangeSets():
	# build the sets of codepoints for each unicode range bit, and cache result
	if not _unicodeRangeSets:
		for bit, blocks in enumerate(OS2_UNICODE_RANGES):
			rangeset = set()
			for _, (start, stop) in blocks:
				rangeset.update(set(range(start, stop+1)))
			if bit == 57:
				# The spec says that bit 57 ("Non Plane 0") implies that there's
				# at least one codepoint beyond the BMP; so I also include all
				# the non-BMP codepoints here
				rangeset.update(set(range(0x10000, 0x110000)))
			_unicodeRangeSets.append(rangeset)
	return _unicodeRangeSets


def intersectUnicodeRanges(unicodes, inverse=False):
	""" Intersect a sequence of (int) Unicode codepoints with the Unicode block
	ranges defined in the OpenType specification v1.7, and return the set of
	'ulUnicodeRanges' bits for which there is at least ONE intersection.
	If 'inverse' is True, return the the bits for which there is NO intersection.

	>>> intersectUnicodeRanges([0x0410]) == {9}
	True
	>>> intersectUnicodeRanges([0x0410, 0x1F000]) == {9, 57, 122}
	True
	>>> intersectUnicodeRanges([0x0410, 0x1F000], inverse=True) == (
	...     set(range(123)) - {9, 57, 122})
	True
	"""
	unicodes = set(unicodes)
	uniranges = _getUnicodeRangeSets()
	bits = set([
		bit for bit, unirange in enumerate(uniranges)
		if not unirange.isdisjoint(unicodes) ^ inverse])
	return bits


if __name__ == "__main__":
	import doctest, sys
	sys.exit(doctest.testmod().failed)