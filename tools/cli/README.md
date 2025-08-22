# bpsai-pair CLI

The PairCoder CLI tool for AI pair programming workflows.

## Quick Start

### Install from PyPI
```bash
pip install bpsai-pair
bpsai-pair --help
```

### Development Install
```bash
cd tools/cli
pip install -e .
bpsai-pair --help
```

## Usage

### Initialize scaffolding (uses bundled template)
```bash
bpsai-pair-init
# or with main CLI:
bpsai-pair init
```

### Create feature branch
```bash
bpsai-pair feature auth-refactor \
  --type refactor \
  --primary "Decouple auth via DI" \
  --phase "Refactor auth module + tests"
```

### Pack context for AI
```bash
bpsai-pair pack --out agent_pack.tgz
bpsai-pair pack --list  # Preview files
bpsai-pair pack --json  # JSON output
```

### Update context loop
```bash
bpsai-pair context-sync \
  --last "Initialized scaffolding" \
  --next "Set up CI secrets" \
  --blockers "None"
```

## Commands

- `bpsai-pair init` - Initialize repo with PairCoder structure
- `bpsai-pair-init` - Quick init with bundled template (no args)
- `bpsai-pair feature` - Create feature/fix/refactor branch
- `bpsai-pair pack` - Package context for AI agents
- `bpsai-pair context-sync` - Update the Context Loop
- `bpsai-pair status` - Show current state
- `bpsai-pair validate` - Check repo structure
- `bpsai-pair ci` - Run local CI checks

## Development

Run tests:
```bash
pytest
```

Build wheel:
```bash
python -m build
```

## Template

The CLI bundles a cookiecutter template in `bpsai_pair/data/cookiecutter-paircoder/` 
that gets installed with the package and used by `bpsai-pair-init`.
