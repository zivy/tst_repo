# =========================================================================
#
#  Copyright Ziv Yaniv
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0.txt
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# =========================================================================

import bibtexparser
import subprocess
import tempfile
import argparse
import sys
from argparse_types import file_path

"""
This script creates the publications markdown page from the publications.bib bibliography
file (in biblatex format). It uses the pandoc tool to do the conversion. Note that all publications
found in the publications.bib file are listed. The order of the entries in that file does not
matter, we use the bibtexparser package to sort them in reverse chronological order and in
secondary alphabetical order using the first author's last name.

The formatting of the references is determined by a citation style language (csl) file provided
as part of the input.

Citation Style Language: https://citationstyles.org/
csl format specification: https://docs.citationstyles.org/en/stable/specification.html.

We use a "custom" style based on the ieee.csl:
1. All authors are listed, no et al. (credit where credit is due).
2. List and quick access to corresponding author emails.
3. Display keywords for convenient searching.

This script is run automatically when modifications to the publications.bib file are merged
into the main branch.
"""


def bibfile2md(bib_file, citation_style_language_file, output_file):
    """
    Use pandoc to convert a bibtex/biblatex file to a markdown list of references.
    The reference format is determined by the citation style language file. A wide
    variety of style files are available from the zotero site https://www.zotero.org/styles.
    """
    pandoc_md_preamble = '---\nnocite: "@*"\n---\n# Publications\n Publications are listed in reverse chronological order.'  # noqa E501
    # Read the bibliography file, sort it and write to temp file which is then used
    # as input for pandoc which converts it to a markdown file.
    with open(bib_file) as biblatex_file:
        bib_database = bibtexparser.load(biblatex_file)
        # sort in reverse chronological order and secondary order using author alphabetical order
        bib_database.entries = sorted(
            bib_database.entries, key=lambda d: (-int(d["year"]), d["author"])
        )
    writer = bibtexparser.bwriter.BibTexWriter()
    # don't sort entries (writer has sorting functionality but not what we need, as above)
    writer.order_entries_by = None
    with tempfile.TemporaryDirectory() as tmpdirname:
        sorted_bib_filepath = tmpdirname + "/sorted.bib"
        with open(sorted_bib_filepath, "w") as fp:
            fp.write(writer.write(bib_database))
        pandoc_md_filepath = tmpdirname + "/pandoc_publications_in.md"
        with open(pandoc_md_filepath, "w") as fp:
            fp.write(pandoc_md_preamble)

        args = [
            "pandoc",
            "-t",
            "markdown_strict",
            "--filter",
            "pandoc-citeproc",
            "--biblatex",
            f"--csl={citation_style_language_file}",
            pandoc_md_filepath,
            f"--bibliography={sorted_bib_filepath}",
            "-o",
            output_file,
        ]
        subprocess.check_call(args)


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Create publications markdown file from a bib file."
    )
    parser.add_argument(
        "bib_file", type=file_path, help="bibliography file in bibtex/biblatex format"
    )
    parser.add_argument(
        "csl_file",
        type=file_path,
        help="citation style language file for formatting the bibliography "
        + "(donwload and view style files from zotero site https://www.zotero.org/styles)",
    )
    parser.add_argument("output_file", type=str, help="markdown output file name")
    args = parser.parse_args(argv)

    try:
        bibfile2md(args.bib_file, args.csl_file, args.output_file)
    except Exception as e:
        print(
            f"{e}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
    # sys.exit(main(["../publications.bib", "ibex.csl", "publications.md"]))
