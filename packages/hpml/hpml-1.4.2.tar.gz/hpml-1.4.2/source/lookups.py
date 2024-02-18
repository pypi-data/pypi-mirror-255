"""
This code defines the dictionaries and objects with which other code can LOOK UP
HPML commands and their LaTeX and plain text equivalents.
"""

# Standard imports.
from enum import Enum
from types import SimpleNamespace

# Local imports
from .utils import get_semantics, get_syntactics

###########
# LOOKUPS #
###########

DASHES = SimpleNamespace(m="---", n="--")
FRACTIONS = {
    "#HALF": SimpleNamespace(plain="half", latex="\\sfrac{$1$}{$2$}"),
    "#THIRD": SimpleNamespace(plain="third", latex="\\sfrac{$1$}{$3$}"),
    "#QUARTER": SimpleNamespace(plain="quarter", latex="\\sfrac{$1$}{$4$}")
}
SEMANTICS = get_semantics()
SYNTACTICS = get_syntactics()

# Abbreviations.
STABLC = SEMANTICS.startblock.hpml # Same as LaTeX.
ENDBLC = SEMANTICS.endblock.hpml # Same as LaTeX.

########
# MODS #
########

SUPPRESS_NON_STANDARD = "suppress_non_standard"

class SuppressNonStandardMods(Enum):
    """ Lists the mods which, individually, suppress any non-standard printing
    conventions. """
    SUPPRESS_PERSON_FONT = "suppress_person_font"
    SUPPRESS_PLACE_FONT = "suppress_place_font"
    SUPPRESS_PUBLICATION_FONT = "suppress_publication_font"
    SUPPRESS_FOREIGN_FONT = "suppress_foreign_font"
    SUPPRESS_SHIP_FONT = "suppress_ship_font"
    SUPPRESS_FRACTIONS = "suppress_fractions"
    SUPPRESS_AMPERSANDS = "suppress_ampersands"

class OtherMods(Enum):
    """ Lists the mods which do not suppress any non-standard printing
    conventions. """
    EM_DASHES = "em_dashes"

# Sets of values are sometimes useful.
SUPPRESS_NON_STANDARD_MODS_AS_SET = {
    item.value for item in SuppressNonStandardMods
}
OTHER_MODS_AS_SET = {item.value for item in OtherMods}

class OtherLaTeX(Enum):
    """ Defines some useful LaTeX formulae which don't crop up elsewhere. """
    START_BLOCK = "{"
    END_BLOCK = "}"
    BEGIN_VERSE = "\\begin{verse}"
    BEGIN_VERSE_CENTERED = "\\begin{verse}[\\versewidth]"
    END_VERSE = "\\end{verse}"
    PRE_SETTOWIDTH = "\\settowidth{\\versewidth}{"
    POST_SETTOWIDTH = "}"
    MULTILINE_ITALICS = "{\\itshape"
    BEGIN_CENTER = "\\begin{center}"
    END_CENTER = "\\end{center}"
    BIGSKIP = "\\bigskip"
    NEW_LINE = "\\\\"
    NEW_LINE_NO_BREAK = "\\\\*"
    NEW_VERSE = "\\\\!"

#############
# FUNCTIONS #
#############

def is_suppress_non_standard_mod(mod_name):
    """ Determine whether the enum contains this value. """
    if mod_name in SUPPRESS_NON_STANDARD_MODS_AS_SET:
        return True
    return False

def is_other_mod(mod_name):
    """ Determine whether the enum contains this value. """
    if mod_name in OTHER_MODS_AS_SET:
        return True
    return False
