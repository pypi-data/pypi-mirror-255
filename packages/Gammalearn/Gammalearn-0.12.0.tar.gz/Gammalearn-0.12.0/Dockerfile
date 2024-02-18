# gammalearn production-ready docker container

FROM gitlab-registry.in2p3.fr/gammalearn/gammalearn/glearnenv:master

LABEL maintainer="GammaLearn https://purl.org/gammalearn"

COPY . gammalearn

RUN . /opt/conda/etc/profile.d/conda.sh; conda activate glearn; cd gammalearn; conda env update -f environment.yml; pip install .; cd ..

RUN rm -rf gammalearn

CMD bash
