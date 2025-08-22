#!/usr/bin/env bash
# setup_test_env.sh - Setup and verify PairCoder test environment
set -e

echo "🔧 Setting up PairCoder test environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.9"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo -e "${GREEN}✓ Python $python_version meets minimum requirement ($required_version)${NC}"
else
    echo -e "${RED}✗ Python $python_version is below minimum requirement ($required_version)${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --quiet --upgrade pip
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install package in editable mode
echo -e "\n${YELLOW}Installing bpsai-pair in editable mode...${NC}"
pip install -e tools/cli
echo -e "${GREEN}✓ Package installed${NC}"

# Install test dependencies
echo -e "\n${YELLOW}Installing test dependencies...${NC}"
pip install pytest pytest-cov pytest-mock
echo -e "${GREEN}✓ Test dependencies installed${NC}"

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
if python -c "import bpsai_pair" 2>/dev/null; then
    echo -e "${GREEN}✓ bpsai_pair module can be imported${NC}"
else
    echo -e "${RED}✗ Failed to import bpsai_pair module${NC}"
    exit 1
fi

# Run basic import tests
echo -e "\n${YELLOW}Running import tests...${NC}"
python3 << 'EOF'
import sys
try:
    from bpsai_pair import cli
    from bpsai_pair import ops
    from bpsai_pair import config
    from bpsai_pair import utils
    print("✓ All core modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
EOF

# Create a simple test to verify the CLI works
echo -e "\n${YELLOW}Testing CLI entry point...${NC}"
if bpsai-pair --help > /dev/null 2>&1; then
    echo -e "${GREEN}✓ CLI entry point works${NC}"
else
    echo -e "${YELLOW}⚠ CLI entry point not found, using module invocation${NC}"
fi

# Run the actual tests
echo -e "\n${YELLOW}Running test suite...${NC}"
cd tools/cli
python -m pytest tests/ -v --tb=short

echo -e "\n${GREEN}✅ Test environment setup complete!${NC}"
echo -e "\nYou can now run tests with:"
echo -e "  ${YELLOW}cd tools/cli && python -m pytest tests/ -v${NC}"
echo -e "\nOr run specific tests:"
echo -e "  ${YELLOW}python -m pytest tests/test_cli.py -v${NC}"
