# Conda base image with libmamba solver set as default and a few additions required for GammaLearn (git, wget, gcc)
FROM docker.io/condaforge/miniforge3:22.9.0-1

LABEL maintainer="GammaLearn https://purl.org/gammalearn"

RUN apt-get update && apt-get install -y git wget gcc

# use libmamba solver as default one
RUN conda install -n base conda-libmamba-solver; conda config --set solver libmamba

RUN conda clean -a
