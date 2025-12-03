#!/usr/bin/env python3
"""
Conversational GUI Chatbot: Sports Edge Analysis Assistant
Multi-turn conversation with API/RAG prediction integration
"""

import sys
sys.path.insert(0, 'src')

import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
from fairllm_agent.agentic_workflow_llm import LLMSportsEdgeFlow
from fairllm_agent.fivethirtyeight_fetcher import FiveThirtyEightFetcher


class ConversationalChatGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Sports Edge AI Assistant")
        self.window.geometry("800x700")
        self.window.minsize(700, 600)
        self.window.configure(bg="#000000")

        # Initialize workflow and prediction API
        self.workflow = None
        self.predictor = None
        self.loading = False
        self.send_enabled = False
        
        # Conversation state
        self.conversation_state = "GREETING"  # GREETING, AWAITING_MATCHUP, AWAITING_ODDS, AWAITING_PREDICTION_CHOICE, AWAITING_MANUAL_PREDICTION, COMPLETE
        self.current_data = {}

        # Placeholder attributes
        self.canvas = None
        self.messages_frame = None

        # Setup UI
        self.setup_ui()

        # Load workflow in background
        threading.Thread(target=self.load_services, daemon=True).start()

    def setup_ui(self):
        # Phone frame
        phone_frame = tk.Frame(self.window, bg="white", bd=0, highlightthickness=0)
        phone_frame.pack(fill="both", expand=True, padx=20, pady=18)

        # Header
        header = tk.Frame(phone_frame, bg="#3b46fa", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        header_left = tk.Frame(header, bg="#3b46fa")
        header_left.pack(side="left", fill="both", expand=True, padx=20)

        title = tk.Label(
            header_left,
            text="Sports Edge Chat",
            font=("Segoe UI", 16, "bold"),
            bg="#3b46fa",
            fg="white"
        )
        title.pack(anchor="w", pady=(12, 0))

        subtitle = tk.Label(
            header_left,
            text="Conversational AI analysis",
            font=("Segoe UI", 9),
            bg="#3b46fa",
            fg="#dbe4ff"
        )
        subtitle.pack(anchor="w")

        # Right side buttons
        header_right = tk.Frame(header, bg="#3b46fa")
        header_right.pack(side="right", padx=20)

        tk.Button(
            header_right,
            text="New",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#3b46fa",
            activebackground="#e5ecff",
            activeforeground="#3b46fa",
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=2,
            command=self.reset_conversation,
            cursor="hand2"
        ).pack(side="left", pady=(16, 0), padx=(0, 10))

        menu_line = tk.Label(
            header_right,
            text="―",
            font=("Segoe UI", 16, "bold"),
            bg="#3b46fa",
            fg="white"
        )
        menu_line.pack(side="right", pady=(18, 0))

        # Chat area
        chat_container = tk.Frame(phone_frame, bg="white")
        chat_container.pack(fill="both", expand=True, padx=10, pady=(6, 0))

        self.canvas = tk.Canvas(chat_container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.messages_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")

        self.messages_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Input area
        input_bar = tk.Frame(phone_frame, bg="white", height=70)
        input_bar.pack(fill="x", side="bottom", pady=(0, 5))
        input_bar.pack_propagate(False)

        entry_holder = tk.Frame(input_bar, bg="#f3f4f6")
        entry_holder.pack(side="left", fill="x", expand=True, padx=(16, 8), pady=10)

        self.input_field = tk.Entry(
            entry_holder,
            font=("Segoe UI", 11),
            bg="#f3f4f6",
            fg="#111827",
            relief=tk.FLAT,
            insertbackground="#111827"
        )
        self.input_field.pack(fill="both", expand=True, padx=10, pady=6)
        self.input_field.bind("<Return>", lambda e: self.send_message())

        # Send button
        send_button_holder = tk.Frame(input_bar, bg="white")
        send_button_holder.pack(side="right", padx=(0, 16), pady=10)

        self.send_button = tk.Canvas(
            send_button_holder,
            width=80,
            height=32,
            bg="white",
            highlightthickness=0,
            bd=0
        )
        self.send_button.pack()
        self._set_send_button_enabled(False)

        # Hint label
        self.hint_label = tk.Label(
            phone_frame,
            text='Waiting for AI to load...',
            font=("Segoe UI", 9),
            bg="white",
            fg="#9ca3af"
        )
        self.hint_label.pack(fill="x", padx=18, pady=(4, 0))

        # Status label
        self.status_label = tk.Label(
            self.window,
            text="Initializing AI agents and prediction API...",
            font=("Segoe UI", 9),
            bg="#000000",
            fg="#e5e7eb",
            anchor="w",
            padx=16
        )
        self.status_label.pack(fill="x", side="bottom", pady=(0, 6))

        # Initial greeting
        self.add_message("system", "Initializing AI agents and prediction services...")

        self.input_field.focus_set()

    def _on_send_click(self, event):
        if self.send_enabled:
            self.send_message()

    def _set_send_button_enabled(self, enabled: bool):
        self.send_enabled = enabled
        self.send_button.delete("all")

        if enabled:
            fill = "#3b46fa"
            text_color = "white"
            cursor = "hand2"
        else:
            fill = "#9ca3af"
            text_color = "#e5e7eb"
            cursor = "arrow"

        self.send_button.create_rectangle(0, 0, 80, 32, outline=fill, fill=fill, width=0, tags="btn_bg")
        self.send_button.create_text(40, 16, text="Send", fill=text_color, font=("Segoe UI", 11, "bold"), tags="btn_label")
        self.send_button.config(cursor=cursor)
        self.send_button.bind("<Button-1>", self._on_send_click if enabled else lambda e: None)

    def load_services(self):
        """Load AI workflow and prediction API in background"""
        try:
            self.workflow = LLMSportsEdgeFlow()
            self.predictor = FiveThirtyEightFetcher()
            
            agents_count = len(self.workflow.agents)
            
            self.window.after(0, lambda: self.status_label.config(
                text=f"✓ Ready! {agents_count} AI agents + Elo prediction API loaded"
            ))
            self.window.after(0, lambda: self._set_send_button_enabled(True))
            self.window.after(0, self.start_greeting)
            
        except Exception as e:
            self.window.after(0, lambda: self.add_message("system", f"Error loading services: {e}"))
            self.window.after(0, lambda: self.status_label.config(text="Error - some features unavailable"))

    def start_greeting(self):
        """Start the conversation"""
        self.add_message("ai", "Hi! I'm your Sports Edge AI assistant. I'll help you find valuable betting opportunities.")
        self.add_message("ai", "Let's analyze a game together. What matchup would you like to look at?")
        self.hint_label.config(text='Example: "Lakers vs Celtics" or "Chiefs vs Bills"')
        self.conversation_state = "AWAITING_MATCHUP"

    def _scroll_to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def add_message(self, sender, text):
        """Add a message bubble to the chat"""
        row = tk.Frame(self.messages_frame, bg="white")
        row.pack(fill="x", pady=4)

        wrap_width = 500

        if sender == "user":
            bubble = tk.Frame(row, bg="#3b46fa")
            bubble.pack(side="right", padx=(40, 0))
            label = tk.Label(
                bubble,
                text=text,
                font=("Segoe UI", 11),
                bg="#3b46fa",
                fg="white",
                wraplength=wrap_width,
                justify="left"
            )
            label.pack(padx=12, pady=8)

        elif sender in ("ai", "result", "recommendation"):
            if sender == "result":
                bubble_color = "#f3f4f6"
                text_color = "#374151"
                font_size = 10
            elif sender == "recommendation":
                bubble_color = "#e3f8e8"
                text_color = "#064e3b"
                font_size = 11
            else:  # ai
                bubble_color = "#f3f4f6"
                text_color = "#111827"
                font_size = 11

            bubble = tk.Frame(row, bg=bubble_color)
            bubble.pack(side="left", padx=(0, 40))
            label = tk.Label(
                bubble,
                text=text,
                font=("Segoe UI", font_size),
                bg=bubble_color,
                fg=text_color,
                wraplength=wrap_width,
                justify="left"
            )
            label.pack(padx=12, pady=8)

        elif sender == "system":
            label = tk.Label(
                row,
                text=text,
                font=("Segoe UI", 9, "italic"),
                bg="white",
                fg="#6b7280",
                wraplength=540,
                justify="center"
            )
            label.pack(anchor="center", padx=40)

        self._scroll_to_bottom()

    def send_message(self):
        """Handle user message"""
        if self.loading or not self.send_enabled:
            return

        message = self.input_field.get().strip()
        if not message:
            return

        if self.workflow is None:
            self.add_message("system", "AI is still loading, please wait...")
            return

        self.input_field.delete(0, tk.END)
        self.add_message("user", message)

        self.loading = True
        self._set_send_button_enabled(False)
        threading.Thread(target=self.process_conversation, args=(message,), daemon=True).start()

    def process_conversation(self, message):
        """Process message based on conversation state"""
        try:
            if self.conversation_state == "AWAITING_MATCHUP":
                self.handle_matchup(message)
                
            elif self.conversation_state == "AWAITING_ODDS":
                self.handle_odds(message)
                
            elif self.conversation_state == "AWAITING_PREDICTION_CHOICE":
                self.handle_prediction_choice(message)
                
            elif self.conversation_state == "AWAITING_MANUAL_PREDICTION":
                self.handle_manual_prediction(message)
                
        except Exception as e:
            self.window.after(0, lambda: self.add_message("ai", f"Sorry, I encountered an error: {str(e)}"))
            self.window.after(0, lambda: self.add_message("ai", "Let's start over. What game would you like to analyze?"))
            self.window.after(0, self.reset_state)
        finally:
            self.window.after(0, self.reset_input)

    def handle_matchup(self, message):
        """Parse matchup from user input"""
        teams = self.parse_teams(message)
        if teams is None:
            self.window.after(0, lambda: self.add_message(
                "ai",
                "I couldn't identify the teams. Please use format like 'Lakers vs Celtics' or 'Chiefs vs Bills'."
            ))
            return

        self.current_data['home_team'] = teams[0]
        self.current_data['away_team'] = teams[1]
        
        self.window.after(0, lambda: self.add_message(
            "ai",
            f"Got it! {teams[0]} vs {teams[1]}. Now, what are the current betting odds?"
        ))
        self.window.after(0, lambda: self.hint_label.config(
            text=f'Example: "{teams[0]} -140, {teams[1]} +120"'
        ))
        self.window.after(0, lambda: setattr(self, 'conversation_state', "AWAITING_ODDS"))

    def handle_odds(self, message):
        """Parse odds from user input"""
        odds = self.parse_odds(message)
        if odds is None:
            self.window.after(0, lambda: self.add_message(
                "ai",
                "I couldn't parse those odds. Please use format like '-140, +120' or 'home -140 away +120'."
            ))
            return

        self.current_data['home_odds'] = odds[0]
        self.current_data['away_odds'] = odds[1]
        
        # Check if we have API predictions available
        home = self.current_data['home_team']
        away = self.current_data['away_team']
        
        prediction = None
        if self.predictor:
            prediction = self.predictor.get_game_prediction(home, away)
        
        if prediction:
            self.window.after(0, lambda: self.add_message(
                "ai",
                f"Perfect! I found an Elo prediction for this game: {home} has a {prediction['home_prob']:.0%} chance to win."
            ))
            self.window.after(0, lambda: self.add_message(
                "ai",
                "Would you like to use this prediction, or do you have your own? (Type 'use elo' or enter your own like '62%')"
            ))
            self.window.after(0, lambda: self.hint_label.config(
                text='Type "use elo" or enter your prediction like "62%"'
            ))
            self.current_data['api_prediction'] = prediction
            self.conversation_state = "AWAITING_PREDICTION_CHOICE"
        else:
            self.window.after(0, lambda: self.add_message(
                "ai",
                f"Great! Now, what's your prediction? What % chance does {home} have to win?"
            ))
            self.window.after(0, lambda: self.hint_label.config(text='Example: "62%" or "58"'))
            self.conversation_state = "AWAITING_MANUAL_PREDICTION"

    def handle_prediction_choice(self, message):
        """Handle user choice between API prediction or manual"""
        message_lower = message.lower()
        
        if 'elo' in message_lower or 'api' in message_lower or 'use' in message_lower:
            # Use API prediction
            prediction = self.current_data['api_prediction']
            self.current_data['home_prob'] = prediction['home_prob']
            self.current_data['away_prob'] = prediction['away_prob']
            
            self.window.after(0, lambda: self.add_message(
                "ai",
                f"Using Elo prediction: {self.current_data['home_team']} {prediction['home_prob']:.0%}, {self.current_data['away_team']} {prediction['away_prob']:.0%}"
            ))
            self.window.after(0, lambda: self.add_message("ai", "Analyzing now..."))
            self.window.after(0, self.run_analysis)
        else:
            # Try to parse as manual prediction
            prob = self.parse_probability(message)
            if prob is None:
                self.window.after(0, lambda: self.add_message(
                    "ai",
                    "I couldn't parse that. Type 'use elo' for the API prediction, or enter a percentage like '62%'."
                ))
                return
            
            self.current_data['home_prob'] = prob
            self.current_data['away_prob'] = 1.0 - prob
            
            self.window.after(0, lambda: self.add_message(
                "ai",
                f"Got your prediction: {self.current_data['home_team']} {prob:.0%}. Running analysis..."
            ))
            self.window.after(0, self.run_analysis)

    def handle_manual_prediction(self, message):
        """Parse manual prediction"""
        prob = self.parse_probability(message)
        if prob is None:
            self.window.after(0, lambda: self.add_message(
                "ai",
                "Please enter a valid probability like '62%' or '58'."
            ))
            return

        self.current_data['home_prob'] = prob
        self.current_data['away_prob'] = 1.0 - prob
        
        self.window.after(0, lambda: self.add_message("ai", "Perfect! Analyzing now..."))
        self.window.after(0, self.run_analysis)

    def run_analysis(self):
        """Run the full analysis"""
        try:
            self.status_label.config(text="Running AI analysis...")
            
            odds_data = {
                "event_id": f"chat-{self.current_data['home_team']}-{self.current_data['away_team']}",
                "sport": "basketball",
                "league": "NBA",
                "home_team": self.current_data['home_team'],
                "away_team": self.current_data['away_team'],
                "sportsbook": "User Input",
                "moneyline": {
                    "home": self.current_data['home_odds'],
                    "away": self.current_data['away_odds']
                }
            }
            
            forecast_data = {
                "event_id": f"chat-{self.current_data['home_team']}-{self.current_data['away_team']}",
                "p_model": {
                    "home": self.current_data['home_prob'],
                    "away": self.current_data['away_prob']
                }
            }
            
            report = self.workflow.run(odds_data, forecast_data)
            
            self.window.after(0, lambda: self.display_results(report))
            self.conversation_state = "COMPLETE"
            
        except Exception as e:
            self.window.after(0, lambda: self.add_message("ai", f"Analysis error: {str(e)}"))

    def display_results(self, report):
        """Display the analysis results"""
        self.add_message("ai", "Analysis complete! Here's what I found:")
        
        # Show LLM insights if available
        if 'llm_insights' in report:
            insights = report['llm_insights']
            
            if insights.get('odds_analysis') and insights['odds_analysis'] != "Analyzed odds and removed vig using standard mathematical formulas.":
                self.add_message("result", f"📊 {insights['odds_analysis']}")
            
            if insights.get('edge_insight') and insights['edge_insight'] != "Edge calculated. Positive edges indicate potential betting value.":
                self.add_message("result", f"💎 {insights['edge_insight']}")

        # Key metrics
        home = self.current_data['home_team']
        away = self.current_data['away_team']
        
        fair_home = report["fair_probabilities"]["home"]
        fair_away = report["fair_probabilities"]["away"]
        
        home_edge = report["edge_analysis"]["edge_pct"]["home"]
        away_edge = report["edge_analysis"]["edge_pct"]["away"]
        
        self.add_message(
            "result",
            f"Fair odds: {home} {fair_home:.1%}, {away} {fair_away:.1%}\n"
            f"Edge: {home} {home_edge:+.2f}%, {away} {away_edge:+.2f}%"
        )
        
        # Recommendation
        rec = report.get('llm_recommendation', report['recommendation'])
        self.add_message("recommendation", f"💰 {rec}")
        
        # Offer new analysis
        self.add_message("ai", "Want to analyze another game? Type 'yes' or tell me the matchup!")
        self.hint_label.config(text='Type "yes" to start fresh, or name a new matchup')
        self.status_label.config(text="Analysis complete")

    # Parsing helpers
    def parse_teams(self, text):
        """Extract team names"""
        text = text.lower()
        if ' vs ' in text or ' v ' in text:
            parts = text.replace(' v ', ' vs ').split(' vs ')
            return [parts[0].strip().title(), parts[1].strip().title()]
        
        words = text.split()
        if len(words) >= 2:
            return [words[0].title(), words[1].title()]
        return None

    def parse_odds(self, text):
        """Extract odds"""
        import re
        odds_pattern = r'[-+]\d+'
        odds = re.findall(odds_pattern, text)
        
        if len(odds) >= 2:
            return [int(odds[0]), int(odds[1])]
        return None

    def parse_probability(self, text):
        """Extract probability percentage"""
        import re
        prob_pattern = r'(\d+)%?'
        probs = re.findall(prob_pattern, text)
        
        if probs:
            prob = float(probs[0]) / 100 if int(probs[0]) > 1 else float(probs[0])
            return max(0.01, min(0.99, prob))
        return None

    def reset_state(self):
        """Reset conversation state"""
        self.current_data = {}
        self.conversation_state = "AWAITING_MATCHUP"
        self.hint_label.config(text='Example: "Lakers vs Celtics"')

    def reset_input(self):
        """Reset input controls"""
        self.loading = False
        if self.workflow is not None:
            self._set_send_button_enabled(True)
        self.input_field.focus()

    def reset_conversation(self):
        """Start new conversation"""
        for child in self.messages_frame.winfo_children():
            child.destroy()
        self.reset_state()
        self.add_message("ai", "New conversation! What matchup would you like to analyze?")

    def run(self):
        """Start the GUI"""
        self.window.mainloop()


def main():
    app = ConversationalChatGUI()
    app.run()


if __name__ == "__main__":
    main()
