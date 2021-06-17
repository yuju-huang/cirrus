#!/bin/bash


BASE_DIR=$PWD

for dir in $PWD/*; do
    cd $dir

    gzip -d *.gz
done
