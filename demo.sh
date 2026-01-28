#!/bin/bash
# Demo: Git-First Test Case Management PoC
# This script demonstrates the complete workflow

set -e

echo "=================================================="
echo "Git-First Test Case Management - PoC Demo"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Show system info
echo -e "${BLUE}Step 1: System Information${NC}"
python scripts/tcm.py info
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 2: Validate example test case
echo -e "${BLUE}Step 2: Validate Example Test Case${NC}"
python scripts/validate_yaml.py --input-dir test-cases/examples
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 3: Show Git workflow
echo -e "${BLUE}Step 3: Git Workflow Demo${NC}"
echo ""

# Create a feature branch
echo -e "${YELLOW}Creating feature branch...${NC}"
git checkout -b demo-improvements
echo ""

# Show the example test case
echo -e "${YELLOW}Current test case (showing first 30 lines):${NC}"
head -n 30 test-cases/examples/TC00001-remote-engine-start-happy-path.yml
echo ""
echo "... (truncated)"
echo ""
read -p "Press Enter to continue..."
echo ""

# Add a new step
echo -e "${YELLOW}Adding a new edge case step...${NC}"
cat >> test-cases/examples/TC00001-remote-engine-start-happy-path.yml << 'EOF'

  - id: 6
    action: "Simulate network timeout during remote start request"
    expected: "Error message displayed: 'Connection timeout. Please check your connection and try again.'"
    timeout: 10s
EOF

echo -e "${GREEN}✓ Added step 6: Network timeout edge case${NC}"
echo ""

# Show the diff
echo -e "${YELLOW}Git diff:${NC}"
git diff test-cases/examples/TC00001-remote-engine-start-happy-path.yml
echo ""
read -p "Press Enter to continue..."
echo ""

# Validate the changes
echo -e "${BLUE}Step 4: Validate Changes${NC}"
python scripts/validate_yaml.py --input-dir test-cases/examples
echo ""
read -p "Press Enter to continue..."
echo ""

# Commit the changes
echo -e "${BLUE}Step 5: Commit Changes${NC}"
git add test-cases/
git commit -m "Add network timeout edge case to remote start test"
echo ""
echo -e "${GREEN}✓ Changes committed${NC}"
echo ""

# Show git log
echo -e "${YELLOW}Git log:${NC}"
git log --oneline --graph --all
echo ""
read -p "Press Enter to continue..."
echo ""

# Show what would happen in PR
echo -e "${BLUE}Step 6: Pull Request Workflow${NC}"
echo ""
echo "In a real workflow, you would now:"
echo "  1. Push to remote: ${YELLOW}git push origin demo-improvements${NC}"
echo "  2. Create Pull Request on GitHub"
echo "  3. Request review from team lead"
echo "  4. After approval and merge → GitHub Actions syncs to Testmo"
echo ""
echo -e "${GREEN}✓ Complete Git workflow demonstrated${NC}"
echo ""
read -p "Press Enter to continue..."
echo ""

# Clean up - go back to main
echo -e "${BLUE}Step 7: Cleanup${NC}"
git checkout main
git branch -D demo-improvements
echo ""
echo -e "${GREEN}✓ Demo branch deleted${NC}"
echo ""

# Summary
echo "=================================================="
echo -e "${GREEN}Demo Complete!${NC}"
echo "=================================================="
echo ""
echo "What we demonstrated:"
echo "  ✓ YAML validation"
echo "  ✓ Git branching workflow"
echo "  ✓ Adding test case improvements"
echo "  ✓ Commit and review process"
echo ""
echo "Next steps for production:"
echo "  1. Export real test cases from Testmo"
echo "  2. Setup GitHub repository with Actions"
echo "  3. Configure team access"
echo "  4. Create Claude Projects for AI assistance"
echo ""
echo "Documentation:"
echo "  - README.md - System overview"
echo "  - docs/TEAM_WORKFLOW.md - Team guide"
echo "  - docs/schema.md - YAML format reference"
echo ""
