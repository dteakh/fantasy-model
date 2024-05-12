#!/bin/bash

python3 -m flake8 ../parsing;
python3 -m isort ../parsing;
python3 -m black ../parsing;
