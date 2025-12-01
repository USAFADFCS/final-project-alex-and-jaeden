# FairLLM Sports Edge Analysis - Setup Guide

Complete instructions for cloning and running the multi-agent sports betting edge analysis system.

---

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- Terminal/Command Line access

---

## 🚀 Step 1: Clone the Repository
```bash
# Clone the repository
git clone <your-github-repo-url>

# Navigate into the project
cd fairllm-sports-edge
```

---

## 🔧 Step 2: Create Virtual Environment

### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate
```

### On Windows:
```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

---

## 📦 Step 3: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install rich numpy pytest
```

**Optional:** Install all dependencies from requirements file:
```bash
pip install -r requirements.txt
```

---

## ✅ Step 4: Verify Installation

Test that everything is working:
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from fairllm_agent.agentic_workflow import SportsEdgeFlow

print('✅ Imports working!')
workflow = SportsEdgeFlow()
print('✅ Workflow initialized!')
print('✅ Agents:', [a.name for a in workflow.agents])
