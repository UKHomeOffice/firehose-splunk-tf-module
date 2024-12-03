#!/bin/bash

rm -rf venv_package
rm -rf package
mkdir package
python3.12 -m venv venv_package
source ./venv_package/bin/activate
pip install -r requirements.txt
deactivate
cp -r venv_package/lib/python3.*/site-packages/* package/
cp src/mbtp_splunk_cloudwatch_transformation/handler.py package/
rm -rf venv_package
# zip -r package/handler.zip package/