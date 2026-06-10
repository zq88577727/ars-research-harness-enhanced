# Public Database Adapters

This directory defines source-aware adapters for public or semi-public medical
research databases.

The key rule is honesty about access:

- NHANES public-use example files are included in the teaching case.
- CHARLS requires registered access through the CHARLS data portal; raw CHARLS
  data should not be committed here.
- GBD should be handled through query manifests and approved exports from the
  GBD Results Tool or an approved API/download route; raw bulk exports should
  only be committed when the license and size are appropriate.

Adapters are metadata contracts. They tell the workflow what questions, weights,
source files, and reporting risks must be resolved before analysis and drafting.

