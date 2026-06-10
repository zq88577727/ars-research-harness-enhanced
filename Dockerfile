FROM rocker/r-ver:4.5.1

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt /workspace/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /workspace/requirements.txt

RUN Rscript -e 'install.packages(c("haven","dplyr","readr","survey","ggplot2"), repos="https://cloud.r-project.org")'

COPY . /workspace

CMD ["python3", "harness/scripts/run_all_validations.py"]
