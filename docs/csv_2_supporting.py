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
import numpy as np
import pathlib
import argparse
import sys
from argparse_types import file_path, dir_path

"""
This utility script facilitates batch creation of supporting material files from a comma-separated-value
file. The csv file follows the format of the knowledge-base roadmap.csv, with one exception, 
each row is expected to contain a single ORCID, either in the Agree or Disagree column. # noqa W291

All supporting materials files follow the same structure which is defined by a template file. Generally speaking, 
template based file generation is best done using a dedicated tool such as jinja (https://jinja.palletsprojects.com/).
As our use case is very simple, string formatting is sufficient and we avoid dependency on an additional tool. 

The supporting material files are created with the expected names in the specific directory: target_conjugate/orcid.md.

As we are creating multiple supporting files, they share the same reasoning section. This shared text is provided as one
of the inputs, the "shared_reasoning_file". The file contents are either plain text or they can be markdown.
For example:

See publication and Zenodo entry:

A. J. Radtke et al., "IBEX: an iterative immunolabeling and chemical bleaching
 method for high-content imaging of diverse tissues", Nat. Protoc., 17(2):378-40
1, 2022, [doi: 10.1038/s41596-021-00644-9](https://www.nature.com/articles/s41596-021-00644-9).

A. J. Radtke et al., "Accompanying dataset for: IBEX: An iterative immunolabeling and chemical 
bleaching method for high-content imaging of diverse tissues",
[doi: 10.5281/zenodo.5244550](https://doi.org/10.5281/zenodo.5244551).
"""


def create_md_files(
    target_conjugate, all_df, template_str, reasoning_str, supporting_material_root_dir
):
    # target_conjugate.fillna(
    #     "", inplace=True
    # )  # if a dye the conjugate is NaN and we replace with empty string
    tc_rows = all_df[
        (all_df[target_conjugate.index[0]] == target_conjugate[0])
        & (all_df[target_conjugate.index[1]] == target_conjugate[1])
    ]
    orcids = [
        orcid
        for orcid in pd.concat(
            [tc_rows["Agree"], tc_rows["Disagree"]]
        ).drop_duplicates()
        if orcid != ""
    ]
    data_path = supporting_material_root_dir / pathlib.Path(
        target_conjugate[0] + "_" + target_conjugate[1]
    )
    data_path.mkdir(parents=True, exist_ok=True)
    result_file_paths = []

    for orcid in orcids:
        configurations_table = tc_rows[
            (tc_rows["Agree"] == orcid) | (tc_rows["Disagree"] == orcid)
        ]
        # replace orcid with +
        configurations_table[configurations_table == orcid] = (
            "[+](#reason1)" if reasoning_str else "+"
        )
        data_dict = {}
        data_dict["configurations_table"] = configurations_table.fillna("").to_markdown(
            index=False
        )
        data_dict["reasoning"] = (
            '<a name="reason1"></a>\n' + reasoning_str if reasoning_str else ""
        )
        data_dict["orcid"] = orcid
        file_path = data_path / pathlib.Path(orcid + ".md")
        with open(file_path, "w") as fp:
            fp.write(template_str.format(**data_dict))
        result_file_paths.append(file_path)
    return result_file_paths


def single_orcid(x):
    num_orcids = 0
    for v in x:
        if v.strip() != "":
            num_orcids += len(v.split(";"))
    return num_orcids == 1


def csv_2_supporting(
    csv_file,
    supporting_material_root_dir,
    supporting_template_file,
    shared_reasoning_file=None,
):
    orcid_column_names = ["Agree", "Disagree"]
    # Read the dataframe and keep entries that are "NA", don't convert to nan
    df = pd.read_csv(csv_file, dtype=str, keep_default_na=False)

    # Check that there is only one ORCID per row.
    single_orcid_rows = df[orcid_column_names].apply(single_orcid, axis=1)
    if not single_orcid_rows.all():
        raise ValueError(
            f"Invalid file {csv_file}, following rows contain more than one ORCID:\n{list(single_orcid_rows[single_orcid_rows==False].index)}"  # noqa E501
        )

    # Check that dataframe does not contain preceding or trailing whitespace in entries
    df_stripped_whitespace = df.applymap(lambda x: x.strip(), na_action="ignore")
    diff_entries = np.where(
        (df != df_stripped_whitespace)
        & ~(df.isnull() & df_stripped_whitespace.isnull())
    )
    if diff_entries[0].size > 0:
        raise ValueError(
            "Dataframe entries contain preceding or trailing whitespace, please remove [row, col, value]:\n"
            + "\n".join(
                [
                    f"{row+2},{col+1}: {val}"
                    for row, col, val in zip(
                        diff_entries[0], diff_entries[1], df.values[diff_entries]
                    )
                ]
            )
        )
    shared_reasoning_str = ""
    if shared_reasoning_file:
        with open(shared_reasoning_file) as fp:
            shared_reasoning_str = fp.read()
    with open(supporting_template_file) as fp:
        template_str = fp.read()

    unique_target_conjugate = df[
        ["Target Name / Protein Biomarker", "Conjugate"]
    ].drop_duplicates()
    return unique_target_conjugate.apply(
        lambda x: create_md_files(
            x, df, template_str, shared_reasoning_str, supporting_material_root_dir
        ),
        axis=1,
    ).explode()  # explode takes series of lists and returns series of entries


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Create supporting material files from a csv which has the same structure as the roadmap."
    )
    parser.add_argument("csv_file", type=file_path)
    parser.add_argument("supporting_template_file", type=file_path)
    parser.add_argument("supporting_material_root_dir", type=dir_path)
    parser.add_argument("--shared_reasoning_file", type=file_path, nargs="?")
    args = parser.parse_args(argv)

    try:
        csv_2_supporting(
            args.csv_file,
            args.supporting_material_root_dir,
            args.supporting_template_file,
            args.shared_reasoning_file,
        )
    except Exception as e:
        print(
            f"{e}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
