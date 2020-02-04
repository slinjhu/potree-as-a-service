FROM ubuntu:19.04 AS builder
ARG NPROC=8

RUN apt-get update -y && apt-get install -y --no-install-recommends \
  software-properties-common build-essential \
  time curl wget unzip git sudo \
  autoconf libtool cmake automake ssh-client \
  && ldconfig && apt-get clean && rm -rf /var/lib/apt/lists/*


# Install PotreeConverter, a tool to visualize 3D point cloud data.
RUN set -ex; \
    cd /tmp && git clone --depth 1 https://github.com/m-schuetz/LAStools.git; \
    cd LAStools/LASzip && mkdir build && cd build && cmake -DCMAKE_BUILD_TYPE=Release ..;\
    make -j${NPROC}; \
    make install; \
    ldconfig; \
    cd /tmp && git clone --depth 1 -b 1.6_2018_07_29 https://github.com/potree/PotreeConverter.git; \
    cd PotreeConverter && mkdir build && cd build && \
      cmake -DCMAKE_BUILD_TYPE=Release \
        -DLASZIP_INCLUDE_DIRS=/tmp/LAStools/LASzip/dll \
        -DLASZIP_LIBRARY=/tmp/LAStools/LASzip/build/src/liblaszip.so ..; \
    make -j${NPROC}; \
    cp -r ../PotreeConverter/resources / ; \
    make install; \
    ldconfig; \
    rm -rf /tmp/*

FROM ubuntu:19.04 AS base

RUN apt-get update -y && apt-get install -y --no-install-recommends \
  python3 python3-pip python3-setuptools \
  nginx liblas-c3 \
  && ldconfig && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN rm -rf /etc/nginx/sites-enabled/*

COPY --from=builder /usr/local/bin/PotreeConverter /usr/local/bin/PotreeConverter
COPY --from=builder /usr/local/lib/liblaszip.so /usr/local/lib/liblaszip.so
RUN ldconfig

RUN pip3 install --no-cache-dir -U pip setuptools wheel
RUN pip3 install --no-cache-dir liblas \
    aiohttp aiofiles aiohttp_jinja2 \
    PyYAML rainbow-logging-handler


ENV PYTHONPATH /src:${PYTHONPATH}

FROM base AS dev
# Nothing special for now

FROM base AS prod

COPY ./src /src

WORKDIR /src
EXPOSE 80
ENTRYPOINT ["python3", "/src/app.py"]
