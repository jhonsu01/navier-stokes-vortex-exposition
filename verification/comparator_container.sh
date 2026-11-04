#!/bin/bash
# Comparator en un volumen nuevo, sin compilar antes la solucion, como usuario sin privilegios.
# Diferencia con el metodo recomendado: en el contenedor no existe systemd-run.
set -u
COMMIT=f9e8bc5b38b6e212696e8a30e3e91517af887bbd
LANDRUN_COMMIT=ec104f6

if [ "$(id -u)" -eq 0 ]; then
  apt-get update -qq && apt-get install -y -qq --no-install-recommends git curl ca-certificates zstd build-essential pkg-config >/dev/null || exit 10
  useradd -m verifier
  chown -R verifier /vol
  chown verifier /logs
  exec su verifier -s /bin/bash -c "bash /comparator.sh"
fi

WORK=/vol
OUT=/logs
export ELAN_HOME=$WORK/elan CARGO_HOME=$WORK/cargo RUSTUP_HOME=$WORK/rustup GOPATH=$WORK/gopath GOCACHE=$WORK/gocache TMPDIR=$WORK/tmp HOME=/home/verifier
mkdir -p "$TMPDIR" "$WORK/bin"
export PATH="$WORK/bin:$ELAN_HOME/bin:$CARGO_HOME/bin:$WORK/go/bin:$PATH"
stamp() { echo "=== $(date -u +%FT%TZ) $*"; }
fail() { echo "DETENIDO: $*"; exit 1; }

stamp identidad
id
uname -r

stamp landrun
curl -sSfL https://go.dev/dl/go1.24.9.linux-amd64.tar.gz | tar -xz -C "$WORK" || fail go
git clone -q https://github.com/Zouuup/landrun.git "$WORK/landrun-src" || fail clon_landrun
(cd "$WORK/landrun-src" && git checkout -q "$LANDRUN_COMMIT" && go build -o "$WORK/bin/landrun" cmd/landrun/main.go) || fail compilar_landrun

stamp prueba_sandbox
PROBE=$WORK/probe_escritura
landrun --best-effort --ro / --rw /dev -ldd -add-exec -- /usr/bin/touch "$PROBE"
echo "touch_exit $?"
if [ -e "$PROBE" ]; then
  rm -f "$PROBE"
  fail "el sandbox NO bloqueo la escritura"
fi
echo "SANDBOX_OK"

stamp nanoda
curl -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path --profile minimal >/dev/null 2>&1 || fail rustup
git clone -q https://github.com/ammkrn/nanoda_lib.git "$WORK/nanoda_lib" || fail clon_nanoda
(cd "$WORK/nanoda_lib" && cargo build --release 2>&1 | tail -2) || fail compilar_nanoda
export PATH="$WORK/nanoda_lib/target/release:$PATH"
command -v nanoda_bin || fail nanoda_bin
echo "nanoda $(git -C "$WORK/nanoda_lib" rev-parse HEAD)"

stamp elan
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o "$TMPDIR/elan-init.sh" || fail elan
sh "$TMPDIR/elan-init.sh" -y --no-modify-path --default-toolchain none || fail elan

stamp repositorio
git clone -q --filter=blob:none https://github.com/openai/NavierStokesAndEuler.git "$WORK/repo" || fail clon_repo
cd "$WORK/repo" || fail repo
git checkout -q "$COMMIT" || fail commit
echo "HEAD $(git rev-parse HEAD)"
sha256sum ComparatorChallenges/NavierStokes.lean ComparatorChallenges/NavierStokes.json NavierStokes/ComparatorSolution.lean

stamp cache
lake exe cache get 2>&1 | tail -2

stamp herramientas
lake build comparator lean4export 2>&1 | tail -3
export PATH="$WORK/repo/.lake/packages/lean4export/.lake/build/bin:$PATH"
command -v lean4export || fail lean4export
COMPARATOR=.lake/packages/Comparator/.lake/build/bin/comparator
[ -x "$COMPARATOR" ] || COMPARATOR=.lake/build/bin/comparator
[ -x "$COMPARATOR" ] || fail binario_comparator
[ ! -e .lake/build/lib/lean/NavierStokes/ComparatorSolution.olean ] && echo "SOLUCION_SIN_COMPILAR_ANTES_DE_COMPARATOR"

stamp comparator
lake env "$COMPARATOR" ComparatorChallenges/NavierStokes.json > "$OUT/comparator.log" 2>&1
CODE=$?
echo "COMPARATOR_EXIT $CODE"
tail -25 "$OUT/comparator.log" | cut -c1-220
stamp fin
exit "$CODE"
