---
permalink: /
---

![](ibex_banner.png?raw=true)

[![Creative Commons License](https://i.creativecommons.org/l/by-nc/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc/4.0/) &nbsp;&nbsp;&nbsp;&nbsp; [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)



# Iterative Bleaching Extends Multiplexity (IBEX) Knowledge-Base

The Iterative Bleaching Extends Multiplexity (IBEX) imaging method is an iterative immunolabeling and chemical bleaching method that enables multiplexed imaging in diverse tissues . The method was originally developed in the [Laboratory of Immune System Biology](https://www.niaid.nih.gov/research/lab-immune-system-biology) at the US National Institutes of Health [[Radtke et al. 2020](https://doi.org/10.1073/pnas.2018488117), [Radtke et al. 2022](https://doi.org/10.1038/s41596-021-00644-9)].

* A. J. Radtke et al., "IBEX: A versatile multiplex optical imaging approach for deep phenotyping and spatial analysis of cells in complex tissues", Proc. Natl. Acad. Sci. USA, 117(52): 33455-33465, 2020, [doi: 10.1073/pnas.2018488117](https://doi.org/10.1073/pnas.2018488117).
* A. J. Radtke et al., "IBEX: an iterative immunolabeling and chemical bleaching method for high-content imaging of diverse tissues", Nat. Protoc., 17(2):378-401, 2022, [doi: 10.1038/s41596-021-00644-9](https://doi.org/10.1038/s41596-021-00644-9).

## Citation

To cite the IBEX knowledge-base use the Digital Object Identifier (DOI) [provided by Zenodo](https://zenodo.org/). Please take care to use the DOI associated with the specific version of the knowledge-base used in your work.

## Download

The authoritative and versioned form of the knowledge-base will be available for download from [Zenodo](https://zenodo.org/).

This repository is a work-in-progress and is not an authoritative version of the knowledge-base.

## Structure
The knowledge-base can be explored from two starting points, [roadmap.csv](roadmap.csv) and [FAQ.md](FAQ.md). The former is the primary starting point and contains high level information describing successful and failed IBEX configurations (based on target-conjugate, dye, organelle marker etc.). The later contains a set of questions and answers on various aspects of the IBEX imaging protocol. These were either not addressed in publications, or were not sufficiently clear to scientists from their descriptions in the publications.

To facilitate browsing on GitHub a markdown file ([roadmap.md](roadmap.md)) file is automatically generated from the [roadmap.csv](roadmap.csv) file. It includes hyperlinks to the supporting materials files, so that you can easily move between this high level file
and the supporting material files.

```
ibex_knowledge_base
│   roadmap.csv
│   roadmap.md
│   FAQ.md   
│   ...   
│
└───supporting_material
    │
    └───CD69_AF647
    │   │  0000-0003-4379-8967.md
    │   │  0000-0003-0315-7727.md
    │   │  ...
    │    
    └───CD34_PE
    │   │  0000-0003-1495-9143
    │   │  ...
    │
    ...
```
## Overview

This repository contains the current state of knowledge
with respect to the IBEX imaging protocol. The authoritative, versioned, knowledge-base is [available on Zenodo](https://zenodo.org/).

Unlike publications, in which only successful work is described, the goal of this knowledge-base (a.k.a. [data lake](https://en.wikipedia.org/wiki/Data_lake)) is to document both *successful and failed* work. By sharing failures we advance science at a faster pace while reducing financial costs. Sharing failures prevents other researchers from wasting time and effort on work that is known to fail. In addition to the time savings, the savings in material costs are non-negligible (developing multiplex imaging protocols is not a low-cost activity).

## Addressing a Need, The "Game" of Science

As scientists we strive to enable others to reproduce our work, confirming or refuting our results, thus making science self-correcting. Self correction does not happen by default, it requires an explicit effort on our part [[Ioannidis 2012](https://doi.org/10.1177/1745691612464056)]. This knowledge-base reflects the effort of the IBEX imaging community.

While refuting results or disagreeing with others may not be the most pleasant thing to do, it is a critical component of the scientific process. We are also aware that for the more junior members of the community this is likely a harder thing to do [[Vazire 2020](https://doi.org/10.1038/d41586-019-03909-2)]. To address any apprehensions, we follow the Contributor Covenant v2.1 [code of conduct](CODE_OF_CONDUCT.md). More specifically, the IBEX imaging community conducts discourse in a civil manner and members of the community share their scientific findings without fear of disagreements with senior members having repercussions on ones scientific career.

* J. P. A. Ioannidis, "Why Science Is Not Necessarily Self-Correcting", Perspect Psychol Sci., 7(6):645-654, 2012, [doi:10.1177/1745691612464056](https://doi.org/10.1177/1745691612464056).
* S. Vazire, "A toast to the error detectors", Nature, 577(7788):9, 2020, [doi: 10.1038/d41586-019-03909-2](https://doi.org/10.1038/d41586-019-03909-2).


## Knowledge-Base (Data Lake) design and rationale

The knowledge-base roadmap is comprised of a single comma-separated-value file, [roadmap.csv](roadmap.csv). Each row in the file contains information with respect to a target-conjugate, a dye, an organelle marker etc. This file is the starting point for exploring the knowledge-base. A markdown version of the roadmap file is automatically created with links to the supporting material files. This enables convenient browsing of these files on GitHub.

When adding content to the file one is **required to provide supporting material**. This can be in the form of a reference to a peer reviewed publication, when reporting successes, or in the form of images and textual explanations when reporting failures. In addition, we highly encourage contributors to provide detailed notes (often omitted from publications due to space limitations).

The supporting material is comprised of an [ASCII text file](https://en.wikipedia.org/wiki/Text_file) using [GitHub markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) for richer content, and possibly images in png, jpg, and tiff formats which are referred to in the text file. The supporting material for each row is found, not surprisingly, in the directory `supporting_material/target_conjugate/ORCID.md`, where the `target_conjugate` are those listed in the row and the `ORCID` is the contributor's [Open Researcher and Contributor ID](https://orcid.org/).

By using simple data formats, csv and markdown, we ensure that the raw files are:
1. Human readable.
2. Supported by many editors (excel/google docs/notepad/emacs...).
3. Will be readable far into the future.

By developing the knowledge-base using a public git repository on GitHub and GitHub's standard, fork and pull request, triangular workflow, we:
1. Enable controlled addition of knowledge via automated testing and human oversight from a broad community.
2. Instill trust in the knowledge-base by developing the knowledge-base in public view of the community.
3. Clearly document contributions, a side effect of using git (every commit is naturally associated with a specific person).

By distributing the knowledge-base via Zenodo, we:
1. Automatically obtain a DOI for each version of the knowledge-base.
2. Enable citation of the work via the DOI.
