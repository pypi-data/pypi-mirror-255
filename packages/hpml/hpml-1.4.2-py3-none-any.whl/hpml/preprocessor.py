"""
This code defines a class which carries out the preprocessing stage of compiling
HPML into LaTeX.
"""

# Standard imports.
import re
import warnings

# Local imports.
from .lookups import (
    is_suppress_non_standard_mod,
    is_other_mod,
    SUPPRESS_NON_STANDARD,
    SUPPRESS_NON_STANDARD_MODS_AS_SET,
    SEMANTICS,
    FRACTIONS,
    DASHES
)

##############
# MAIN CLASS #
##############

class Preprocessor:
    """ The class in question. """
    def __init__(self, hpml, raw_mods):
        if not raw_mods:
            raw_mods = ()
        self.hpml = hpml
        self.mods = build_mods(raw_mods)

    def preprocess(self):
        """ Ronseal. """
        for mod in self.mods:
            mod_method = getattr(self, mod)
            mod_method()
        return self.hpml

    def replace_substring(self, old, new):
        """ Replace a given substring with another. """
        self.hpml = self.hpml.replace(old, new)

    def suppress_person_font(self):
        """ Implement the mod. """
        self.replace_substring(SEMANTICS.person.hpml, "")

    def suppress_place_font(self):
        """ Implement the mod. """
        self.replace_substring(SEMANTICS.place.hpml, "")

    def suppress_publication_font(self):
        """ Implement the mod. """
        self.replace_substring(SEMANTICS.publication.hpml, SEMANTICS.ital.hpml)

    def suppress_foreign_font(self):
        """ Implement the mod. """
        self.replace_substring(SEMANTICS.foreign.hpml, SEMANTICS.ital.hpml)

    def suppress_ship_font(self):
        """ Implement the mod. """
        self.replace_substring(SEMANTICS.ship.hpml, SEMANTICS.ital.hpml)

    def suppress_ampersands(self):
        """ Implement the mod. """
        self.replace_substring(SEMANTICS.add.hpml, SEMANTICS.add.plain)

    def suppress_fractions(self):
        """ Implement the mod. """
        for fraction, value in FRACTIONS.items():
            self.replace_substring(fraction, value.plain)

    def suppress_marginnotes(self):
        """ Implement the mod. """
        re.sub("##MARGINNOTE{.*}", "", self.hpml)

    def em_dashes(self):
        """ Implement the mod. """
        self.replace_substring(" "+DASHES.n+" ", " "+DASHES.m+" ")

####################
# HELPER FUNCTIONS #
####################

def build_mods(raw_mods):
    """ Build a SET of mods from a list of raw mods. """
    result = set()
    for raw_mod in raw_mods:
        if raw_mod == SUPPRESS_NON_STANDARD:
            result = result.union(SUPPRESS_NON_STANDARD_MODS_AS_SET)
        elif is_suppress_non_standard_mod(raw_mod) or is_other_mod(raw_mod):
            result.add(raw_mod)
        else:
            warnings.warn("Unrecognised preprocessor mod: "+str(raw_mod))
    return result
