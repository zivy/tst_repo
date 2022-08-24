---
permalink: /questions_and_answers/
---

# Questions and Answers

Multiplex imaging protocols are complex, they involve a variety of technologies and deal with both physical elements and computational ones. Accurately describing all aspects of a protocol in sufficient detail to consistently obtain high quality results is a work in progress. Detailed descriptions addressing all aspects of a protocol need to span the gamut from physical sample handling to software settings used by the computational components utilized in the work.

This file contains questions and answers addressing various aspects of the IBEX imaging protocol which were not addressed in publications, or which were not sufficiently clear to scientists from their descriptions in the publications.


1. I get the following error, "CondaHTTPError: HTTP 000 CONNECTION FAILED for url...".

  When following the [setup instructions](https://github.com/niaid/imaris_extensions#setup) creation of the virtual environment fails with a CondaHTTPError.

  This error is most likely due to your institution's proxy server security settings. To resolve proxy server issues, see the [instructions provided in the anaconda documentation](https://docs.anaconda.com/anaconda/user-guide/tasks/proxy/) and possibly the instructions for using [non standard certificates](https://conda.io/projects/conda/en/latest/user-guide/configuration/non-standard-certs.html).
  This [stack-overflow discussion](https://stackoverflow.com/questions/33883371/python-anaconda-proxy-setup-via-condarc-file-on-windows) may also be of interest.
2. I am using the registration application from the [imaris extensions GitHub repository](https://github.com/niaid/imaris_extensions) and it fails. Are there settings I can change to make it work?

 Yes, there are. For common failure modes and various settings that you can try, see the application's `Help` menu or [this web page](https://niaid.github.io/imaris_extensions/XTRegisterSameChannel.html).   
