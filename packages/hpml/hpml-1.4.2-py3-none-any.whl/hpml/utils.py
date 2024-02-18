"""
This code defines some utility functions used across the package.
"""

# Standard imports.
import json
import re
import shutil
import warnings
from pathlib import Path
from types import SimpleNamespace

# Local constants.
PATH_OBJ_TO_DATA = Path(__file__).parent/"data"
PATH_TO_SYNTACTICS = str((PATH_OBJ_TO_DATA/"syntactics.json").resolve())
PATH_TO_SEMANTICS = str((PATH_OBJ_TO_DATA/"semantics.json").resolve())
PATH_OBJ_TO_GTKSOURCEVIEW = Path("/usr")/"share"/"gtksourceview-4"
PATH_TO_HPML_LANG_SRC = str((PATH_OBJ_TO_DATA/"hpml.lang").resolve())
PATH_OBJ_TO_HPML_LANG_DST = \
    PATH_OBJ_TO_GTKSOURCEVIEW/"language-specs"/"hpml.lang"
PATH_TO_HPML_LANG_DST = str(PATH_OBJ_TO_HPML_LANG_DST.resolve())
HPML_EXTENSION = ".hpml"
TEX_EXTENSION = ".tex"

#############
# FUNCTIONS #
#############

def get_syntactics():
    """ Return a dictionary of the HPML syntactic commands. """
    with open(PATH_TO_SYNTACTICS, "r") as syntactics_file:
        syntactics_str = syntactics_file.read()
    syntactics_dict = json.loads(syntactics_str)
    result = {}
    for key, value in syntactics_dict.items():
        result[key] = SimpleNamespace(**value)
    return result

def get_semantics():
    """ Return an object of the HPML semantic commands. """
    with open(PATH_TO_SEMANTICS, "r") as semantics_file:
        semantics_str = semantics_file.read()
    result = \
        json.loads(semantics_str, object_hook=lambda d: SimpleNamespace(**d))
    return result

def install_hpml_lang():
    """ Install the HPML language features in Gedit. """
    if not PATH_OBJ_TO_HPML_LANG_DST.exists():
        if PATH_OBJ_TO_GTKSOURCEVIEW.exists():
            shutil.copy(PATH_TO_HPML_LANG_SRC, PATH_TO_HPML_LANG_DST)
        else:
            path_to_gtksourceview = str(PATH_OBJ_TO_GTKSOURCEVIEW.resolve())
            warnings.warn(
                "The folder "+path_to_gtksourceview+" does not exist on this "+
                "machine. Therefore, it has not been possible to install the "+
                "HPML language features into Gedit."
            )

def trim_whitespace(line):
    """ Remove (1) whitespace from the front, (2) and from the back, and (3)
    any double, triple, etc spaces. """
    line = re.sub("^ *", "", line)
    line = re.sub(" *$", "", line)
    while "  " in line:
        line = line.replace("  ", " ")
    return line

def trim_blank_lines(lines):
    """ Trim any leading or trailing blank lines, and any double, triple, etc
    blank lines, from a list of lines. """
    result = []
    last_index = len(lines)-1
    prev = None
    for index, line in enumerate(lines):
        if (
            (line != "") or
            ((prev is not None) and (prev != "") and (index != last_index))
        ):
            result.append(line)
        prev = line
    return result

def remove_command_with_argument(command, line):
    """ Purge anything of the form #COMMAND{argument}. """
    regex_pattern = command+".*}"
    result = re.sub(regex_pattern, "", line)
    return result

def remove_commands_without_arguments(line):
    """ Remove each #COMMAND, ##COMMAND, etc. """
    for hashes in (1, 2):
        result = remove_commands_with_hashes_but_without_arguments(line, hashes)
    return result

def remove_commands_with_hashes_but_without_arguments(line, hashes):
    """ Remove each #COMMAND OR ##COMMAND, etc. """
    regex_pattern = "\\w*"
    for _ in range(hashes):
        regex_pattern = "#"+regex_pattern
    result = re.sub(regex_pattern, "", line)
    return result
