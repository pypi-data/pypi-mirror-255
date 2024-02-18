# This file is sourced in the sh() function of uniws.
# It also can be sourced manually, if needed.

export UNIWS_DIR_ROOT="$(realpath "$(dirname ${BASH_SOURCE[0]})/..")"
export UNIWS_DIR_BIN="${UNIWS_DIR_ROOT}/bin"
export UNIWS_DIR_ETC="${UNIWS_DIR_ROOT}/etc"
export UNIWS_DIR_LIB="${UNIWS_DIR_ROOT}/lib"
export UNIWS_DIR_TMP="${UNIWS_DIR_ROOT}/tmp"
export PATH="${UNIWS_DIR_BIN}:${UNIWS_DIR_LIB}:${PATH}"
export PYTHONPATH="${UNIWS_DIR_LIB}:${PYTHONPATH}"
export LD_LIBRARY_PATH="${UNIWS_DIR_LIB}:${LD_LIBRARY_PATH}"

# Add custom environment and actions below.
