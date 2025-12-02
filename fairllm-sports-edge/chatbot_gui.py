#!/usr/bin/env python3
"""
GUI Chatbot: Sports Edge Analysis Assistant
Modern chat interface in a separate window!
"""
import sys
sys.path.insert(0, 'src')

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import threading
from datetime import datetime
from fairllm_agent.agentic_workflow_llm import LLMSportsEdgeFlow


class SportsBettingChatGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🤖 Sports Edge AI Assistant")
        self.window.geometry("800x700")
        self.window.configure(bg='#1e1e1e')
        
        # Initialize workflow
        self.workflow = None
        self.loading = False
        
        # Setup UI
        self.setup_ui()
        
        # Load workflow in background
        threading.Thread(target=self.load_workflow, daemon=True).start()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg='#2563eb', height=80)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="🤖 Sports Edge AI Assistant",
            font=('Arial', 20, 'bold'),
            bg='#2563eb',
            fg='white'
        )
        title.pack(pady=15)
        
        subtitle = tk.Label(
            header,
            text="Chat with AI agents to analyze betting opportunities",
            font=('Arial', 10),
            bg='#2563eb',
            fg='#e0e0e0'
        )
        subtitle.pack()
        
        # Chat display area
        chat_frame = tk.Frame(self.window, bg='#1e1e1e')
        chat_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#2d2d2d',
            fg='#ffffff',
            insertbackground='white',
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.chat_display.pack(fill='both', expand=True)
        self.chat_display.config(state='disabled')
        
        # Configure tags for styling
        self.chat_display.tag_config('user', foreground='#60a5fa', font=('Arial', 11, 'bold'))
        self.chat_display.tag_config('ai', foreground='#34d399', font=('Arial', 11, 'bold'))
        self.chat_display.tag_config('system', foreground='#fbbf24', font=('Arial', 10, 'italic'))
        self.chat_display.tag_config('result', foreground='#a78bfa', font=('Arial', 10))
        self.chat_display.tag_config('recommendation', foreground='#10b981', font=('Arial', 12, 'bold'))
        self.chat_display.tag_config('warning', foreground='#f59e0b', font=('Arial', 11, 'bold'))
        
        # Input area
        input_frame = tk.Frame(self.window, bg='#1e1e1e')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        self.input_field = tk.Entry(
            input_frame,
            font=('Arial', 12),
            bg='#2d2d2d',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT
        )
        self.input_field.pack(side='left', fill='x', expand=True, ipady=10, padx=(0, 10))
        self.input_field.bind('<Return>', lambda e: self.send_message())
        
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            font=('Arial', 11, 'bold'),
            bg='#2563eb',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.send_message,
            padx=20,
            pady=10
        )
        self.send_button.pack(side='right')
        
        # Quick action buttons
        quick_frame = tk.Frame(self.window, bg='#1e1e1e')
        quick_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Button(
            quick_frame,
            text="📊 Example Analysis",
            font=('Arial', 9),
            bg='#374151',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.run_example,
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            quick_frame,
            text="❓ How to Use",
            font=('Arial', 9),
            bg='#374151',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.show_help,
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            quick_frame,
            text="🔄 New Analysis",
            font=('Arial', 9),
            bg='#374151',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.reset_conversation,
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        # Status bar
        self.status_label = tk.Label(
            self.window,
            text="Initializing AI agents...",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#9ca3af',
            anchor='w'
        )
        self.status_label.pack(fill='x', padx=10, pady=(0, 5))
        
        # Welcome message
        self.add_message("system", "🤖 Welcome! I'm your AI sports betting analyst.")
        self.add_message("system", "I'll help you analyze betting opportunities using 4 specialized AI agents.\n")
    
    def load_workflow(self):
        """Load the AI workflow in background"""
        try:
            self.workflow = LLMSportsEdgeFlow()
            self.window.after(0, lambda: self.status_label.config(
                text=f"✓ Ready! {len(self.workflow.agents)} AI agents loaded"
            ))
            self.window.after(0, lambda: self.add_message(
                "system",
                "Type a game to analyze (e.g., 'Lakers vs Celtics with Lakers -140 and Celtics +120, I predict Lakers 62%')\n"
            ))
        except Exception as e:
            self.window.after(0, lambda: self.add_message("system", f"⚠️ Error loading: {e}\n"))
    
    def add_message(self, sender, text):
        """Add a message to the chat display"""
        self.chat_display.config(state='normal')
        
        timestamp = datetime.now().strftime("%H:%M")
        
        if sender == 'user':
            self.chat_display.insert(tk.END, f"[{timestamp}] You: ", 'user')
            self.chat_display.insert(tk.END, f"{text}\n\n")
        elif sender == 'ai':
            self.chat_display.insert(tk.END, f"[{timestamp}] AI: ", 'ai')
            self.chat_display.insert(tk.END, f"{text}\n\n")
        elif sender == 'system':
            self.chat_display.insert(tk.END, f"{text}\n")
        elif sender == 'result':
            self.chat_display.insert(tk.END, f"{text}\n", 'result')
        elif sender == 'recommendation':
            self.chat_display.insert(tk.END, f"\n💰 {text}\n\n", 'recommendation')
        
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def send_message(self):
        """Handle user message"""
        if self.loading:
            return
        
        message = self.input_field.get().strip()
        if not message:
            return
        
        if self.workflow is None:
            self.add_message("system", "⏳ Still loading AI agents, please wait...\n")
            return
        
        self.input_field.delete(0, tk.END)
        self.add_message("user", message)
        
        # Process in background
        self.loading = True
        self.send_button.config(state='disabled', text="Thinking...")
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
    
    def process_message(self, message):
        """Process the message and run analysis"""
        try:
            # Parse the message
            parsed = self.parse_message(message)
            
            if parsed is None:
                self.window.after(0, lambda: self.add_message(
                    "ai",
                    "I couldn't understand that. Please format like:\n'Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%'"
                ))
                self.window.after(0, self.reset_input)
                return
            
            self.window.after(0, lambda: self.add_message("system", "🤖 Running AI analysis...\n"))
            self.window.after(0, lambda: self.status_label.config(text="🔄 Analyzing..."))
            
            # Run the workflow
            odds_data = {
                "event_id": f"chat-{parsed['home']}-{parsed['away']}",
                "sport": "basketball",
                "league": "NBA",
                "home_team": parsed['home'],
                "away_team": parsed['away'],
                "sportsbook": "User Input",
                "moneyline": {"home": parsed['home_odds'], "away": parsed['away_odds']}
            }
            
            forecast_data = {
                "event_id": f"chat-{parsed['home']}-{parsed['away']}",
                "p_model": {"home": parsed['home_prob'], "away": parsed['away_prob']}
            }
            
            report = self.workflow.run(odds_data, forecast_data)
            
            # Display results
            self.window.after(0, lambda: self.display_results(report, parsed))
            
        except Exception as e:
            self.window.after(0, lambda: self.add_message("ai", f"❌ Error: {str(e)}\n"))
        finally:
            self.window.after(0, self.reset_input)
    
    def parse_message(self, message):
        """Parse user message to extract game info"""
        try:
            message = message.lower()
            
            # Extract teams
            if ' vs ' in message or ' v ' in message:
                parts = message.replace(' v ', ' vs ').split(' vs ')
                home = parts[0].strip().title()
                away = parts[1].split(',')[0].strip().title()
            else:
                words = message.split()
                home = words[0].title() if len(words) > 0 else "Home"
                away = words[1].title() if len(words) > 1 else "Away"
            
            # Extract odds
            import re
            odds_pattern = r'[-+]\d+'
            odds = re.findall(odds_pattern, message)
            
            if len(odds) >= 2:
                home_odds = int(odds[0])
                away_odds = int(odds[1])
            else:
                home_odds = -150
                away_odds = +130
            
            # Extract probability
            prob_pattern = r'(\d+)%?'
            probs = re.findall(prob_pattern, message)
            
            if probs:
                home_prob = float(probs[-1]) / 100
                home_prob = max(0.01, min(0.99, home_prob))
            else:
                home_prob = 0.55
            
            away_prob = 1.0 - home_prob
            
            return {
                'home': home,
                'away': away,
                'home_odds': home_odds,
                'away_odds': away_odds,
                'home_prob': home_prob,
                'away_prob': away_prob
            }
            
        except:
            return None
    
    def display_results(self, report, parsed):
        """Display analysis results"""
        self.add_message("ai", "✅ Analysis complete! Here's what I found:\n")
        
        # Fair odds
        fair_home = report['fair_probabilities']['home']
        fair_away = report['fair_probabilities']['away']
        self.add_message("result", f"📊 Fair Odds (vig removed):")
        self.add_message("result", f"   {parsed['home']}: {fair_home:.1%}")
        self.add_message("result", f"   {parsed['away']}: {fair_away:.1%}\n")
        
        # Model prediction
        model_home = report['model_probabilities']['home']
        model_away = report['model_probabilities']['away']
        self.add_message("result", f"🎯 Your Prediction:")
        self.add_message("result", f"   {parsed['home']}: {model_home:.1%}")
        self.add_message("result", f"   {parsed['away']}: {model_away:.1%}\n")
        
        # Edge
        home_edge = report['edge_analysis']['edge_pct']['home']
        away_edge = report['edge_analysis']['edge_pct']['away']
        self.add_message("result", f"💎 Betting Edge:")
        self.add_message("result", f"   {parsed['home']}: {home_edge:+.2f}%")
        self.add_message("result", f"   {parsed['away']}: {away_edge:+.2f}%\n")
        
        # Recommendation
        rec = report['recommendation']
        self.add_message("recommendation", rec)
        
        self.status_label.config(text="✓ Analysis complete")
    
    def reset_input(self):
        """Reset input controls"""
        self.loading = False
        self.send_button.config(state='normal', text="Send")
        self.input_field.focus()
    
    def run_example(self):
        """Run an example analysis"""
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, "Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%")
        self.send_message()
    
    def show_help(self):
        """Show help information"""
        help_text = """
How to Use:

1. Type a matchup: "Lakers vs Celtics"
2. Include odds: "Lakers -140, Celtics +120"
3. Add your prediction: "Lakers 62%"

Example:
"Lakers vs Celtics, Lakers -140, Celtics +120, I predict Lakers 62%"

The AI will analyze and recommend!
        """
        self.add_message("system", help_text)
    
    def reset_conversation(self):
        """Clear chat and start fresh"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        self.add_message("system", "🔄 New conversation started!\n")
    
    def run(self):
        """Start the GUI"""
        self.window.mainloop()


def main():
    app = SportsBettingChatGUI()
    app.run()


if __name__ == "__main__":
    main()
