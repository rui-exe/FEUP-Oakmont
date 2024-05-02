# This file intended to be sourced

# . /build/config.sh

HBASE_DIST="https://dlcdn.apache.org/hbase"
HADOOP_DIST="https://dlcdn.apache.org/hadoop/common/hadoop"


# Prevent initramfs updates from trying to run grub and lilo.
export INITRD=no
export DEBIAN_FRONTEND=noninteractive
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

minimal_apt_get_args='-y --no-install-recommends'


## Build time dependencies ##
BUILD_PACKAGES="curl"

## Build and run time dependencies
BUILD_RUN_PACKAGES="openssh-server openssh-client sudo"

## Run time dependencies ##
RUN_PACKAGES="openjdk-11-jre-headless"