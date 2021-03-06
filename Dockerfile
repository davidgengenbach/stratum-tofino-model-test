# These images are pre-built as described in https://github.com/stratum/stratum/blob/master/stratum/hal/bin/barefoot/README.run.md#running-stratum-on-tofino-model
FROM stratumproject/tofino-model:9.3.0 as tofino_model

FROM stratumproject/stratum-bfrt:9.3.0

# The next two statements come from https://github.com/stratum/stratum/blob/master/stratum/hal/bin/barefoot/docker/Dockerfile.model
ENV BUILD_DEPS \
    iproute2 \
    ethtool \
    procps \
    libcli1.9
RUN apt-get update && \
    apt-get install -y $BUILD_DEPS && \
    rm -rf /var/lib/apt/lists/*

COPY --from=tofino_model /usr/local/bin/tofino-model /usr/local/bin/
COPY --from=tofino_model /usr/local/bin/veth_setup.sh /usr/local/bin/
COPY --from=tofino_model /usr/local/bin/dma_setup.sh /usr/local/bin/
COPY --from=tofino_model /usr/share/stratum/tofino_skip_p4.conf /usr/share/stratum/
COPY --from=tofino_model /usr/local/bin/start-tofino-model.sh /usr/local/bin/
