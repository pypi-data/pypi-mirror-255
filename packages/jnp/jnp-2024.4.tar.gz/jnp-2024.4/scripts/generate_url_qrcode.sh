#!/usr/bin/env bash
set -euo pipefail

# Dependencies
# * Bash >=5.0 (https://gitlab.inria.fr/jrye/jnp)
# * qrencode (https://fukuchi.org/works/qrencode/)
# * scour (https://github.com/scour-project/scour)

URL=${1:-https://gitlab.inria.fr/jrye/jnp}
SELF=$(readlink -f "${BASH_SOURCE[0]}")
IMG_DIR=${SELF%/*/*}

cd -- "${SELF%/*/*}"
mkdir -p "$IMG_DIR"
cd "$IMG_DIR"
tmp_path=$(mktemp)
qrencode -o "$tmp_path" -t svg "$URL"
scour \
  --remove-titles \
  --remove-descriptions \
  --remove-metadata \
  --remove-descriptive-elements \
  --enable-comment-stripping \
  --enable-viewboxing \
  --indent=none \
  --strip-xml-space \
  --enable-id-stripping \
  --shorten-ids \
  "$tmp_path" url.svg
