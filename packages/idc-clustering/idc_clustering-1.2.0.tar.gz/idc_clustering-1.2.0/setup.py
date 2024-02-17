# Copyright 2024 idc_clustering(https://gitee.com/hai_li_de/gitee-clustering.git). All Rights Reserved.
#
# Licensed under the Apache License, Version 1.2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="idc_clustering",
    version="1.2.0",
    author="idc_clustering",
    author_email="1262043823@qq.com",
    description="A clustering library that can return which cluster it belongs to",
    long_description="A clustering library that can learn based on historical data and classification labels."
                " The current version can only test and classify a set of data. "
                "The test classification of batch data will be updated later, "
                "and will return which historical learning data the test data belongs to. Classification tags",
    long_description_content_type="text/markdown",
    url="https://gitee.com/hai_li_de/gitee-clustering.git",
    packages=['idc_clustering'],
    install_requires=['pydantic', 'cushy-storage'],
    python_requires='>=3.6',
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",

    ],
    keywords="idc_clustering, clustering-service, Return to category tags",
)