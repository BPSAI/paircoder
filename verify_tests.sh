#!/usr/bin/env bash
# verify_tests.sh - Verify all PairCoder tests pass
set -e

echo "🧪 Verifying PairCoder test suite..."
echo "=================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Activate venv if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the fixes first
echo -e "\n${YELLOW}Applying test fixes...${NC}"
if [ -f "fix_remaining_tests.py" ]; then
    python3 fix_remaining_tests.py
else
    echo -e "${YELLOW}Fix script not found, skipping...${NC}"
fi

# Change to CLI directory
cd tools/cli

# Run tests with coverage
echo -e "\n${YELLOW}Running test suite with coverage...${NC}"
python -m pytest tests/ -v --tb=short --cov=bpsai_pair --cov-report=term-missing

# Check the exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"

    # Show summary
    echo -e "\n${YELLOW}Test Summary:${NC}"
    python -m pytest tests/ --co -q | grep -E "test_" | wc -l | xargs -I {} echo "  Total tests: {}"

    # Check if CLI works
    echo -e "\n${YELLOW}Verifying CLI entry point...${NC}"
    if bpsai-pair --version > /dev/null 2>&1; then
        echo -e "${GREEN}✓ CLI entry point works${NC}"
        bpsai-pair --version
    else
        echo -e "${YELLOW}⚠ Using module invocation${NC}"
        python -m bpsai_pair.cli --version
    fi

    echo -e "\n${GREEN}🎉 PairCoder test suite is fully functional!${NC}"
else
    echo -e "\n${RED}❌ Some tests failed. Please review the output above.${NC}"
    exit 1
fi

# Final instructions
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Create a feature branch:"
echo "   bpsai-pair feature test-fixes --type fix --primary 'Fixed test suite' --phase 'Tests passing'"
echo ""
echo "2. Update context:"
echo "   bpsai-pair context-sync --last 'Fixed all test failures' --next 'Commit and push fixes' --blockers 'None'"
echo ""
echo "3. Create a pack for agent:"
echo "   bpsai-pair pack --out test-fixes.tgz"
