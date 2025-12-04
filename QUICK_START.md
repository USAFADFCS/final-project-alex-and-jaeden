# ⚡ QUICK START GUIDE
**Sports Edge Analysis System - One Page Reference**

---

## 🚀 Installation (One Time)

```bash
cd ~/Downloads/final-project-alex-and-jaeden-1/fairllm-sports-edge
pip install numpy rich flask --break-system-packages
```

---

## 🎯 Running the System

### Option 1: Command Line (Fastest)
```bash
python3 demo.py
```

### Option 2: Desktop GUI (Visual)
```bash
python3 chatbot_gui.py
```

### Option 3: Web Browser (Best for Demo)
```bash
python3 web_server.py
# Then open: http://localhost:5001
```

---

## 📝 Input Format

```
Team1 vs Team2, Team1 Odds, Team2 Odds, Prediction%
```

### Examples:
```
Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%
Warriors -150, Suns +130, Warriors 55%
Chiefs vs Bills, -200, +170, 58%
```

---

## 📊 Reading Results

### Fair Odds
Market probability after removing bookmaker's profit margin

### Your Prediction  
Your assessment of team win probability

### Betting Edge
```
Edge = (Your Prediction - Fair Odds) × 100
```

### Recommendation
- **> 2% edge:** Consider betting
- **< 2% edge:** Don't bet

### Confidence Levels
- 0-2%: NO BET
- 2-4%: LOW
- 4-6%: MEDIUM
- 6-8%: MEDIUM-HIGH
- 8%+: HIGH

---

## 🔧 Common Issues

### "No module named X"
```bash
pip install -r requirements.txt --break-system-packages
```

### "Command not found: python3"
```bash
python demo.py  # Try 'python' instead
```

### Port 5001 in use
Edit `web_server.py` line 155: change 5001 to 5002

### GUI won't open
```bash
# macOS:
brew install python-tk

# Ubuntu:
sudo apt-get install python3-tk
```

---

## 🎓 Tips

✅ Use clickable examples in GUI/Web (zero errors)  
✅ Look for edges > 2%  
✅ First LLM run takes 5-10 min (downloads model)  
✅ Web version best for presentations  
✅ CLI version fastest for testing  

---

## 📚 Full Documentation

See `FINAL_USER_GUIDE.md` for complete instructions

---

**Ready to analyze! 🎯**
