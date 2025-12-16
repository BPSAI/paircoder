# TASK-030: Token Tracking and Cost Estimation

## Metadata
- **ID**: TASK-030
- **Plan**: paircoder-v2-upgrade
- **Sprint**: sprint-7
- **Priority**: P1
- **Complexity**: 45
- **Status**: pending
- **Created**: 2025-01-16
- **Tags**: metrics, tokens, cost, tracking, analytics

## Description

Implement token tracking and cost estimation to provide visibility into AI agent usage. This enables budget management, cost optimization, and ROI analysis.

## Objectives

1. Capture token usage from all agent invocations
2. Calculate costs based on model pricing
3. Store metrics in persistent log
4. Provide reporting and analytics
5. Support budget alerts and limits

## Technical Requirements

### Metrics Schema

```json
{
  "timestamp": "2025-01-16T10:30:00Z",
  "session_id": "abc123",
  "task_id": "TASK-025",
  "agent": "claude-code",
  "model": "claude-sonnet-4-5-20250929",
  "operation": "invoke",
  "tokens": {
    "input": 1500,
    "output": 800,
    "total": 2300
  },
  "cost_usd": 0.0345,
  "duration_ms": 4500,
  "success": true,
  "error": null
}
```

### Metrics Storage

```
.paircoder/history/
├── metrics.jsonl           # Append-only log (JSON Lines)
├── metrics-2025-01.jsonl   # Monthly rollover
└── summary.json            # Aggregated stats (updated hourly)
```

### Pricing Configuration

```yaml
# .paircoder/config.yaml
pricing:
  claude-code:
    claude-sonnet-4-5-20250929:
      input_per_1m: 3.00
      output_per_1m: 15.00
    claude-opus-4-5-20251101:
      input_per_1m: 15.00
      output_per_1m: 75.00
  codex-cli:
    default:
      input_per_1m: 2.50
      output_per_1m: 10.00
  budget:
    daily_limit_usd: 10.00
    monthly_limit_usd: 200.00
    alert_threshold: 0.8  # Alert at 80% of limit
```

### Metrics Collector

```python
class MetricsCollector:
    def __init__(self, log_path: Path, config: PricingConfig):
        self.log_path = log_path
        self.config = config
        
    def record(self, event: MetricsEvent) -> None:
        """Append event to metrics log"""
        
    def calculate_cost(self, agent: str, model: str, 
                       input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on pricing config"""
        
    def check_budget(self) -> BudgetStatus:
        """Check current spend against limits"""
```

### CLI Commands

```bash
# Show current session usage
bpsai-pair metrics session

# Show task-level metrics
bpsai-pair metrics task TASK-025

# Show daily/weekly/monthly summary
bpsai-pair metrics summary --period daily
bpsai-pair metrics summary --period weekly
bpsai-pair metrics summary --period monthly

# Show cost breakdown by agent
bpsai-pair metrics breakdown --by agent
bpsai-pair metrics breakdown --by task
bpsai-pair metrics breakdown --by model

# Export metrics
bpsai-pair metrics export --format csv --output usage.csv

# Check budget status
bpsai-pair metrics budget
```

### Integration Points

1. **Headless Session** (TASK-025)
   - Capture tokens from JSON response
   - Log after each invocation

2. **Orchestrator** (TASK-028)
   - Factor cost into agent selection
   - Enforce budget limits

3. **Handoff** (TASK-026)
   - Include cumulative cost in handoff metadata

### Budget Enforcement

```python
class BudgetEnforcer:
    def __init__(self, config: BudgetConfig, collector: MetricsCollector):
        self.config = config
        self.collector = collector
        
    def can_proceed(self, estimated_cost: float) -> tuple[bool, str]:
        """Check if operation within budget"""
        status = self.collector.check_budget()
        
        if status.daily_remaining < estimated_cost:
            return False, f"Would exceed daily limit (${status.daily_remaining:.2f} remaining)"
            
        if status.daily_spent / status.daily_limit > self.config.alert_threshold:
            logger.warning(f"Approaching daily limit: ${status.daily_spent:.2f}/${status.daily_limit:.2f}")
            
        return True, "OK"
```

## Acceptance Criteria

- [ ] Token usage captured from Claude Code headless responses
- [ ] Costs calculated accurately per model pricing
- [ ] Metrics appended to JSONL log
- [ ] Summary aggregations computed correctly
- [ ] CLI commands display metrics clearly
- [ ] Budget limits enforced (optional bypass with --force)
- [ ] Alert threshold triggers warnings
- [ ] Monthly log rollover works
- [ ] Export to CSV works
- [ ] Unit tests for cost calculation
- [ ] Integration test for full tracking flow

## Dependencies

- TASK-025 (headless mode provides token data)
- TASK-027 (Codex adapter for Codex metrics)

## Files to Create/Modify

- `tools/cli/src/paircoder/metrics/__init__.py`
- `tools/cli/src/paircoder/metrics/collector.py`
- `tools/cli/src/paircoder/metrics/budget.py`
- `tools/cli/src/paircoder/metrics/reports.py`
- `tools/cli/src/paircoder/commands/metrics.py`
- `tools/cli/tests/test_metrics.py`
- `.paircoder/config.yaml` (add pricing section)

## Notes

- Use JSONL for append-only performance
- Don't block on metrics failures (fire and forget)
- Consider privacy: no prompts in metrics log
- Pricing will change - make config easy to update
- Consider: dashboard/visualization (future)

## Example Output

```bash
$ bpsai-pair metrics summary --period weekly

Weekly Usage Summary (Jan 10 - Jan 16, 2025)
============================================

Total Tokens:     45,230 (38,400 input / 6,830 output)
Total Cost:       $1.87
Total Operations: 23

By Agent:
  claude-code:    $1.52 (81%)
  codex-cli:      $0.35 (19%)

By Task:
  TASK-025:       $0.78 (42%)
  TASK-026:       $0.61 (33%)
  TASK-027:       $0.48 (25%)

Budget Status:
  Daily:          $1.87 / $10.00 (18.7%)
  Monthly:        $12.45 / $200.00 (6.2%)
```
