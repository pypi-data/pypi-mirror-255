"""
This code defines a class which generates a LaTeX string which CENTERS a given
poem on a page.
"""

# Standard imports.
import re

# Local imports.
from .lookups import SYNTACTICS, FRACTIONS
from .utils import trim_whitespace, trim_blank_lines

##############
# MAIN CLASS #
##############

class Centerer:
    """ The class in question. """
    def __init__(self, input_string):
        self.input_string = input_string
        self.lines = input_string.split("\n")

    def convert_lines_to_plain_text(self):
        """ Purge any HPML code, etc, from each line. """
        for index, line in enumerate(self.lines):
            if not line.startswith("###"):
                self.lines[index] = convert_line_of_hpml_to_plain_text(line)
        self.lines = trim_blank_lines(self.lines)

    def get_second_longest_line(self):
        """ Ronseal. """
        longest_line = self.lines[0]
        second_longest_line = self.lines[0]
        for line in self.lines:
            if len(line) > len(longest_line):
                second_longest_line = longest_line
                longest_line = line
            elif len(line) > len(second_longest_line):
                second_longest_line = line
        return second_longest_line

    def get_settowidth_string(self):
        """ Get the second longest PURGED line. """
        self.convert_lines_to_plain_text()
        return self.get_second_longest_line()

####################
# HELPER FUNCTIONS #
####################

def convert_line_of_hpml_to_plain_text(line):
    """ Purge any HPML code, etc, from a given line. """
    tabs = line.count("##TAB")
    line = convert_equivalents_in_line(line)
    line = convert_fractions_in_line(line)
    line = re.sub("##MARGINNOTE{.*}", "", line) # Remove any margin notes.
    line = re.sub("##\\w*", "", line) # Remove any word beginning "##...".
    line = re.sub("#\\w*", "", line) # Remove any word beginning "#...".
    line = line.replace("{", "")
    line = line.replace("}", "")
    line = trim_whitespace(line)
    for _ in range(tabs):
        line = "    "+line
    return line

def convert_equivalents_in_line(line):
    """ Convert any straightforward equivalents from HPML to plain text. """
    for hpml_code, value in SYNTACTICS.items():
        line = line.replace(hpml_code, value.plain)
    return line

def convert_fractions_in_line(line):
    """ Convert any fractions from HPML to plain text. """
    for hpml_code, value in FRACTIONS.items():
        line = line.replace(hpml_code, value.plain)
    return line
