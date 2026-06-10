# Reproducibility Notes

This project now uses three reproducibility layers:

1. `requirements.txt` pins Python package versions used by table and DOCX tools.
2. `renv.lock` records the intended R package set for the analysis scripts.
3. `.Rprofile` and `Dockerfile` point R package installation to a dated Posit
   Package Manager snapshot.

For strict production use, run the project inside the Docker image or restore R
packages from `renv.lock` in an isolated R library. For teaching use, the local
system R installation is acceptable as long as the validation suite passes and
the analysis logs record package versions.

