#!/usr/bin/env bash
set -euo pipefail

# Update notebooks by running all cells and overwriting the original file with
# the result.

for notebook in "$@"
do
  jupyter nbconvert --to notebook --inplace --execute "$notebook"
done
