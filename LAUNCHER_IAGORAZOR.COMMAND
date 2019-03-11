#!/bin/sh
echo Starting Iagorazor
export PYTHONPATH=$(dirname $0)/libs:$(dirname $0)/src/
cd $(dirname $0)/src
python -W ignore ./Razor.py
echo Done