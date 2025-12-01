# 🚀 Quick Run Guide

**How to run the FairLLM Sports Edge Analysis system**

---

## ⚡ Prerequisites

Make sure you've done the initial setup:
```bash
# 1. Navigate to project
cd fairllm-sports-edge

# 2. Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies (if not done already)
pip install -r requirements.txt
```

You should see `(.venv)` in your terminal prompt.

---

## 🎮 Option 1: Run the Demo (Recommended First)

**What it does:** Shows 3 pre-built demonstrations of the multi-agent system
```bash
python3 demo.py
```

### What you'll see:

**Demo 1:** Single game analysis (Lakers vs Celtics)
- Shows all 4 agents working together
- Calculates fair probabilities
- Computes betting edge
- Makes recommendation

**Demo 2:** Batch processing (5 games)
- Analyzes NBA, NFL, and NHL games
- Shows summary of all recommendations
- Displays top opportunities

**Demo 3:** Agent-by-agent breakdown
- Step through each agent's analysis
- See how data flows through the pipeline

### Controls:
- **Press Enter** to move between demos
- **Press Ctrl+C** to exit anytime

---

## 💬 Option 2: Interactive Analysis (Custom Input)

**What it does:** Let you enter your own odds and predictions
```bash
python3 interactive_analysis.py
```

### You'll be prompted for:

1. **Game Information:**
   - Event ID (e.g., `2025-12-01-NBA-001`)
   - Sport (default: `basketball`)
   - League (default: `NBA`)
   - Home Team (e.g., `Warriors`)
   - Away Team (e.g., `Lakers`)
   - Sportsbook (default: `DraftKings`)

2. **Odds (American format):**
   - Home team odds (e.g., `-140` for favorite)
   - Away team odds (e.g., `+120` for underdog)

3. **Your Prediction:**
   - Home team win probability (e.g., `0.65` for 65%)
   - Away probability is auto-calculated

### Example Session:
```
Event ID: 2025-12-01-NBA-001
Sport [basketball]: basketball
League [NBA]: NBA
Home Team: Warriors
Away Team: Lakers
Sportsbook [DraftKings]: DraftKings

Warriors odds: -140
Lakers odds: +120

Home team win probability: 0.65

[System shows full analysis with recommendation]

Analyze another game? [y/n]: y
```

### Understanding Odds:

**Negative numbers** = Favorite
- `-140` means bet $140 to win $100
- Higher negative = bigger favorite

**Positive numbers** = Underdog
- `+120` means bet $100 to win $120
- Higher positive = bigger underdog

### Controls:
- **Enter `y`** to analyze another game
- **Enter `n`** or **Ctrl+C** to exit

---

## 🧪 Option 3: Quick Test

**What it does:** Quick verification that everything works
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from fairllm_agent.agentic_workflow import SportsEdgeFlow

print('Testing system...')
workflow = SportsEdgeFlow()
print('✅ System initialized!')
print('✅ Agents:', [a.name for a in workflow.agents])
