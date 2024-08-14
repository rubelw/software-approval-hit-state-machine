#!/usr/bin/env bash

cd tf
for file in *.tf; do mv "$file" "${file%.tf}.tf.bak"; done
