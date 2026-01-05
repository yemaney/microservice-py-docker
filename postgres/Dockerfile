FROM postgres:16

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

# Clone and build pgvector
RUN cd /tmp && \
    git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install

# Clean up build dependencies
RUN apt-get remove -y build-essential git postgresql-server-dev-16 && \
    apt-get autoremove -y && \
    rm -rf /tmp/pgvector
