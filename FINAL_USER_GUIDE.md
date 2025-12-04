# 🎯 Sports Edge Analysis System - FINAL USER GUIDE

## Complete Setup and Usage Instructions

**Project:** Agentic Sports Betting Analysis System  
**Authors:** Alex & Jaeden  
**GitHub:** https://github.com/USAFADFCS/final-project-alex-and-jaeden

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Running the System](#running-the-system)
   - [Option 1: Command Line Interface](#option-1-command-line-interface)
   - [Option 2: Desktop GUI](#option-2-desktop-gui)
   - [Option 3: Web Browser Interface](#option-3-web-browser-interface)
4. [How to Use Each Interface](#how-to-use-each-interface)
5. [Understanding the Output](#understanding-the-output)
6. [Troubleshooting](#troubleshooting)
7. [Advanced: LLM Mode](#advanced-llm-mode)

---

## 🖥️ System Requirements

### Minimum Requirements (Rule-Based Mode):
- **OS:** macOS, Linux, or Windows
- **Python:** 3.8 or higher
- **RAM:** 2GB available
- **Disk Space:** 500MB
- **Internet:** For initial setup only

### Recommended Requirements (LLM Mode):
- **OS:** macOS, Linux, or Windows
- **Python:** 3.10 or higher
- **RAM:** 16GB available (8GB minimum)
- **Disk Space:** 10GB (for Phi-3-mini model)
- **GPU:** Optional but speeds up LLM inference


### DOWNLOAD ALL REQUIREMENTS

pip install -r requirements.txt --break-system-packages
---

## 📥 Installation

### Step 1: Get the Code

```bash
# Clone the repository
git clone https://github.com/USAFADFCS/final-project-alex-and-jaeden.git
cd final-project-alex-and-jaeden-1/fairllm-sports-edge
```

**OR** if you already have the files:

```bash
cd ~/Downloads/final-project-alex-and-jaeden-1/fairllm-sports-edge
```

### Step 2: Verify Python Version

```bash
python3 --version
# Should show Python 3.8 or higher
```

### Step 3: Install Dependencies

#### Option A: Using pip (Recommended)

```bash
# Install core dependencies (fast, works immediately)
pip install numpy rich flask --break-system-packages

# Optional: Install LLM dependencies (slower, enables Phi-3-mini explanations)
pip install transformers torch accelerate --break-system-packages
```

#### Option B: Using requirements.txt

```bash
# Install all dependencies at once
pip install -r requirements.txt --break-system-packages
```

**Note:** On macOS, you may need to add `--break-system-packages` flag.  
On other systems, you can usually omit this flag.

### Step 4: Verify Installation

```bash
# Quick test
python3 -c "import numpy, rich, flask; print('✓ Core dependencies installed!')"

# Check if LLM dependencies are available (optional)
python3 -c "import transformers, torch; print('✓ LLM dependencies installed!')" 2>/dev/null || echo "LLM dependencies not installed (optional)"
```

---

## 🚀 Running the System

The system has **three interfaces**. Choose the one that fits your needs:

| Interface | Best For | Speed | Command |
|-----------|----------|-------|---------|
| Command Line | Quick testing, developers | Fastest | `python3 demo.py` |
| Desktop GUI | Casual use, visual interface | Fast | `python3 chatbot_gui.py` |
| Web Browser | Presentations, modern UI | Fast | `python3 web_server.py` |

---

## 🖥️ Option 1: Command Line Interface

### Starting the CLI:

```bash
python3 demo.py
```

### What You'll See:

```
Sports Edge Analysis System
===========================
Loaded 4 agents successfully!

Available demo games:
1. Lakers vs Celtics (NBA) - Lakers -140, Celtics +120
2. Chiefs vs Bills (NFL) - Chiefs -200, Bills +170
3. Bruins vs Rangers (NHL) - Bruins +105, Rangers -125
...

Select a game number (1-10) or type 'quit' to exit:
```

### How to Use:

1. **Select a pre-loaded game:**
   ```
   Select: 1 [Enter]
   ```

2. **Enter your prediction:**
   ```
   What is your predicted win probability for Lakers? (0-100): 62
   ```

3. **View results:**
   - Fair odds (vig removed)
   - Your prediction
   - Betting edge calculation
   - Recommendation (BET or NO BET)

4. **Analyze another game:**
   - Select another number
   - Or type `quit` to exit

### Example Session:

```
Select: 1
What is your predicted win probability for Lakers? 62

================== ANALYSIS REPORT ==================

Fair Odds (Vig Removed):
  Lakers: 56.2%
  Celtics: 43.8%

Your Model Prediction:
  Lakers: 62.0%
  Celtics: 38.0%

Betting Edge:
  Lakers: +5.8% ✓
  Celtics: -5.8%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDATION: BET LAKERS
Edge: 5.8% (MEDIUM-HIGH confidence)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🖼️ Option 2: Desktop GUI

### Starting the GUI:

```bash
python3 chatbot_gui.py
```

### What You'll See:

A window will open with:
- **Blue header** with "Sports Edge Chat" title
- **Chat area** showing welcome messages
- **Example buttons** with pre-filled game scenarios
- **Input field** at the bottom
- **Send button** on the right

### How to Use:

#### Method 1: Click an Example

1. Click one of the example buttons like:
   ```
   [Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%]
   ```

2. The example auto-fills the input field

3. Click **Send** or press **Enter**

4. Wait 1-2 seconds for analysis

5. Results appear as chat bubbles:
   - Gray bubbles: Analysis data
   - Green bubble: Recommendation

#### Method 2: Type Your Own

1. Click in the input field

2. Type your game info:
   ```
   Warriors vs Suns, Warriors -150, Suns +130, Warriors 55%
   ```

3. Format: `Team1 vs Team2, Team1 Odds, Team2 Odds, Prediction%`

4. Click **Send** or press **Enter**

#### Method 3: Demo Button

1. Click the **Demo** button in the top-right

2. Automatically runs Lakers vs Celtics example

### GUI Features:

- ✅ **Clickable examples** - Zero typing errors
- ✅ **Color-coded results** - Easy to scan
- ✅ **Smooth animations** - Professional feel
- ✅ **Status bar** - Shows when agents are working
- ✅ **Scroll automatically** - Always shows latest results

---

## 🌐 Option 3: Web Browser Interface

### Starting the Web Server:

```bash
python3 web_server.py
```

### What You'll See (in terminal):

```
============================================================
🚀 Sports Edge Chat - Web Version
============================================================

Open your browser and go to:
👉 http://localhost:5001

Press Ctrl+C to stop the server
============================================================

Loading AI agents...
✓ Loaded 4 AI agents
 * Serving Flask app 'web_server'
 * Debug mode: on
```

### Opening in Browser:

1. **Automatically:** Some systems open the browser automatically

2. **Manually:** Open any browser and go to:
   ```
   http://localhost:5001
   ```

3. **Bookmark it:** You can bookmark for easy access while server is running

### How to Use:

The web interface works just like the Desktop GUI:

1. **Click example buttons** - Pre-filled scenarios
2. **Type your own** - Custom game analysis
3. **Click Demo** - Quick test with Lakers example

### Web Interface Features:

- ✅ **Modern gradient design** - Professional appearance
- ✅ **Responsive layout** - Works on any screen size
- ✅ **Smooth animations** - Messages slide in nicely
- ✅ **Mobile-friendly** - Can use on phone/tablet (if on same network)
- ✅ **No installation needed** - Just a browser

### Stopping the Server:

Press **Ctrl+C** in the terminal where it's running.

---

## 📊 How to Use Each Interface

### General Input Format:

All three interfaces accept the same format:

```
Team1 vs Team2, Team1 Odds, Team2 Odds, Your Prediction%
```

### Examples:

✅ **Full format:**
```
Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%
```

✅ **Short format:**
```
Warriors -150, Suns +130, Warriors 55%
```

✅ **With "vs":**
```
Chiefs vs Bills, -200, +170, 58%
```

### Understanding Odds:

- **Negative odds (-140):** Favorite. You risk $140 to win $100
- **Positive odds (+120):** Underdog. You risk $100 to win $120

### Prediction Guidelines:

- Enter as percentage (0-100)
- 50% = coin flip (even teams)
- 60% = moderate favorite
- 70%+ = heavy favorite
- Must be between 1-99%

---

## 📖 Understanding the Output

### Output Sections:

#### 1. Fair Odds (Vig Removed)
```
Lakers: 56.2%
Celtics: 43.8%
```
- **What it means:** True market probability without bookmaker profit margin
- **How it's calculated:** Removes the "vig" (bookmaker's edge)

#### 2. Your Prediction
```
Lakers: 62.0%
Celtics: 38.0%
```
- **What it means:** Your assessment of win probability
- **Note:** Must sum to 100%

#### 3. Betting Edge
```
Lakers: +5.8%
Celtics: -5.8%
```
- **Formula:** Edge = (Your Prediction - Fair Odds) × 100
- **Positive edge:** You think the team is undervalued
- **Negative edge:** You think the team is overvalued
- **Threshold:** Professional bettors look for edges > 2%

#### 4. Recommendation
```
RECOMMENDED BET: LAKERS
5.8% edge (MEDIUM-HIGH confidence)
```

**Confidence Levels:**
- **0-2%:** NO BET (edge too small)
- **2-4%:** LOW confidence
- **4-6%:** MEDIUM confidence  
- **6-8%:** MEDIUM-HIGH confidence
- **8%+:** HIGH confidence

### What LLM Mode Adds (Optional):

When LLM mode is enabled, you also see:

**Agent Insights:**
- **OddsAnalyzer:** Explains vig removal process
- **EdgeCalculator:** Assesses betting opportunity quality
- **ReportGenerator:** Provides betting context

---

## 🔧 Troubleshooting

### Problem: "Command not found: python3"

**Solution:**
```bash
# Try 'python' instead
python --version

# If that works, use 'python' instead of 'python3' in all commands
python demo.py
```

### Problem: "No module named 'numpy'"

**Solution:**
```bash
# Install missing dependency
pip install numpy --break-system-packages

# Or install all at once
pip install -r requirements.txt --break-system-packages
```

### Problem: GUI window doesn't open

**Check if Tkinter is installed:**
```bash
python3 -c "import tkinter; print('Tkinter available!')"
```

**If not available:**
- **macOS:** `brew install python-tk`
- **Ubuntu/Debian:** `sudo apt-get install python3-tk`
- **Windows:** Reinstall Python with Tkinter option checked

### Problem: "Address already in use" (Port 5001)

**Solution:**
```bash
# Stop other programs using port 5001
# Or edit web_server.py line 155 to use different port:
app.run(debug=True, host='0.0.0.0', port=5002)  # Change 5001 to 5002
```

### Problem: Slow performance / Long loading time

**This is normal if:**
- First time using LLM mode (downloads 7.6GB Phi-3-mini model)
- No GPU available (CPU inference is slower)

**Solutions:**
- Wait for first download to complete (only happens once)
- Use rule-based mode (still accurate, much faster)
- System automatically falls back to rule-based if LLM unavailable

### Problem: Wrong edge calculations (showing 0.06% instead of 5.8%)

**Solution:**
```bash
# Make sure you have the FIXED probability_adjuster.py
grep "* 100" src/fairllm_agent/probability_adjuster.py

# Should show: return {"home": (model_p["home"] - fair_p["home"]) * 100, ...}
# If not, copy the fixed version from /mnt/user-data/outputs/
```

### Problem: "Cannot find fairllm_agent module"

**Solution:**
```bash
# Make sure you're in the project root directory
cd ~/Downloads/final-project-alex-and-jaeden-1/fairllm-sports-edge
pwd  # Should end with /fairllm-sports-edge

# Check that src/ directory exists
ls src/fairllm_agent/
```

### Problem: Web page shows "Connection refused"

**Solution:**
1. Make sure the server is actually running (check terminal)
2. Use the exact URL: `http://localhost:5001`
3. Try `http://127.0.0.1:5001` instead
4. Check if another program is using port 5001

---

## 🚀 Advanced: LLM Mode

### What is LLM Mode?

- **Rule-Based Mode (default):** Fast mathematical calculations (~2 seconds)
- **LLM Mode:** Adds natural language explanations (~5-8 seconds)

### When to Use LLM Mode:

✅ **Use LLM Mode when:**
- You want to understand WHY the system recommends a bet
- Presenting to non-technical audience
- Learning about betting analysis
- First-time users

✅ **Use Rule-Based Mode when:**
- You need fast results
- Analyzing many games quickly
- You understand the calculations
- Running on limited hardware

### Enabling LLM Mode:

LLM mode is **automatically attempted** if transformers/torch are installed.

**To force LLM mode:**
```bash
# Make sure LLM dependencies are installed
pip install transformers torch accelerate --break-system-packages

# Run normally - system will use LLM mode if available
python3 chatbot_gui.py
```

**To force rule-based mode:**
```bash
# Simply don't install transformers/torch
# OR temporarily rename the fair_framework file to skip LLM loading
```

### First Run with LLM:

**Expect:**
- 7.6GB download (Phi-3-mini model from HuggingFace)
- 5-10 minutes on first use
- Subsequent runs are much faster (model is cached)

**Download location:**
```
~/.cache/huggingface/hub/
```

### LLM Performance:

| Hardware | Analysis Time |
|----------|--------------|
| GPU (CUDA) | 3-5 seconds |
| M1/M2/M3 Mac | 5-8 seconds |
| CPU only | 10-15 seconds |

---

## 📊 Complete Workflow Example

Let's walk through a complete analysis from start to finish:

### Scenario: Analyzing Tonight's Game

**You think:** Warriors will beat the Suns with 55% confidence  
**Bookmaker odds:** Warriors -150, Suns +130

### Step 1: Choose Your Interface

```bash
# Let's use the web browser for best visuals
python3 web_server.py
```

### Step 2: Open Browser

```
http://localhost:5001
```

### Step 3: Enter Your Analysis

Click example or type:
```
Warriors vs Suns, Warriors -150, Suns +130, Warriors 55%
```

### Step 4: Review Results

**System shows:**
```
Fair Odds: Warriors 59.5%, Suns 40.5%
Your Prediction: Warriors 55.0%, Suns 45.0%
Edge: Warriors -4.5%, Suns +4.5%

RECOMMENDATION: NO BET
No significant edge detected
```

### Step 5: Interpret

- Fair odds show Warriors at 59.5%
- You think they're only 55%
- Market is actually MORE confident than you
- Your prediction is WORSE than market consensus
- **Correct decision: Don't bet!**

### Alternative Scenario: Finding Value

**Different prediction:** Warriors 65%

```
Fair Odds: Warriors 59.5%, Suns 40.5%
Your Prediction: Warriors 65.0%, Suns 35.0%
Edge: Warriors +5.5%, Suns -5.5%

RECOMMENDATION: BET WARRIORS
5.5% edge (MEDIUM-HIGH confidence)
```

Now there's value! You're more confident than the market.

---

## 🎓 Tips for Best Results

### For Accurate Analysis:

1. **Be honest with your predictions**
   - Don't adjust to "find" a bet
   - Enter your true assessment

2. **Consider all factors**
   - Injuries, home/away, recent form
   - Head-to-head history
   - Motivation (playoffs vs regular season)

3. **Use multiple sources**
   - FiveThirtyEight ratings
   - Team stats
   - Expert analysis

4. **Look for 2%+ edges**
   - Smaller edges often aren't worth the risk
   - Account for bet sizing and bankroll

### For System Performance:

1. **First run:** Wait for any downloads to complete
2. **Web version:** Keep terminal open while using browser
3. **Desktop GUI:** Click examples to avoid typos
4. **LLM mode:** Be patient on slower computers

### For Presentations:

1. **Pre-load the system:** Start before presenting
2. **Use web version:** Most visually impressive
3. **Have examples ready:** Lakers example always works well
4. **Show both interfaces:** CLI for speed, Web for polish

---

## 📚 Quick Reference Card

### Three Commands to Remember:

```bash
python3 demo.py          # CLI - Fast testing
python3 chatbot_gui.py   # GUI - Visual interface  
python3 web_server.py    # Web - Modern UI
```

### Input Format:

```
Team1 vs Team2, Odds1, Odds2, Prediction%
```

### Edge Formula:

```
Edge = (Your Prediction - Fair Odds) × 100
```

### Decision Rule:

```
Edge > 2% → Consider betting
Edge < 2% → Don't bet
```

---

## ✅ Pre-Flight Checklist

Before running the system:

- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] In correct directory (should see `src/` folder)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Port 5001 available (for web version)
- [ ] Know your input format (Team vs Team, odds, prediction)

---

## 🎉 You're Ready!

You now have everything you need to run the Sports Edge Analysis System!

**Remember:**
- ✅ Three interfaces to choose from
- ✅ Rule-based mode works immediately  
- ✅ LLM mode adds explanations (optional)
- ✅ Look for edges > 2%
- ✅ Bet responsibly!

**Questions?**
- Check the troubleshooting section
- Review the examples
- Check GitHub issues: https://github.com/USAFADFCS/final-project-alex-and-jaeden

**Happy analyzing! 🎯**
