#!/bin/bash
# Instala ptts en /work y sintetiza. Uso: run.sh <en|es> <escena|all>
set -u
export HF_HOME=/work/hf
export HOME=/work/home
export TMPDIR=/work/tmp
export XDG_CACHE_HOME=/work/cache
mkdir -p "$HOME" "$TMPDIR" "$XDG_CACHE_HOME"
# El token se monta en solo lectura y no se copia a /work.
if [ -f /run/hf_token ]; then export HF_TOKEN="$(tr -d '\r\n' < /run/hf_token)"; fi
if [ ! -x /work/venv/bin/python ]; then
  python -m venv --copies /work/venv || exit 10
  /work/venv/bin/pip install -q ptts || exit 11
fi
/work/venv/bin/pip show ptts | grep -E '^(Name|Version|License)'
/work/venv/bin/python /work/synth.py "$1" "$2"
