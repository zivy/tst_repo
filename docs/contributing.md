# Contributing
This knowledge-base follows the standard GitHub
[fork and pull request, triangular workflow](https://guides.github.com/activities/forking/).

To contribute your knowledge, please follow these steps:

## One time setup
1. Install [git](https://git-scm.com/downloads) and [git-lfs](https://git-lfs.github.com/).
2. If you are not comfortable working with git and GitHub from the command-line, download the [GitHub Desktop](https://desktop.github.com/) application and [read the installation and configuration help](https://docs.github.com/en/desktop/installing-and-configuring-github-desktop).
3. Fork this repository and clone it to a local directory ([GitHub Desktop instructions](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop)).
4. Add your information to the "creators" section in the .zenodo.json file.

## Adding information to the knowledge-base

#### Before starting to work
Create a new local git branch based off of the `main` branch ([GitHub Desktop instructions](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/making-changes-in-a-branch/managing-branches#creating-a-branch)).

#### Adding information to the FAQ:
If adding an answer to the [FAQ](FAQ.md), simply edit that file.

#### Adding new information to the IBEX configurations file:
1. Add a line to the [roadmap.csv](roadmap.csv).
2. Create corresponding supporting material sub-directory using the target_conjugate as the directory name and add a markdown file with your ORCID as the file prefix (see existing files for reference). Supporting material file has a fixed layout, given in the [template_file.md](supporting_material/template_file.md).
3. Optionally add **small** image files (jpg, png, tiff) and refer to them in the supporting material file.

#### Adding information to existing line in the IBEX configurations file:
1. Add your ORCID to the `Agree` or `Disagree` column on the appropriate line in the roadmap file, use a semicolon `;` to separate from the previous ones (e.g. `ORCID1; ORCID2; ORCID3`).
2. If after adding your vote:
  * The number of ORCIDs in the `Disagree` column is greater than those in the `Agree` column:
    1. Change the content of the `Result` column from "Success" to "Failure" or the other way round and swap the ORCIDs between the `Agree` and `Disagree` columns.
    2. Modify all the supporting material markdown files associated with this row, changing the `Result` and `Recommendation` sections.
3. Add a markdown file with your ORCID to the existing sub-directory. Easiest option is to copy the contents of one of the markdown files already in this directory and modify it.
4. Optionally add **small** image files (jpg, png, tiff) and refer to them in the supporting material file.

#### After work is completed
After completing the work we need to update the knowledge-base, this can be done using git on the command-line or using GitHub desktop:
1. Commit the changes ([GitHub Desktop instructions](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/making-changes-in-a-branch/committing-and-reviewing-changes-to-your-project)).
2. Push the commit to GitHub ([GitHub Desktop instructions](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/making-changes-in-a-branch/pushing-changes-to-github)).
3. Create a pull-request on GitHub ([GitHub Desktop instructions](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request#creating-a-pull-request)).
