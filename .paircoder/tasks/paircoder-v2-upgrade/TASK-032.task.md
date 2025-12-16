# TASK-032: Benchmarking Framework

## Metadata
- **ID**: TASK-032
- **Plan**: paircoder-v2-upgrade
- **Sprint**: sprint-7
- **Priority**: P2
- **Complexity**: 50
- **Status**: done
- **Created**: 2025-01-16
- **Tags**: benchmarking, metrics, performance, comparison, analytics

## Description

Implement a benchmarking framework to measure and compare AI agent performance across different tasks, models, and configurations. This enables data-driven optimization of agent selection and workflow design.

## Objectives

1. Define benchmark task suite
2. Implement benchmark runner
3. Capture comprehensive metrics
4. Generate comparison reports
5. Support A/B testing of configurations

## Technical Requirements

### Benchmark Task Suite

```yaml
# .paircoder/benchmarks/suite.yaml
benchmarks:
  simple-bug-fix:
    description: "Fix off-by-one error in array loop"
    category: fix
    complexity: low
    setup:
      - copy: fixtures/bug-fix/
    prompt: "Fix the bug in loop.py that causes index out of bounds"
    validation:
      - test: pytest tests/test_loop.py
      - assert: exit_code == 0
    expected_files: [loop.py]
    
  feature-implementation:
    description: "Add pagination to API endpoint"
    category: implement
    complexity: medium
    setup:
      - copy: fixtures/pagination/
    prompt: "Add pagination support to the /users endpoint"
    validation:
      - test: pytest tests/test_pagination.py
      - lint: ruff check src/
    expected_files: [src/api.py, tests/test_pagination.py]
    
  architecture-design:
    description: "Design caching layer"
    category: design
    complexity: high
    setup:
      - copy: fixtures/caching/
    prompt: "Design a caching layer for the database queries"
    validation:
      - exists: design.md
      - contains: design.md "cache invalidation"
    expected_files: [design.md]
```

### Benchmark Runner

```python
class BenchmarkRunner:
    def __init__(self, suite_path: Path, config: BenchmarkConfig):
        self.suite = load_suite(suite_path)
        self.config = config
        
    def run(self, 
            benchmark_ids: List[str],
            agents: List[str],
            iterations: int = 3) -> BenchmarkResults:
        """Run benchmarks across agents with multiple iterations"""
        results = []
        
        for benchmark_id in benchmark_ids:
            for agent in agents:
                for i in range(iterations):
                    result = self._run_single(benchmark_id, agent, i)
                    results.append(result)
                    
        return BenchmarkResults(results)
        
    def _run_single(self, benchmark_id: str, agent: str, iteration: int) -> BenchmarkResult:
        """Run single benchmark iteration"""
        benchmark = self.suite[benchmark_id]
        
        # Setup
        workspace = self._setup_workspace(benchmark)
        
        # Execute
        start = time.time()
        execution = self._execute(agent, benchmark.prompt, workspace)
        duration = time.time() - start
        
        # Validate
        validation = self._validate(benchmark, workspace)
        
        return BenchmarkResult(
            benchmark_id=benchmark_id,
            agent=agent,
            iteration=iteration,
            success=validation.passed,
            duration_seconds=duration,
            tokens=execution.tokens,
            cost_usd=execution.cost,
            validation_details=validation,
            files_modified=execution.files_modified
        )
```

### Metrics Captured

```python
@dataclass
class BenchmarkResult:
    # Identification
    benchmark_id: str
    agent: str
    model: str
    iteration: int
    timestamp: datetime
    
    # Outcome
    success: bool
    validation_passed: List[str]
    validation_failed: List[str]
    
    # Performance
    duration_seconds: float
    tokens_input: int
    tokens_output: int
    cost_usd: float
    
    # Quality
    files_modified: List[str]
    lines_added: int
    lines_removed: int
    test_coverage_delta: float  # Optional
    
    # Agent behavior
    tool_calls: int
    iterations: int  # Back-and-forth cycles
    errors_recovered: int
```

### CLI Commands

```bash
# Run full benchmark suite
bpsai-pair benchmark run --suite default

# Run specific benchmarks
bpsai-pair benchmark run --only simple-bug-fix,feature-implementation

# Run with specific agents
bpsai-pair benchmark run --agents claude-code,codex-cli

# Run with iterations for statistical significance
bpsai-pair benchmark run --iterations 5

# View results
bpsai-pair benchmark results --latest
bpsai-pair benchmark results --id bench-2025-01-16-001

# Compare agents
bpsai-pair benchmark compare --baseline claude-code --challenger codex-cli

# Export results
bpsai-pair benchmark export --format csv --output results.csv
```

### Results Storage

```
.paircoder/history/benchmarks/
├── bench-2025-01-16-001/
│   ├── config.yaml          # Run configuration
│   ├── results.jsonl        # Raw results
│   ├── summary.json         # Aggregated stats
│   └── logs/                # Execution logs
│       ├── simple-bug-fix-claude-code-0.log
│       └── ...
└── index.json               # All benchmark runs
```

### Comparison Report

```markdown
# Benchmark Comparison Report
Generated: 2025-01-16T15:00:00Z

## Summary

| Metric | claude-code | codex-cli | Winner |
|--------|-------------|-----------|--------|
| Success Rate | 92% | 85% | claude-code |
| Avg Duration | 45s | 32s | codex-cli |
| Avg Cost | $0.08 | $0.05 | codex-cli |
| Avg Tokens | 2,300 | 1,800 | codex-cli |

## By Category

### Bug Fixes
| Agent | Success | Duration | Cost |
|-------|---------|----------|------|
| claude-code | 100% | 28s | $0.04 |
| codex-cli | 95% | 22s | $0.03 |

### Feature Implementation
| Agent | Success | Duration | Cost |
|-------|---------|----------|------|
| claude-code | 90% | 65s | $0.12 |
| codex-cli | 75% | 45s | $0.07 |

## Recommendations

Based on results:
- Use **codex-cli** for simple bug fixes (faster, cheaper)
- Use **claude-code** for feature implementation (higher success)
```

## Acceptance Criteria

- [ ] Benchmark suite YAML format defined
- [ ] At least 5 benchmark tasks created
- [ ] Runner executes benchmarks correctly
- [ ] Validation checks pass/fail accurately
- [ ] All metrics captured per spec
- [ ] Results stored in structured format
- [ ] Comparison reports generated
- [ ] CLI commands work as documented
- [ ] Unit tests for runner and validation
- [ ] Integration test with real agents (manual)

## Dependencies

- TASK-025 (headless mode for execution)
- TASK-027 (Codex adapter)
- TASK-030 (metrics collection)
- Git for workspace isolation

## Files to Create/Modify

- `tools/cli/src/paircoder/benchmarks/__init__.py`
- `tools/cli/src/paircoder/benchmarks/runner.py`
- `tools/cli/src/paircoder/benchmarks/validation.py`
- `tools/cli/src/paircoder/benchmarks/reports.py`
- `tools/cli/src/paircoder/commands/benchmark.py`
- `.paircoder/benchmarks/suite.yaml`
- `.paircoder/benchmarks/fixtures/` (benchmark fixtures)
- `tools/cli/tests/test_benchmarks.py`

## Notes

- Benchmarks must be deterministic where possible
- Use git worktrees for isolated workspaces
- Consider: Caching setup for faster iterations
- Statistical significance requires 3+ iterations
- Results are for internal optimization, not public claims

## Future Enhancements

- Custom benchmark creation wizard
- Automated regression detection
- Performance trending over time
- Integration with SWE-bench style evaluations
- Cost-efficiency scoring

## Example Output

```bash
$ bpsai-pair benchmark run --only simple-bug-fix --agents claude-code,codex-cli --iterations 3

Running benchmarks...

simple-bug-fix:
  claude-code: ✓✓✓ (3/3, avg 28s, $0.04)
  codex-cli:   ✓✓✗ (2/3, avg 22s, $0.03)

Summary:
  Total: 6 runs
  Passed: 5 (83%)
  Duration: 2m 34s
  Cost: $0.21

Results saved: .paircoder/history/benchmarks/bench-2025-01-16-001/
```
