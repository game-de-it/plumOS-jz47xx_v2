FROM debian:bookworm

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    bash bc binutils bison build-essential ca-certificates cpio curl dosfstools \
    e2fsprogs fdisk file flex git libncurses-dev libssl-dev mtools patch perl \
    python3 rsync sed tar unzip util-linux wget xz-utils zstd \
    && rm -rf /var/lib/apt/lists/*
