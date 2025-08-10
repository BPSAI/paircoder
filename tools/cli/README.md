
# bpsai-pair CLI

## Quick start (local, un-packaged)
```
python -m tools.cli.bpsai_pair --help
python -m tools.cli.bpsai_pair init tools/cookiecutter-paircoder
python -m tools.cli.bpsai_pair feature auth-di --primary "Decouple auth via DI" --phase "Refactor auth + tests"
python -m tools.cli.bpsai_pair pack --extra README.md
python -m tools.cli.bpsai_pair context-sync --last "initialized scaffolding" --nxt "set up CI secrets" --blockers "none"
```

## Install as a CLI
```
cd tools/cli
pip install -e .
# now available as: bpsai-pair --help
```
