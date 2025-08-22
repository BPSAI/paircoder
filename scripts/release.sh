#!/usr/bin/env bash
set -euo pipefail
usage(){ echo "Usage: scripts/release.sh --version X.Y.Z [--repo testpypi|pypi]"; }
VER=""; REPO="pypi"
while (($#)); do
  case "$1" in
    --version) VER="$2"; shift 2;;
    --repo) REPO="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg $1"; usage; exit 1;;
  esac
done
[ -n "$VER" ] || { usage; exit 1; }

sed -i "s/^version = \".*\"/version = \"$VER\"/" tools/cli/pyproject.toml
python -m pip install --upgrade pip build twine
rm -rf tools/cli/dist
python -m build tools/cli
twine check tools/cli/dist/*
if [ "$REPO" = "testpypi" ]; then
  [ -n "${TWINE_USERNAME:-}" ] && [ -n "${TWINE_PASSWORD:-}" ] || { echo "Set TWINE creds"; exit 1; }
  export TWINE_REPOSITORY_URL="https://test.pypi.org/legacy/"
fi
twine upload tools/cli/dist/*
(git checkout -b "release/v$VER" || git checkout "release/v$VER") || true
git add -A && git commit -m "chore(release): $VER" || true
git tag -a "v$VER" -m "PairCoder CLI $VER" || true
echo "Push: git push origin release/v$VER --tags"
