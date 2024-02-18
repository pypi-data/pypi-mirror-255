#!/usr/bin/env bash
set -euo pipefail

SELF=$(readlink -f "${BASH_SOURCE[0]}")
DIR=${SELF%/*/*}
DOC_DIR=$DIR/doc
SRC_DIR=$DIR/src

python3 -m venv venv
source venv/bin/activate

pip install "$DIR"
jnp --config "$DIR/config.yaml"

pip install -r "$DOC_DIR/requirements.txt"
sphinx-apidoc -o "$DOC_DIR/source" -f -H 'API Documentation' "$SRC_DIR"
mkdir -p "public/sphinx"
sphinx-build -b html "$DOC_DIR/source" "public/sphinx"
