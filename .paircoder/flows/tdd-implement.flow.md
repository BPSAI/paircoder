---
name: tdd-implement
version: 1
description: >
  Test-Driven Development implementation flow. Write failing tests first,
  then minimal code to pass, then refactor.
when_to_use:
  - Implementing a planned task
  - Fixing a bug
  - Adding a new function or feature
  - Any code change that should have tests
roles:
  driver:
    primary: true
    description: Writes tests and implementation code
  navigator:
    description: Can assist with test design and edge cases
triggers:
  - bugfix
  - implement_task
  - code_change
requires:
  tools:
    - test_runner
  context:
    - .paircoder/context/state.md
tags:
  - tdd
  - implementation
  - testing
  - driver
---

# TDD Implementation Flow

## Preconditions

Before starting this flow:

- [ ] You have a clear task/goal (from a plan or explicit request)
- [ ] Tests can be run locally
- [ ] You understand the acceptance criteria

---

## The TDD Cycle

```
┌─────────────────────────────────────┐
│                                     │
│   ┌─────┐    ┌─────┐    ┌────────┐ │
│   │ RED │ -> │GREEN│ -> │REFACTOR│ │
│   └─────┘    └─────┘    └────────┘ │
│       ^                      │      │
│       └──────────────────────┘      │
│                                     │
└─────────────────────────────────────┘
```

Repeat this cycle for each piece of functionality.

---

## Phase 1 — Red (Write Failing Test)

### Step 1.1: Identify What to Test

Based on the task, identify:
- The function/method/behavior to implement
- Expected inputs and outputs
- Edge cases and error conditions

### Step 1.2: Write the Test

```python
def test_<what_it_does>():
    # Arrange
    <setup test data>
    
    # Act
    result = <call the function>
    
    # Assert
    assert result == <expected>
```

### Step 1.3: Run and Confirm Failure

```bash
pytest tests/test_<module>.py::<test_name> -v
```

The test MUST fail. If it passes, either:
- The functionality already exists (no work needed)
- The test is wrong (fix the test)

**Gate:** Test fails with expected error before proceeding.

---

## Phase 2 — Green (Make Test Pass)

### Step 2.1: Write Minimal Code

Write the **simplest possible code** that makes the test pass:
- Don't optimize yet
- Don't handle cases not covered by tests
- Don't add features "while you're in there"

### Step 2.2: Run Test

```bash
pytest tests/test_<module>.py::<test_name> -v
```

### Step 2.3: Iterate Until Green

If test still fails:
- Read the error message carefully
- Adjust implementation
- Run again

**Gate:** Test passes before proceeding to refactor.

---

## Phase 3 — Refactor (Improve Code)

### Step 3.1: Review the Code

Now that tests pass, consider:
- Is the code readable?
- Are there duplicate patterns to extract?
- Are variable/function names clear?
- Is there unnecessary complexity?

### Step 3.2: Refactor Safely

Make improvements while keeping tests green:
- Extract methods/functions
- Rename for clarity
- Remove duplication
- Simplify logic

### Step 3.3: Verify Tests Still Pass

```bash
pytest tests/test_<module>.py -v
```

**Gate:** All tests still pass after refactoring.

---

## Phase 4 — Expand Coverage

### Step 4.1: Add Edge Case Tests

Consider:
- Empty inputs
- Boundary values
- Invalid inputs
- Error conditions
- Concurrent access (if applicable)

### Step 4.2: Repeat TDD Cycle

For each new test:
1. Write failing test (Red)
2. Make it pass (Green)
3. Refactor if needed

---

## Phase 5 — Verify and Complete

### Step 5.1: Run Full Test Suite

```bash
pytest -v
```

Ensure no regressions.

### Step 5.2: Check Coverage (Optional)

```bash
pytest --cov=<module> --cov-report=term-missing
```

### Step 5.3: Update State

Update `.paircoder/context/state.md`:
- Mark task as `done`
- Note what was implemented

### Step 5.4: Commit

```bash
git add .
git commit -m "<type>(<scope>): <description>"
```

---

## Quick Reference

### Test Structure

```python
def test_<function>_<scenario>_<expected_result>():
    # Arrange - Set up test data
    input_data = ...
    
    # Act - Call the function
    result = function_under_test(input_data)
    
    # Assert - Check the result
    assert result == expected_value
```

### Common Test Patterns

| Pattern | Use When |
|---------|----------|
| `test_X_returns_Y` | Testing return values |
| `test_X_raises_Y` | Testing exceptions |
| `test_X_with_empty_input` | Edge case: empty |
| `test_X_with_invalid_Y` | Error handling |
| `test_X_calls_Y` | Testing interactions |

### Commit Message Format

```
<type>(<scope>): <description>

Types: feat, fix, refactor, test, docs, chore
```

---

## Completion Checklist

- [ ] Failing test written first
- [ ] Minimal code makes test pass
- [ ] Code refactored for clarity
- [ ] Edge cases covered
- [ ] Full test suite passes
- [ ] State updated
- [ ] Changes committed
