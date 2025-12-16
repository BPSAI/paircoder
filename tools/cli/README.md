# bpsai-pair CLI Package

The PairCoder CLI tool for AI pair programming workflows.

See [main README](../../README.md) for full documentation.

## Development

```bash
# Install for development
pip install -e .

# Run tests
pytest -v

# Build
python -m build
```

## Package Structure

```
bpsai_pair/
├── cli.py              # Main CLI entry point
├── ops.py              # Core operations
├── config.py           # Configuration handling
├── planning/           # Plan and task management
├── tasks/              # Lifecycle, archival
├── metrics/            # Token tracking
├── integrations/       # Time tracking (Toggl)
├── benchmarks/         # Benchmark framework
├── orchestration/      # Multi-agent routing
└── data/               # Cookiecutter template
```
