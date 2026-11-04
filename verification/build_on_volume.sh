#!/bin/bash
# Compila el Lean de OpenAI en un volumen de Docker. Los registros quedan en /logs (D:).
set -u
COMMIT=f9e8bc5b38b6e212696e8a30e3e91517af887bbd
export ELAN_HOME=/vol/elan
export HOME=/vol/home
export TMPDIR=/vol/tmp
export XDG_CACHE_HOME=/vol/cache
mkdir -p "$HOME" "$TMPDIR" "$XDG_CACHE_HOME"
export PATH="$ELAN_HOME/bin:$PATH"

stamp() { echo "=== $(date -u +%FT%TZ) $*"; df -h /vol | tail -1; }

stamp apt
apt-get update -qq && apt-get install -y -qq --no-install-recommends git curl ca-certificates zstd >/dev/null || exit 10

stamp elan
if [ ! -x "$ELAN_HOME/bin/elan" ]; then
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o /tmp/elan-init.sh || exit 11
  sh /tmp/elan-init.sh -y --no-modify-path --default-toolchain none || exit 11
fi

stamp clone
git config --global --add safe.directory '*'
git config --global core.autocrlf false
if [ ! -d /vol/repo/.git ]; then
  git clone --filter=blob:none https://github.com/openai/NavierStokesAndEuler.git /vol/repo || exit 12
fi
cd /vol/repo || exit 12
git checkout -q "$COMMIT" || exit 12
echo "HEAD $(git rev-parse HEAD)"
cat lean-toolchain

stamp cache
lake exe cache get 2>&1 | tail -5
echo "CACHE_EXIT ${PIPESTATUS[0]}"

stamp build
lake build NavierStokes.ComparatorSolution > /logs/build.log 2>&1
BUILD=$?
echo "BUILD_EXIT $BUILD"
grep -E "error|declaration uses|Build completed|build failed" /logs/build.log | tail -30

stamp axioms
grep -n -A2 "depends on axioms" /logs/build.log | tail -20
stamp fin
exit "$BUILD"
