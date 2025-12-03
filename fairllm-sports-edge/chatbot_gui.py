#!/usr/bin/env python3
"""
GUI Chatbot: Sports Edge Analysis Assistant - FIXED VERSION
Proper message ordering and scroll behavior
"""

import sys
sys.path.insert(0, 'src')

import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
from fairllm_agent.agentic_workflow_llm import LLMSportsEdgeFlow


class ChatbotFixed:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Sports Edge AI Assistant")
        self.window.geometry("800x750")
        self.window.minsize(700, 650)
        self.window.configure(bg="#000000")

        # Initialize workflow
        self.workflow = None
        self.loading = False
        self.send_enabled = False

        # Placeholder attributes
        self.canvas = None
        self.messages_frame = None

        # Setup UI
        self.setup_ui()

        # Load workflow in background
        threading.Thread(target=self.load_workflow, daemon=True).start()

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
            text="Analyze matchups with AI",
            font=("Segoe UI", 9),
            bg="#3b46fa",
            fg="#dbe4ff"
        )
        subtitle.pack(anchor="w")

        # Right side buttons
        header_right = tk.Frame(header, bg="#3b46fa")
        header_right.pack(side="right", padx=20)

        demo_button = tk.Button(
            header_right,
            text="Demo",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#3b46fa",
            activebackground="#e5ecff",
            activeforeground="#3b46fa",
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=2,
            command=self.run_example,
            cursor="hand2"
        )
        demo_button.pack(side="left", pady=(16, 0), padx=(0, 10))

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
        self.canvas_window = self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")

        # Bind to update scroll region
        self.messages_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Bottom input area with examples
        input_section = tk.Frame(phone_frame, bg="white")
        input_section.pack(fill="x", side="bottom", pady=(0, 5))

        # Example suggestions (clickable chips)
        self.examples_frame = tk.Frame(input_section, bg="white", height=35)
        self.examples_frame.pack(fill="x", padx=16, pady=(0, 5))
        self.examples_frame.pack_propagate(False)

        # Input bar
        input_bar = tk.Frame(input_section, bg="white", height=70)
        input_bar.pack(fill="x")
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
            input_section,
            text='Waiting for AI to load...',
            font=("Segoe UI", 8),
            bg="white",
            fg="#9ca3af"
        )
        self.hint_label.pack(fill="x", padx=18, pady=(0, 2))

        # Status label
        self.status_label = tk.Label(
            self.window,
            text="Initializing AI agents...",
            font=("Segoe UI", 9),
            bg="#000000",
            fg="#e5e7eb",
            anchor="w",
            padx=16
        )
        self.status_label.pack(fill="x", side="bottom", pady=(0, 6))

        # Initial messages
        self.add_message("system", "Welcome to Sports Edge Chat.")
        self.add_message("system", "Once the AI loads, describe a matchup with odds and your prediction.")
        
        # Set initial examples
        self.show_examples([])

        self.input_field.focus_set()

    def _on_frame_configure(self, event):
        """Update scroll region when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _on_canvas_configure(self, event):
        """Update frame width when canvas resizes"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

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

    def show_examples(self, examples):
        """Display clickable example suggestions"""
        # Clear existing examples
        for widget in self.examples_frame.winfo_children():
            widget.destroy()

        if not examples:
            examples = [
                "Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%",
                "Warriors vs Suns, Warriors -150, Suns +130, Warriors 55%",
                "Chiefs vs Bills, Chiefs -200, Bills +170, Chiefs 58%"
            ]

        # Create scrollable container
        canvas = tk.Canvas(self.examples_frame, bg="white", highlightthickness=0, height=30)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.examples_frame, orient="horizontal", command=canvas.xview)
        scrollbar.pack(side="bottom", fill="x")
        canvas.configure(xscrollcommand=scrollbar.set)

        container = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=container, anchor="nw")

        for example in examples:
            btn = tk.Button(
                container,
                text=example if len(example) < 50 else example[:47] + "...",
                font=("Segoe UI", 9),
                bg="#f3f4f6",
                fg="#374151",
                activebackground="#e5e7eb",
                activeforeground="#111827",
                relief=tk.FLAT,
                bd=0,
                padx=12,
                pady=4,
                command=lambda ex=example: self.use_example(ex),
                cursor="hand2"
            )
            btn.pack(side="left", padx=4)

        container.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def use_example(self, example):
        """Fill input with example text"""
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, example)
        self.input_field.focus()

    def load_workflow(self):
        """Load AI workflow in background"""
        try:
            self.workflow = LLMSportsEdgeFlow()
            agents_count = len(self.workflow.agents)

            self.window.after(0, lambda: self.status_label.config(
                text=f"✓ Ready! {agents_count} AI agents loaded"
            ))
            self.window.after(0, lambda: self._set_send_button_enabled(True))
            self.window.after(0, lambda: self.add_message(
                "system",
                "AI loaded! Enter a matchup with odds and your prediction, or click an example below."
            ))
            self.window.after(0, lambda: self.hint_label.config(
                text='Click an example or type your own'
            ))
            self.window.after(0, lambda: self.show_examples([
                "Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%",
                "Warriors vs Suns, -150, +130, Warriors 55%",
                "Chiefs vs Bills, -200, +170, 58%"
            ]))

        except Exception as e:
            self.window.after(0, lambda: self.add_message("system", f"Error loading: {e}"))

    def _scroll_to_bottom(self):
        """Scroll to bottom of chat"""
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def add_message(self, sender, text):
        """Add a message bubble - MESSAGES APPEND TO BOTTOM"""
        row = tk.Frame(self.messages_frame, bg="white")
        row.pack(fill="x", pady=4, anchor="n")  # anchor="n" keeps them at top of frame

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
            else:
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

        # Scroll to bottom after adding message
        self.window.after(10, self._scroll_to_bottom)

    def send_message(self):
        """Handle user message"""
        if self.loading:
            return

        message = self.input_field.get().strip()
        if not message:
            return

        if self.workflow is None:
            self.add_message("system", "AI agents are still loading. Please wait.")
            return

        self.input_field.delete(0, tk.END)
        self.add_message("user", message)

        # Update examples
        self.show_examples([
            "Nuggets vs Clippers, -145, +125, 55%",
            "Ravens -120, Bengals +100, Ravens 52%",
            "Bruins vs Rangers, +105, -125, 48%"
        ])

        # Process in background
        self.loading = True
        self._set_send_button_enabled(False)
        self.status_label.config(text="Analyzing matchup...")
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()

    def process_message(self, message):
        """Process the message and run analysis"""
        try:
            parsed = self.parse_message(message)

            if parsed is None:
                self.window.after(0, lambda: self.add_message(
                    "ai",
                    "I could not understand that input. Try: 'Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%'"
                ))
                self.window.after(0, self.reset_input)
                return

            self.window.after(0, lambda: self.add_message("system", "Running AI analysis..."))

            # Build data
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
            self.window.after(0, lambda: self.display_results(report, parsed))

        except Exception as e:
            self.window.after(0, lambda: self.add_message("ai", f"Error: {str(e)}"))
            self.window.after(0, lambda: self.status_label.config(text="Error during analysis"))
        finally:
            self.window.after(0, self.reset_input)

    def parse_message(self, message):
        """Parse user message"""
        try:
            message = message.lower()

            # Extract teams
            if " vs " in message or " v " in message:
                parts = message.replace(" v ", " vs ").split(" vs ")
                home = parts[0].strip().title()
                away = parts[1].split(",")[0].strip().title()
            else:
                words = message.split()
                home = words[0].title() if len(words) > 0 else "Home"
                away = words[1].title() if len(words) > 1 else "Away"

            # Extract odds
            import re
            odds_pattern = r"[-+]\d+"
            odds = re.findall(odds_pattern, message)

            if len(odds) >= 2:
                home_odds = int(odds[0])
                away_odds = int(odds[1])
            else:
                home_odds = -150
                away_odds = +130

            # Extract probability
            prob_pattern = r"(\d+)%?"
            probs = re.findall(prob_pattern, message)

            if probs:
                home_prob = float(probs[-1]) / 100
                home_prob = max(0.01, min(0.99, home_prob))
            else:
                home_prob = 0.55

            away_prob = 1.0 - home_prob

            return {
                "home": home,
                "away": away,
                "home_odds": home_odds,
                "away_odds": away_odds,
                "home_prob": home_prob,
                "away_prob": away_prob
            }

        except Exception:
            return None

    def display_results(self, report, parsed):
        """Display analysis results"""
        self.add_message("ai", "Analysis complete. Here are the details:")

        # Show LLM insights if available
        if 'llm_insights' in report:
            insights = report['llm_insights']

            if insights.get('odds_analysis') and insights['odds_analysis'] != "Analyzed odds and removed vig using standard mathematical formulas.":
                self.add_message("ai", f"OddsAnalyzer: {insights['odds_analysis']}")

            if insights.get('forecast_evaluation') and insights['forecast_evaluation'] != "Forecast validated. Probabilities sum to 100% and are within valid ranges.":
                self.add_message("ai", f"ForecastEvaluator: {insights['forecast_evaluation']}")

            if insights.get('edge_insight') and insights['edge_insight'] != "Edge calculated. Positive edges indicate potential betting value.":
                self.add_message("ai", f"EdgeCalculator: {insights['edge_insight']}")

        # Fair odds
        fair_home = report["fair_probabilities"]["home"]
        fair_away = report["fair_probabilities"]["away"]
        self.add_message(
            "result",
            f"Fair odds (vig removed):\n{parsed['home']}: {fair_home:.1%}\n{parsed['away']}: {fair_away:.1%}"
        )

        # Model prediction
        model_home = report["model_probabilities"]["home"]
        model_away = report["model_probabilities"]["away"]
        self.add_message(
            "result",
            f"Your prediction:\n{parsed['home']}: {model_home:.1%}\n{parsed['away']}: {model_away:.1%}"
        )

        # Edge
        home_edge = report["edge_analysis"]["edge_pct"]["home"]
        away_edge = report["edge_analysis"]["edge_pct"]["away"]
        self.add_message(
            "result",
            f"Betting edge:\n{parsed['home']}: {home_edge:+.2f}%\n{parsed['away']}: {away_edge:+.2f}%"
        )

        # Recommendation
        if 'llm_recommendation' in report and report['llm_recommendation'] != "Recommendation generated based on edge thresholds and risk management.":
            self.add_message("recommendation", report['llm_recommendation'])
        else:
            rec = report["recommendation"]
            self.add_message("recommendation", rec)

        self.add_message("system", "Reminder: Bet responsibly.")

        # Update examples
        self.show_examples([
            "Mavericks vs Thunder, +120, -140, 46%",
            "Eagles -250, Dolphins +210, Eagles 61%",
            "Avalanche vs Knights, -120, +100, 52%"
        ])

        self.status_label.config(text="Analysis complete")

    def reset_input(self):
        """Reset input controls"""
        self.loading = False
        if self.workflow is not None:
            self._set_send_button_enabled(True)
        self.input_field.focus()

    def run_example(self):
        """Run demo analysis"""
        if self.workflow is None:
            self.add_message("system", "Agents still loading...")
            return
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, "Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%")
        self.send_message()

    def run(self):
        """Start the GUI"""
        self.window.mainloop()


def main():
    app = ChatbotFixed()
    app.run()


if __name__ == "__main__":
    main()