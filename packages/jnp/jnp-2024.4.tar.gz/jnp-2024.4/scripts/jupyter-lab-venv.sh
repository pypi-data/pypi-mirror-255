#!/usr/bin/env bash
set -euo pipefail

if [[ ${BASH_VERSINFO[0]} -lt 5 ]]
then
  echo "warning: You are running Bash version $BASH_VERSION but this script expects at least version 5.0" >&2
fi

SELF=$(readlink -f "${BASH_SOURCE[0]}")
DIR=${SELF%/*/*}
VENV_DIR=jnp_venv

# Create and activate the Python virtual environment.
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install the latest versions of pip and ipykernel in the virtual environment
# along with this package. Also install jupyterlab if necessary.
venv_pkgs=(ipykernel)
if ! command -v jupyter-lab >/dev/null 2>&1
then
  venv_pkgs+=(jupyterlab)
fi
pip install --upgrade pip
pip install --upgrade "${venv_pkgs[@]}"
pip install --upgrade "$DIR"

# Install the custom kernel if necessary.
if ! (jupyter kernelspec list | grep "^[[:space:]]*${VENV_DIR}[[:space:]]" > /dev/null 2>&1)
then
	ipython kernel install --user --name="$VENV_DIR"
fi

# Add the src directory to the Python path.
if [[ -z ${PYTHONPATH:+x} ]]
then
	PYTHONPATH=$DIR/src
else
	PYTHONPATH="$DIR/src:$PYTHONPATH"
fi
export PYTHONPATH

# Notify the user of the browser option.
if [[ -z ${BROWSER:+x} ]]
then
	echo "Set the environment variable BROWSER to the full path of your prefered browser if Jupyter Lab does not launch it by default."
fi

jupyter-lab "$@" .
