# Use the Ubuntu latest image as the base image
FROM ubuntu:latest

# Update the package manager's package index
RUN apt-get update  \
    && apt-get -y upgrade \
    # && apt-get install -y build-essential \
    && apt-get install --fix-missing \
    # tzdata is the timezone data package for Linux systems and it allows to set the system's timezone.
    && apt-get install -y tzdata \
    # Install the software-properties-common package
    # This package contains the add-apt-repository command, which we'll use later to add a package repository
    && apt-get install -y software-properties-common \
    # Add the deadsnakes PPA (Personal Package Archive) as a package repository
    # This repository contains the latest version of Python
    && add-apt-repository ppa:deadsnakes/ppa \
    # && apt-get update \
    # Install the latest version of Python (3.9) \
    && apt-get install -y python3.9 \
    # Install the python3-pip package
    # This package contains the pip3 command, which we'll use later to install packages
    && apt-get install -y python3-pip \
    # Install Java for Spark
    && apt-get install -y openjdk-8-jdk

# Use pip3 to install the pyspark and pytest packages
RUN pip3 install pyspark pytest coverage

# Run the 'pytest' module to execute all the tests in the 'tests/' directory in verbose mode
# CMD tail -f /dev/null
CMD cat 'scripts/banner.txt' && echo '\n' && coverage run -m pytest . -v && coverage report -m
