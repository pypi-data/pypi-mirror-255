# -*- coding: utf-8 -*-
# Copyright (C) Alexander Pace, Duncan Meacher (2021)
#
# This file is part of igwn-alert
#
# igwn-alert is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with igwn-alert.  If not, see <http://www.gnu.org/licenses/>.
#
import sys
from setuptools import (
    setup,
    find_packages,
)

version = "0.6.0"

# Pinning some old requirements for a few centos
# container holdouts
if sys.version_info > (3, 7):
    install_requires = [
        "adc-streaming>=2.3.0",
        "confluent-kafka>=2.0.0",
        "hop-client>=0.7.0",
        "pyopenssl>=23.0.0",
        "safe-netrc",
        "setuptools",
    ],
else:
    install_requires = [
        "adc-streaming<=2.1.0",
        "confluent-kafka<2.0.0",
        "hop-client>=0.7.0",
        "pyopenssl>=23.0.0",
        "safe-netrc",
        "setuptools",
    ],

setup(
    # metadata
    name="igwn-alert",
    version=version,
    maintainer="Alexander Pace, Duncan Meacher",
    maintainer_email=(
        "alexander.pace@ligo.org, "
        "duncan.meacher@ligo.org, "
    ).rstrip(", "),
    description="IGWN Alert Network",
    long_description=(
        "The IGWN Alert System (igwn-alert) is a prototype notification "
        "service built on Apache Kafka, using the publish-subscribe "
        "(pubsub) protocol. It is a higher-level modification of SCIMMA's "
        "hop-client to streamline receiving and responding to alerts from "
        "GraceDB."
    ),
    url="https://igwn-alert.readthedocs.io/",
    project_urls={
        "Bug Tracker": "https://git.ligo.org/computing/igwn-alert/client/-/issues",  # noqa: E501
        "Documentation": "https://igwn-alert.readthedocs.io/",
        "Source Code": "https://git.ligo.org/computing/igwn-alert/client",
    },
    license='GPLv3+',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: "
        "GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    # requirements
    python_requires=">=3.6",
    setup_requires=["setuptools"],
    install_requires=install_requires,
    # contents
    entry_points={
        'console_scripts': [
            'igwn-alert=igwn_alert.tool:main',
        ],
    },
    packages=find_packages(),
)
