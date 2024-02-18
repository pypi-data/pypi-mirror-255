"""
This code defines a class which compiles HPML into LaTeX.
"""

# Standard imports.
from dataclasses import dataclass
from pathlib import Path

# Local imports.
from .centerer import Centerer
from .lookups import (
    SEMANTICS,
    SYNTACTICS,
    FRACTIONS,
    ENDBLC,
    OtherLaTeX
)
from .preprocessor import Preprocessor
from .utils import TEX_EXTENSION, trim_whitespace, trim_blank_lines

##############
# MAIN CLASS #
##############

@dataclass
class HPMLCompiler:
    """ The class in question. """
    path_to_input_file: str = None
    input_string: str = None
    is_prose_poem: bool = False
    mods: list[str] = None
    path_to_output_file: str = None
    output_string: str = None
    enclose: bool = True
    manual_settowidth_string: str = None
    auto_center: bool = True
    epigraph: list[str] = None
    # Non-public.
    _temp: str = None
    _lines: list[str] = None

    def __post_init__(self):
        if self.path_to_input_file and self.input_string:
            raise HPMLCompilerException(
                "You must Specify either an input file or an input string, "+
                "but NOT BOTH."
            )
        if not self.path_to_input_file and not self.input_string:
            raise HPMLCompilerException(
                "You must specify either an input file or an input string."
            )
        if not self.input_string:
            with open(self.path_to_input_file, "r") as input_file:
                self.input_string = input_file.read()
        if self.path_to_input_file and not self.path_to_output_file:
            self.path_to_output_file = \
                Path(self.path_to_input_file).with_suffix(TEX_EXTENSION)
        if self.is_prose_poem:
            self.enclose = False

    def compile(self) -> str:
        """ Build the output string from the input. """
        self._preprocess()
        self._process()
        if self.path_to_output_file:
            return self.path_to_output_file
        return self.output_string

    def _preprocess(self):
        """ Run the input through a preprocessor object. """
        preprocessor = Preprocessor(self.input_string, self.mods)
        self._temp = preprocessor.preprocess()

    def _process(self):
        """ Ronseal. """
        self._lines = self._temp.split("\n")
        self._update_manual_settowidth_string()
        self._update_epigraph()
        self._purge_whitespace()
        self._process_choruses()
        self._process_minichoruses()
        self._add_endings()
        self._process_syntactics()
        self._process_semantics()
        if self.enclose:
            self._enclose_output()
        self.output_string = "\n".join(self._lines)

    def _purge_whitespace(self):
        """ Ronseal. """
        for index, line in enumerate(self._lines):
            self._lines[index] = trim_whitespace(line)
        self._lines = trim_blank_lines(self._lines)

    def _process_choruses(self):
        """ Handles choruses and inscriptions. """
        for index, line in enumerate(self._lines):
            if (
                (SEMANTICS.chorus.hpml in line) or
                (SEMANTICS.inscription.hpml in line)
            ):
                for line_num in range(index+1, len(self._lines)):
                    current_line = self._lines[line_num]
                    previous_line = self._lines[line_num-1]
                    if index == len(self._lines)-1:
                        self._lines[line_num] = current_line+ENDBLC
                    elif current_line == "":
                        self._lines[line_num-1] = previous_line+ENDBLC
                        break
                self._lines[index] = OtherLaTeX.MULTILINE_ITALICS

    def _process_minichoruses(self):
        """ Handles mini-choruses and mini-inscriptions. """
        for index, line in enumerate(self._lines):
            if (
                (SEMANTICS.minichorus.hpml in line) or
                (SEMANTICS.miniinscription.hpml in line)
            ):
                line = \
                    line.replace(
                        SEMANTICS.minichorus.hpml,
                        SEMANTICS.minichorus.latex
                    )
                line = \
                    line.replace(
                        SEMANTICS.miniinscription.hpml,
                        SEMANTICS.miniinscription.latex
                    )
                line = line+ENDBLC
                self._lines[index] = line

    def _add_endings(self):
        """ Adds "\\", "\\*" or "\\!" to each line, as appropriate. """
        if self.is_prose_poem:
            return
        for index, line in enumerate(self._lines):
            if (
                (line == "") or
                (line == OtherLaTeX.MULTILINE_ITALICS) or
                (index == len(self._lines)-1)
               ):
                pass
            elif (index != len(self._lines)-1) and (self._lines[index+1] == ""):
                line = line+OtherLaTeX.NEW_VERSE.value
                self._lines[index] = line
            elif (
                (index in (0, len(self._lines)-2)) or
                (self._lines[index-1] == "") or
                ((index < len(self._lines)-2) and (self._lines[index+2] == ""))
            ):
                line = line+OtherLaTeX.NEW_LINE_NO_BREAK.value
                self._lines[index] = line
            else:
                line = line+OtherLaTeX.NEW_LINE.value
                self._lines[index] = line

    def _process_syntactics(self):
        """ Translate those clusters for which clear equivalents exist. """
        for hpml_code, value in SYNTACTICS.items():
            self._replace_across_all_lines(hpml_code, value.latex)

    def _replace_across_all_lines(self, old, new):
        """ Replace every instance of old with new across all lines. """
        for index, line in enumerate(self._lines):
            self._lines[index] = line.replace(old, new)

    def _replace_across_all_lines_semantic(self, semantic_obj):
        """ Replace the HPML command with the equivalent LaTeX command. """
        self._replace_across_all_lines(semantic_obj.hpml, semantic_obj.latex)

    def _process_semantics(self):
        """ Ronseal. """
        self._process_tabs()
        self._process_margin_notes()
        self._process_places()
        self._process_persons()
        self._process_publications()
        self._process_foreign_strings()
        self._process_fractions()
        self._process_ampersands()
        self._process_stress()
        self._process_flagverses()
        self._process_subscript()
        self._process_footnotes()
        self._process_whitespace()

    def _process_tabs(self):
        """ Ronseal. """
        self._replace_across_all_lines_semantic(SEMANTICS.tab)

    def _process_margin_notes(self):
        """ Ronseal. """
        self._replace_across_all_lines_semantic(SEMANTICS.marginnote)

    def _process_places(self):
        """ Ronseal. """
        self._replace_across_all_lines_semantic(SEMANTICS.place)

    def _process_persons(self):
        """ Ronseal. """
        self._replace_across_all_lines_semantic(SEMANTICS.person)

    def _process_publications(self):
        """ Ronseal. """
        self._replace_across_all_lines_semantic(SEMANTICS.publication)

    def _process_foreign_strings(self):
        """ Ronseal. """
        self._replace_across_all_lines_semantic(SEMANTICS.foreign)

    def _process_fractions(self):
        """ Ronseal. """
        for hpml, value in FRACTIONS.items():
            self._replace_across_all_lines(hpml, value.latex)

    def _process_ampersands(self):
        """ Ronseal. """
        self._replace_across_all_lines_semantic(SEMANTICS.add)

    def _process_stress(self):
        """ Handles stressed syllables. """
        self._replace_across_all_lines_semantic(SEMANTICS.stress)

    def _process_flagverses(self):
        """ Adds mini-titles to particular verses. """
        self._replace_across_all_lines_semantic(SEMANTICS.flagverse)

    def _process_subscript(self):
        """ Ronseal. """
        self._replace_across_all_lines_semantic(SEMANTICS.sub)

    def _process_footnotes(self):
        """ Ronseal. """
        self._replace_across_all_lines_semantic(SEMANTICS.footnote)
        self._replace_across_all_lines_semantic(SEMANTICS.blfootnote)

    def _process_whitespace(self):
        """ Ronseal. """
        self._replace_across_all_lines_semantic(SEMANTICS.whitespace)

    def make_epigraph_block(self):
        """ Make the epigraph block from the epigraph. """
        result = [
            OtherLaTeX.BEGIN_CENTER.value,
            self.epigraph,
            OtherLaTeX.END_CENTER.value,
            OtherLaTeX.BIGSKIP.value,
            OtherLaTeX.BIGSKIP.value
        ]
        return result

    def _enclose_output(self):
        """ Enclose the input in a poem environment. """
        if self.manual_settowidth_string or self.auto_center:
            local_begin_verse = OtherLaTeX.BEGIN_VERSE_CENTERED.value
        else:
            local_begin_verse = OtherLaTeX.BEGIN_VERSE.value
        self._lines = (
            [local_begin_verse]+
            self._lines+
            [OtherLaTeX.END_VERSE.value]
        )
        if self.manual_settowidth_string or self.auto_center:
            self._center_output()
        if self.epigraph:
            epigraph_block = self.make_epigraph_block()
            self._lines = epigraph_block+self._lines

    def _update_manual_settowidth_string(self):
        """ Check each line to see whether the verse width is set manually. """
        settowidth_marker = SEMANTICS.settowidth.hpml
        settowidth_len = len(settowidth_marker)
        settowidth_line_index = None
        for index, line in enumerate(self._lines):
            if line.startswith(settowidth_marker) and line.endswith(ENDBLC):
                if not self.manual_settowidth_string:
                    self.manual_settowidth_string = line[settowidth_len:-1]
                settowidth_line_index = index
                break
        if settowidth_line_index is not None:
            self._lines.pop(settowidth_line_index)

    def _get_auto_settowidth_string(self):
        """ Get an automatically-generated settowidth string for a given poem in
        HPML code. """
        centerer = Centerer(self.input_string)
        return centerer.get_settowidth_string()

    def _center_output(self):
        """ Add a string to center this poem on the page. """
        if self.manual_settowidth_string:
            settowidth_string = self.manual_settowidth_string
        else:
            settowidth_string = self._get_auto_settowidth_string()
        settowidth_line = (
            OtherLaTeX.PRE_SETTOWIDTH.value+
            settowidth_string+
            ENDBLC
        )
        self._lines = [settowidth_line]+self._lines

    def _update_epigraph(self):
        """ Find and process the epigraph, if it exists. """
        epigraph_marker = SEMANTICS.epigraph.hpml
        epigraph_len = len(epigraph_marker)
        epigraph_index = None
        for index, line in enumerate(self._lines):
            if line.startswith(epigraph_marker) and line.endswith(ENDBLC):
                self.epigraph = (
                    SEMANTICS.ital.latex+
                    line[epigraph_len:-1]+
                    OtherLaTeX.END_BLOCK.value
                )
                epigraph_index = index
                break
        if epigraph_index is not None:
            self._lines.pop(epigraph_index)

    def save_to_file(self) -> str:
        """ Save the output string to a file. """
        if not self.path_to_output_file:
            raise HPMLCompilerException("No save file path specified.")
        with open(self.path_to_output_file, "w") as output_file:
            output_file.write(self.output_string)
        return self.path_to_output_file

##################
# HELPER CLASSES #
##################

class HPMLCompilerException(Exception):
    """ A custom exception. """
