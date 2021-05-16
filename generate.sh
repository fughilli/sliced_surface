#!/bin/bash

mkdir outputs
python3 generate.py && openscad stack.scad -o stack.stl
rm -Rf outputs
fstl stack.stl
rm stack.stl
