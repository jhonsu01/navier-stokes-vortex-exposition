#!/bin/bash
# Verifica con Comparator el Lean de OpenAI en una maquina Linux limpia.
# Uso, como usuario normal: bash comparator_clean.sh /ruta/en/un/disco/real
# Requiere Ubuntu 24.04 o similar. El resultado queda en <ruta>/resultado.
set -u

COMMIT=f9e8bc5b38b6e212696e8a30e3e91517af887bbd
LANDRUN_COMMIT=ec104f6
WORK="${1:-$HOME/ns-verify}"
OUT="$WORK/resultado"
mkdir -p "$OUT"
exec > >(tee -a "$OUT/run.log") 2>&1

stamp() { echo "=== $(date -u +%FT%TZ) $*"; }
fail() { echo "DETENIDO: $*"; exit 1; }

stamp preflight
[ "$(id -u)" -ne 0 ] || fail "ejecutar como usuario normal, no como root"
uname -a
grep -E 'PRETTY_NAME' /etc/os-release
free -g | sed -n 2p
nproc
FREE_GB=$(df -BG --output=avail "$WORK" | tail -1 | tr -dc '0-9')
echo "Libre en $WORK: ${FREE_GB} GB"
[ "$FREE_GB" -ge 30 ] || fail "hacen falta al menos 30 GB libres en un disco real"
RAM_GB=$(free -g | awk 'NR==2{print $2}')
[ "$RAM_GB" -ge 14 ] || echo "AVISO: menos de 16 GB de RAM; podria quedarse sin memoria"
LSM=$(cat /sys/kernel/security/lsm 2>/dev/null || echo "")
echo "LSM activos: $LSM"
echo "$LSM" | grep -q landlock || fail "Landlock no esta activo en este kernel"

stamp paquetes
sudo apt-get update -qq || fail "apt update"
sudo apt-get install -y -qq git curl ca-certificates zstd build-essential pkg-config || fail "apt install"

export ELAN_HOME="$WORK/elan" CARGO_HOME="$WORK/cargo" RUSTUP_HOME="$WORK/rustup" GOPATH="$WORK/gopath" GOCACHE="$WORK/gocache"
export TMPDIR="$WORK/tmp"
mkdir -p "$TMPDIR" "$WORK/bin"
export PATH="$WORK/bin:$ELAN_HOME/bin:$CARGO_HOME/bin:$WORK/go/bin:$PATH"

stamp landrun
if [ ! -x "$WORK/bin/landrun" ]; then
  [ -d "$WORK/go" ] || curl -sSfL https://go.dev/dl/go1.24.9.linux-amd64.tar.gz | tar -xz -C "$WORK" || fail "descarga de Go"
  [ -d "$WORK/landrun-src" ] || git clone -q https://github.com/Zouuup/landrun.git "$WORK/landrun-src" || fail "clon de landrun"
  (cd "$WORK/landrun-src" && git checkout -q "$LANDRUN_COMMIT" && go build -o "$WORK/bin/landrun" cmd/landrun/main.go) || fail "compilacion de landrun"
fi

stamp prueba_sandbox
# Comparator usa --best-effort, asi que hay que confirmar que el bloqueo es real.
PROBE="$WORK/probe_escritura"
rm -f "$PROBE"
landrun --best-effort --ro / --rw /dev -ldd -add-exec -- /usr/bin/touch "$PROBE"
if [ -e "$PROBE" ]; then
  rm -f "$PROBE"
  fail "el sandbox NO bloqueo la escritura; un resultado aqui no valdria"
fi
echo "SANDBOX_OK: la escritura fuera de lo permitido quedo bloqueada"

stamp nanoda
if [ ! -x "$WORK/nanoda_lib/target/release/nanoda_bin" ]; then
  command -v cargo >/dev/null || curl -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path --profile minimal || fail "rustup"
  [ -d "$WORK/nanoda_lib" ] || git clone -q https://github.com/ammkrn/nanoda_lib.git "$WORK/nanoda_lib" || fail "clon de nanoda"
  (cd "$WORK/nanoda_lib" && cargo build --release) || fail "compilacion de nanoda"
fi
export PATH="$WORK/nanoda_lib/target/release:$PATH"
echo "nanoda $(git -C "$WORK/nanoda_lib" rev-parse HEAD)"

stamp elan
if [ ! -x "$ELAN_HOME/bin/elan" ]; then
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o "$TMPDIR/elan-init.sh" || fail "descarga de elan"
  sh "$TMPDIR/elan-init.sh" -y --no-modify-path --default-toolchain none || fail "instalacion de elan"
fi

stamp repositorio
[ -d "$WORK/repo/.git" ] || git clone -q https://github.com/openai/NavierStokesAndEuler.git "$WORK/repo" || fail "clon del repositorio"
cd "$WORK/repo" || fail "repositorio"
git checkout -q "$COMMIT" || fail "commit"
echo "HEAD $(git rev-parse HEAD)"
sha256sum ComparatorChallenges/NavierStokes.lean ComparatorChallenges/NavierStokes.json NavierStokes/ComparatorSolution.lean | tee "$OUT/hashes.txt"

stamp cache_mathlib
lake exe cache get 2>&1 | tail -3

stamp herramientas
# Solo se compilan las herramientas. La solucion la compila Comparator dentro del sandbox.
lake build comparator lean4export 2>&1 | tail -3
export PATH="$WORK/repo/.lake/packages/lean4export/.lake/build/bin:$PATH"
command -v lean4export >/dev/null || fail "lean4export no esta en PATH"

stamp comparator
COMPARATOR=".lake/packages/Comparator/.lake/build/bin/comparator"
[ -x "$COMPARATOR" ] || COMPARATOR=".lake/build/bin/comparator"
[ -x "$COMPARATOR" ] || fail "no encuentro el binario de comparator"
START=$(date +%s)
systemd-run --property='RestrictAddressFamilies=~AF_UNIX' --user --pty -E PATH="$PATH" -E ELAN_HOME="$ELAN_HOME" -E TMPDIR="$TMPDIR" \
  --working-directory "$PWD" -- bash -c "lake env $COMPARATOR ComparatorChallenges/NavierStokes.json > '$OUT/comparator.log' 2>&1; echo \$? > '$OUT/comparator.exit'"
echo "Duracion: $(( $(date +%s) - START )) s"
stamp fin
echo "COMPARATOR_EXIT $(cat "$OUT/comparator.exit" 2>/dev/null || echo desconocido)"
tail -25 "$OUT/comparator.log" 2>/dev/null
echo "Copia la carpeta $OUT y compartela."
