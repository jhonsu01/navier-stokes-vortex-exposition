#!/bin/bash
# Comprobaciones adicionales sobre el Lean ya compilado. Los resultados quedan en /logs.
set -u
export ELAN_HOME=/vol/elan HOME=/vol/home TMPDIR=/vol/tmp
export PATH="$ELAN_HOME/bin:/vol/tools/go/bin:/vol/tools/bin:$PATH"
cd /vol/repo || exit 1
stamp() { echo "=== $(date -u +%FT%TZ) $*"; }

stamp apt
apt-get update -qq && apt-get install -y -qq --no-install-recommends git curl ca-certificates zstd >/dev/null

stamp leanchecker
timeout 5400 lake env leanchecker --fresh NavierStokes.ComparatorSolution > /logs/leanchecker.log 2>&1
echo "LEANCHECKER_EXIT $?"
tail -5 /logs/leanchecker.log | cut -c1-200

stamp landrun
mkdir -p /vol/tools/bin
if [ ! -x /vol/tools/bin/landrun ]; then
  [ -d /vol/tools/go ] || curl -sSfL https://go.dev/dl/go1.24.9.linux-amd64.tar.gz | tar -xz -C /vol/tools
  GOBIN=/vol/tools/bin go install github.com/zouuup/landrun/cmd/landrun@main > /logs/landrun_build.log 2>&1
  echo "LANDRUN_BUILD_EXIT $?"
fi
landrun --ro / -- /bin/true > /logs/landlock_probe.log 2>&1
PROBE=$?
echo "LANDLOCK_PROBE_EXIT $PROBE"
cut -c1-200 /logs/landlock_probe.log | tail -3

if [ "$PROBE" -eq 0 ]; then
  stamp comparator
  lake build comparator lean4export > /logs/comparator_build.log 2>&1
  echo "COMPARATOR_BUILD_EXIT $?"
  export COMPARATOR_LEAN4EXPORT=/vol/repo/.lake/packages/lean4export/.lake/build/bin/lean4export
  python_config=/tmp/ns.json
  sed 's/"enable_nanoda": true/"enable_nanoda": false/' ComparatorChallenges/NavierStokes.json > "$python_config"
  timeout 3600 lake env .lake/packages/Comparator/.lake/build/bin/comparator "$python_config" > /logs/comparator.log 2>&1
  echo "COMPARATOR_EXIT $?"
  tail -15 /logs/comparator.log | cut -c1-200
else
  echo "COMPARATOR_NOT_RUN: el sandbox landrun no funciona en este entorno"
fi
stamp fin
