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

import pandas as pd
import os  # had to use os for relpath, pathlib's relative_to doesn't work
import argparse
import sys
from argparse_types import file_path, dir_path

"""
This script converts the IBEX knowledge-base roadmap file to markdown and
adds hyperlinks between the ORCID entries and the supporting material files.
The links cannot exist in the original csv file, or in a simple way in an excel
spreadsheet because we use multiple links in the same table cell (Agree/Disagree), 
functionality excel does not support in a simple manner. # noqa W291

On the other hand, using markdown for the roadmap table does not address all our 
needs either, sorting and searching are not possible or are very cumbersome.

We therefore use the csv file as the official roadmap, and it is what
contributors edit. This script is run automatically on merge into the main
branch and generates the markdown-with-hyperlinks version of the csv file, enabling
easy access and browsing of the supporting material.
"""


def data_2_urls_str(data, supporting_material_root_dir):
    urls_str = ""
    # First entry in the data corresponds to the "Agree" or "Disagree" column and can
    # be a space.
    if data[0].strip() != "":
        txt = [v.strip() for v in data[0].split(";") if v.strip() != ""]
        for v in txt[0:-1]:
            urls_str += (
                f"[{v}]({supporting_material_root_dir}/{data[1]}_{data[2]}/{v}.md), "
            )
        urls_str += f"[{txt[-1]}]({supporting_material_root_dir}/{data[1]}_{data[2]}/{txt[-1]}.md)"
        # Encode space as %20 in the url
        urls_str = urls_str.replace(" ", "%20")
    return urls_str


def csv_2_md_with_url(file_path, supporting_material_root_dir):
    # Read the dataframe and keep entries that are "NA", don't convert to nan
    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
    # Use relative paths between the roadmap.csv and the supporting material directory
    # so that they can be moved around together
    supporting_material_root_dir = os.path.relpath(
        supporting_material_root_dir, file_path.parent
    )
    if not df.empty:
        df["Agree"] = df[
            ["Agree", "Target Name / Protein Biomarker", "Conjugate"]
        ].apply(lambda x: data_2_urls_str(x, supporting_material_root_dir), axis=1)
        df["Disagree"] = df[
            ["Disagree", "Target Name / Protein Biomarker", "Conjugate"]
        ].apply(lambda x: data_2_urls_str(x, supporting_material_root_dir), axis=1)
    df.to_markdown(file_path.with_suffix(".md"), index=False)


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Convert knowledge-base roadmap file from csv to md and add hyperlinks."
    )
    parser.add_argument("csv_file", type=file_path)
    parser.add_argument("supporting_material_root_dir", type=dir_path)
    args = parser.parse_args(argv)

    try:
        csv_2_md_with_url(args.csv_file, args.supporting_material_root_dir)
    except Exception as e:
        print(
            f"{e}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
