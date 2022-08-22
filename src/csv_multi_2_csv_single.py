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
import argparse
import sys
from argparse_types import file_path
import traceback

"""
This utility script converts a csv file containing multiple entries per row to
a csv file containing a single entry per row, which is the format the knowledge-base
uses. While multiple entries per row makes for a compact representation which is easier
for the expert to write, it is harder for the newcomer and other experts to follow and
interpret. With a single entry per row the data can be easily read by all in an
unambiguous manner.

Example:

Original, multiple entries per row:
| UniProt Accession Number   | Target Name / Protein Biomarker   | Antibody Name                | Host Organism and Isotype   | Clonality   | Vendor    |   Catalog Number | Conjugate   | RRID      | Application    | Method                          | Tissue Preservation   | Tissue                          | Detergent         |   Antigen Retrieval Conditions | Dye Inactivation Conditions                                                                      | Result   | Agree               |   Disagree | # noqa E501 
|:---------------------------|:----------------------------------|:-----------------------------|:----------------------------|:------------|:----------|-----------------:|:------------|:----------|:---------------|:--------------------------------|:----------------------|:--------------------------------|:------------------|-------------------------------:|:-------------------------------------------------------------------------------------------------|:---------|:--------------------|-----------:|
| P19320                     | CD106                             | PE anti-human CD106 Antibody | Mouse IgG1, Kappa           | STA         | BioLegend |           305806 | PE          | AB_314561 | IHC-Fr; IHC-Fr | IBEX2D Automated; IBEX2D Manual | 1% PFA Fixed Frozen   | Human jejunum; Human lymph node | 0.3% Triton-X-100 |                            nan | 0.5 mg/ml LiBH4 10 minutes continuous exchange with automated protocol; 1 mg/ml LiBH4 15 minutes | Success  | 0000-0003-4379-8967 |        nan |

Resulting, single entry per row:
| UniProt Accession Number   | Target Name / Protein Biomarker   | Antibody Name                | Host Organism and Isotype   | Clonality   | Vendor    |   Catalog Number | Conjugate   | RRID      | Application   | Method           | Tissue Preservation   | Tissue           | Detergent         | Antigen Retrieval Conditions   | Dye Inactivation Conditions                                            | Result   | Agree               |   Disagree |
|:---------------------------|:----------------------------------|:-----------------------------|:----------------------------|:------------|:----------|-----------------:|:------------|:----------|:--------------|:-----------------|:----------------------|:-----------------|:------------------|:-------------------------------|:-----------------------------------------------------------------------|:---------|:--------------------|-----------:|
| P19320                     | CD106                             | PE anti-human CD106 Antibody | Mouse IgG1, Kappa           | STA         | BioLegend |           305806 | PE          | AB_314561 | IHC-Fr        | IBEX2D Automated | 1% PFA Fixed Frozen   | Human jejunum    | 0.3% Triton-X-100 |                                | 0.5 mg/ml LiBH4 10 minutes continuous exchange with automated protocol | Success  | 0000-0003-4379-8967 |        nan |
| P19320                     | CD106                             | PE anti-human CD106 Antibody | Mouse IgG1, Kappa           | STA         | BioLegend |           305806 | PE          | AB_314561 | IHC-Fr        | IBEX2D Manual    | 1% PFA Fixed Frozen   | Human lymph node | 0.3% Triton-X-100 |                                | 1 mg/ml LiBH4 15 minutes                                               | Success  | 0000-0003-4379-8967 |        nan |
"""


def entry2list(entry):
    if pd.isna(entry) or entry.strip() == "":
        return [" "]
    else:
        res_list = [v.strip() for v in entry.split(";") if v.strip() != ""]
        return res_list


def single_2_multi(row):
    # Indexes of columns that can contain multiple entries. The separator
    # character between entries is semicolon (see entry2list).
    indexes_2_list = [
        "Application",
        "Method",
        "Tissue Preservation",
        "Tissue",
        "Antigen Retrieval Conditions",
        "Dye Inactivation Conditions",
    ]
    for i in indexes_2_list:
        row[i] = entry2list(row[i])

    # For the "Application", "Tissue Preservation", "Tissue", "Antigen Retrieval Conditions" and
    # "Dye Inactivation Conditions" accommodate situations where only a single value is entered
    # even if there should be multiple values.
    entry_num = len(row["Method"])
    if len(row["Application"]) != entry_num:
        row["Application"] = row["Application"] * entry_num
    if len(row["Tissue Preservation"]) != entry_num:
        row["Tissue Preservation"] = row["Tissue Preservation"] * entry_num
    if len(row["Tissue"]) != entry_num:
        row["Tissue"] = row["Tissue"] * entry_num
    if len(row["Antigen Retrieval Conditions"]) != entry_num:
        row["Antigen Retrieval Conditions"] = (
            row["Antigen Retrieval Conditions"] * entry_num
        )
    if len(row["Dye Inactivation Conditions"]) != entry_num:
        row["Dye Inactivation Conditions"] = (
            row["Dye Inactivation Conditions"] * entry_num
        )

    expand_list = []
    # separate single row containing multiple entries to multiple rows containing a single entry.
    # also remove preceding and trailing whitespace
    for i in range(entry_num):
        expand_list.append(
            [
                row["UniProt Accession Number"].strip(),
                row["Target Name / Protein Biomarker"].strip(),
                row["Antibody Name"].strip(),
                row["Host Organism and Isotype"].strip(),
                row["Clonality"].strip(),
                row["Vendor"].strip(),
                row["Catalog Number"].strip(),
                row["Conjugate"].strip(),
                row["RRID"].strip(),
                row["Application"][i].strip(),
                row["Method"][i].strip(),
                row["Tissue Preservation"][i].strip(),
                row["Tissue"][i].strip(),
                row["Detergent"].strip(),
                row["Antigen Retrieval Conditions"][i].strip(),
                row["Dye Inactivation Conditions"][i].strip(),
                row["Result"].strip(),
                row["Agree"].strip(),
                row["Disagree"].strip(),
            ]
        )
    return pd.DataFrame(expand_list, columns=row.index)


def csv_multi_2_csv_single(csv_file):
    # Read the dataframe and keep entries that are "NA", don't convert to nan
    df = pd.read_csv(csv_file, dtype=str, keep_default_na=False)
    res = df.apply(
        lambda x: single_2_multi(x),
        axis=1,
    )
    return pd.concat(res.to_list())


def main(argv=None):
    if argv is None:  # script was invoked from commandline
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("multi_entry_csv_file", type=file_path)
    parser.add_argument("single_entry_csv_file", type=str)
    args = parser.parse_args(argv)

    try:
        df = csv_multi_2_csv_single(args.multi_entry_csv_file)
        df.to_csv(args.single_entry_csv_file, index=False)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
