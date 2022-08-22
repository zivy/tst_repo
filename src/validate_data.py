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
import sys
import pathlib
import json
import argparse
from argparse_types import file_path, dir_path

"""
This script validates the IBEX knowledge-base comma-separated-value roadmap file based on the
settings from the given JSON configuration file. Additionally it checks that the roadmap
file and supporting material markdown files are consistent with each other.

The JSON configuration defines the list of expected column names, which columns are required to
contain data, which optionally contain data and what are the valid values for specific columns.

Beyond the settings defined by the JSON configuration file the script checks that any ORCID which
is listed in the roadmap file also appears in the .zenodo.json file which is used as part of the
zenodo knowledge-base release workflow.

Additional checks include:
 0. Check that the .zenodo.json creators section includes the affiliation, name, ORCID and email for
    each contributor and that each contributor is only listed once.
 1. All rows of the roadmap.csv file are unique.
 2. The same ORCID does not appear in the agree and disagree columns (can't make up our minds).
 3. The same ORCID does not appear multiple times in the same column (one person, one vote).
 4. The content of the supporting material files is consistent with the roadmap.
 5. No superfluous markdown files found in the supporting material directories, nothing additional to the roadmap.
"""


def validate_data(
    json_config_file, roadmap_csv, supporting_material_root_dir, zenodo_json
):

    with open(json_config_file) as fp:
        try:
            # The configuration dictionary contains the list of columns that must contain
            # data and those that may not contain data. All other elements in the dictionary
            # correspond to column names and expected/valid data entry values for those columns.
            configuration_dict = json.load(fp)
            required_column_names = set(
                configuration_dict["data_required_column_names"]
            )
            optional_column_names = set(
                configuration_dict["data_optional_column_names"]
            )
            if required_column_names.intersection(optional_column_names):
                raise ValueError(
                    "Problem with JSON configuration file ({json_config_file}), {required_column_names} appear in both required and optional data columns."  # noqa E501
                )
            expected_values = {}
            for k, val in configuration_dict.items():
                if k not in [
                    "data_required_column_names",
                    "data_optional_column_names",
                ]:
                    expected_values[k] = set(val)
        except Exception as e:
            print(
                f"Problem reading JSON configuration file ({json_config_file}): {e}.",
                file=sys.stderr,
            )
            return 1
    with open(zenodo_json) as fp:
        try:
            zenodo_dict = json.load(fp)
            # Get list of ORCIDs
            orcids = []
            required_information = {"affiliation", "name", "orcid", "email"}
            for data in zenodo_dict["creators"]:
                if not required_information.issubset(data.keys()):
                    raise ValueError(
                        "missing required information in the creators section"
                    )
                orcids.append(data["orcid"])
            # Check uniqueness
            creator_orcids = set(orcids)
            if len(creator_orcids) != len(orcids):
                raise ValueError("Duplicate entry in creators section")
        except Exception as e:
            print(
                f"Problem reading zenodo JSON file ({zenodo_json}): {e}.",
                file=sys.stderr,
            )
            return 1

    try:
        supporting_md_files = read_and_validate_csv(
            file_path=roadmap_csv,
            data_required_column_names=required_column_names,
            data_optional_column_names=optional_column_names,
            expected_values=expected_values,
            creator_orcids=creator_orcids,
            material_root_dir=supporting_material_root_dir,
        )
        all_files_in_supporting_material = [
            p
            for p in supporting_material_root_dir.rglob("*")
            if p.is_file() and p.suffix == ".md"
        ]
        diff_set = set(all_files_in_supporting_material).difference(supporting_md_files)
        if diff_set != set():
            print(
                f"The following markdown files were found in the supporting material directory but were not referenced in the roadmap csv file: {diff_set}"  # noqa E501
            )
    except Exception as e:
        print(
            f"Invalid knowledge-base: {str(e)}.",
            file=sys.stderr,
        )
        return 1
    return 0


def entry2set(entry):
    """
    Replace a string entry with a set and check that there are
    no duplicate entries in the entry. If the entry is
    nan or a null string it is replaced by the empty set.
    Otherwise, the string is split using the semicolon as
    the separator character, leading and trailing whitespace is
    removed from the substrings and the results are added to the
    set.
    """
    if pd.isna(entry) or entry.strip() == "":
        return set()
    else:
        res_list = [v.strip() for v in entry.split(";") if v.strip() != ""]
        res = set(res_list)
        if len(res_list) != len(res):
            raise ValueError(f"entry with duplicate values - {entry}")
        return res


def read_and_validate_csv(
    file_path,
    data_required_column_names,
    data_optional_column_names,
    expected_values,
    creator_orcids,
    material_root_dir,
):
    orcid_column_names = ["Agree", "Disagree"]
    # Read the dataframe and keep entries that are "NA", don't convert to nan
    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
    if (
        df.empty
    ):  # return the empty data frame and empty list of supporting material files, nothing to check
        return df, set()

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

    # Check that the roadmap/overview dataframe columns match the combined
    # set of columns which are required to contain data or may optionally contain data.
    if not data_required_column_names.union(data_optional_column_names) == set(
        df.columns
    ):
        raise ValueError(
            f"{file_path} - expected column names do not match those found in the csv file"
        )
    # Check that the columns which are required to have data do not contain nan
    columns_expected_no_na = df[list(data_required_column_names)]
    columns_with_na = columns_expected_no_na.columns[
        columns_expected_no_na.isna().any()
    ].tolist()
    if columns_with_na:
        raise ValueError(
            f"{file_path} - found missing value in column(s) that are required to contain data: {columns_with_na}"
        )

    # Check for repeated rows (ignore the columns associated with contributor's details)
    raw_df = df.drop(orcid_column_names, axis=1)
    row_counts = raw_df.astype(str).value_counts().reset_index(name="count")
    if any(row_counts["count"] > 1):
        raise ValueError(  # Print the first couple of columns of the repeated rows
            f"{file_path} - found repeated row(s), starting with:\n"
            + row_counts.iloc[:, 0:3][row_counts["count"] > 1].to_string(index=False)
            + "\n"  # noqa E501
        )

    # Convert columns agreeing/disagreeing with the specific configuration to sets. orcid/vote cannot appear more
    # than once in the same column for a specific configuration.
    for col_name in orcid_column_names:
        df[col_name] = df[col_name].apply(entry2set)
    # Check that the same ORCID does not appear in the agree and disagree columns, we already know it does not
    # appear more than once in the same column because of the entry2set apply to the dataframe above
    rows_with_contradicting_orcid = df[orcid_column_names].apply(
        lambda x: len(x[0]) + len(x[1]) != len(x[0].union(x[1])), axis=1
    )
    if any(rows_with_contradicting_orcid):
        raise ValueError(
            f"{file_path} - found contradictory recommendation in the following rows (same ORCID appears in agree and disagree columns of same row, zero based numbering): {list(rows_with_contradicting_orcid[rows_with_contradicting_orcid == True].index)}"  # noqa E501
        )
    # Check that all ORCIDs are in the creator_orcids set
    for col_name in orcid_column_names:
        rows_not_in_creator_set = df[col_name].apply(
            lambda x: not x.issubset(creator_orcids)
        )
        if any(rows_not_in_creator_set):
            raise ValueError(
                f"{file_path} - found ORCID in the {col_name} column which is not in the creators list in the zenodo JSON, (zero based numbering) rows: {list(rows_not_in_creator_set[rows_not_in_creator_set==True].index)}"  # noqa E501
            )
    # Check that the column content for the given set of columns (see configuration file) is in
    # the expected set of values
    for k, val in expected_values.items():
        rows_with_unexpected_values = df[k].apply(lambda x: x not in val)
        if any(rows_with_unexpected_values):
            raise ValueError(
                f"{file_path} - found unexpected value in column titled {k}, rows (zero based numbering, see configuration file for valid values): {list(rows_with_unexpected_values[rows_with_unexpected_values == True].index)}"  # noqa E501
            )
    # Validate the supporting material, markdown files with unique names relative to the csv
    # file location: "supporting_material"/target_conjugate/orcid.md
    unique_target_conjugate = df[
        ["Target Name / Protein Biomarker", "Conjugate"]
    ].drop_duplicates()
    supporting_files = unique_target_conjugate.apply(
        lambda target_conjugate: validate_supporting_material(
            target_conjugate, df, material_root_dir
        ),
        axis=1,
    )

    # Return set containing all validated markdown file paths
    return set([itm for row_list in supporting_files.tolist() for itm in row_list])


def validate_supporting_material(
    target_conjugate, all_df, supporting_material_root_dir
):
    """
    Given a specific pair of target-conjugate and the complete knowledge-base dataframe, go
    over the supporting material files for all orcids listed in the dataframe and validate that
    the contents of the configurations listed in the supporting material files match the contents
    of the roadmap file.
    """
    tc_rows = all_df[
        (all_df[target_conjugate.index[0]] == target_conjugate[0])
        & (all_df[target_conjugate.index[1]] == target_conjugate[1])
    ]
    orcids = set().union(*(pd.concat([tc_rows["Agree"], tc_rows["Disagree"]])))
    data_path = supporting_material_root_dir / pathlib.Path(
        target_conjugate[0] + "_" + target_conjugate[1]
    )
    validated_files = []
    for orcid in orcids:
        md_file_path = data_path / pathlib.Path(orcid + ".md")
        if not md_file_path.is_file():
            raise ValueError(f"Missing expected supporting file {md_file_path}")
        orcid_configurations = tc_rows[
            tc_rows["Agree"].apply(lambda x: orcid in x)
            | tc_rows["Disagree"].apply(lambda x: orcid in x)
        ]
        # drop the 'Agree'/'Disagree' columns they are not part of the configuration
        orcid_configurations = orcid_configurations.loc[
            :, ~orcid_configurations.columns.isin(["Agree", "Disagree"])
        ]
        try:
            # read file content remove all rows that are only whitespace and
            # remove leading or trailing whitespace from all other rows
            with open(md_file_path, "r", encoding="utf-8") as f:
                content = f.read().split("\n")
            content = [c.strip() for c in content if c.strip()]
            # Get configurations table, this needs to match the information in the csv file
            config_start_section = content.index("# Configurations") + 1
            config_end_section = content.index("# Reasoning")
            columns = [
                column.strip()
                for column in content[config_start_section].split("|")
                if column.strip()
            ]
            table_content = []
            for r_index in range(config_start_section + 2, config_end_section):
                # split the table columns and get rid of the preceding and trailing strings that correspond to table
                # borders '|'
                table_content.append(
                    [rc.strip() for rc in content[r_index].split("|")][1:-1]
                )
            supporting_orcid_configurations = pd.DataFrame(
                data=table_content, columns=columns
            )
            supporting_orcid_configurations = supporting_orcid_configurations.loc[
                :, ~supporting_orcid_configurations.columns.isin(["Agree", "Disagree"])
            ]
            unique_supporting_orcid_configurations = (
                supporting_orcid_configurations.drop_duplicates()
            )
            if len(supporting_orcid_configurations) != len(
                unique_supporting_orcid_configurations
            ):
                raise ValueError(
                    f"Supporting file {md_file_path} configurations table contains duplicate entry."
                )
            # Compare the configuration data from the supporting material to that from the roadmap file.
            # We don't use DataFrame.equal because that assumes the order of the columns and indexes is the same,
            # which is a harder constraint than needed.
            if (
                len(unique_supporting_orcid_configurations) != len(orcid_configurations)
            ) or (
                len(
                    pd.concat(
                        [unique_supporting_orcid_configurations, orcid_configurations]
                    ).drop_duplicates()
                )
                != len(unique_supporting_orcid_configurations)
            ):
                raise ValueError(
                    f"Supporting file {md_file_path} configurations table does not match content of roadmap file"
                )
            validated_files.append(md_file_path)
        except Exception:
            raise ValueError(
                f"Supporting file {md_file_path} format does not match expected format"
            )
    return validated_files


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Validate knowledge base.")
    parser.add_argument("json_config_file", type=file_path)
    parser.add_argument("roadmap_csv", type=file_path)
    parser.add_argument("supporting_material_root_dir", type=dir_path)
    parser.add_argument("zenodo_json", type=file_path)

    args = parser.parse_args(argv)
    return validate_data(
        args.json_config_file,
        args.roadmap_csv,
        args.supporting_material_root_dir,
        args.zenodo_json,
    )


if __name__ == "__main__":
    sys.exit(main())
