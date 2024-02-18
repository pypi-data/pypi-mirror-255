# OAT (Observation Analysis Tool)

A Python library (oatlib) to manage sensor data in Python.
It provides objects and methods to manipulate
obeservation time series. It support data loading, export and saving
on different format (CSV, sqlite, istSOS).

- lib documentation: https://ist-supsi.gitlab.io/OAT

## installation

> pip install oatlib

## Create pypi package

modify the code and
**change the VERSION in **init**.py**

# run scipy-notebook docker

docker run -p 10001:8888 -v /home/maxi/GIT/OAT:/home/jovyan/work jupyter/scipy-notebook:807999a41207

# in jupyter-lab terminal:

# install required packages -->
cd /home/jovyan/work
python -m pip install --upgrade setuptools
python -m pip install --upgrade pip
python -m pip install --upgrade build

# build the package -->
python -m build

# test the package in your notebook

pip install /home/jovyan/work/dist/oatlib-**YOUR_VERSION_HERE**-py3-none-any.whl

# upload to pipy

python -m pip install --upgrade twine
twine upload dist/\*

## update library documentation

pip install pdoc3
pdoc3 --force --html -o html_doc oatlib
--> we have some issue here (see bug https://github.com/pdoc3/pdoc/issues/299)

## test in a 3.10.5 python

docker run -p 10000:8888 -v /home/maxi/GIT/OAT/oatlib:/home/jovyan/work jupyter/scipy-notebook:807999a41207

## old packg build CMD

python setup.py sdist bdist_wheel
