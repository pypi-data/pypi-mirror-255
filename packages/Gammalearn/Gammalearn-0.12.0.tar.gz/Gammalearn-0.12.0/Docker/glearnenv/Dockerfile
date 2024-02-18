# gammalearn conda environment with dependencies pre-installed
FROM gitlab-registry.in2p3.fr/gammalearn/gammalearn/mamba:master

LABEL maintainer="GammaLearn https://purl.org/gammalearn"

COPY . gammalearn

RUN conda env create -f gammalearn/environment.yml -n glearn; conda clean -a

RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc
RUN sed 's/conda activate base/conda activate glearn/' ~/.bashrc > /tmp/tmpbash.txt && mv /tmp/tmpbash.txt ~/.bashrc

RUN rm -rf gammalearn

CMD bash
