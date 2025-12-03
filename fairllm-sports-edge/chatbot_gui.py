#!/usr/bin/env python3
"""
GUI Chatbot: Sports Edge Analysis Assistant
Modern chat interface in a separate window.
"""

import sys
sys.path.insert(0, 'src')

import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
from fairllm_agent.agentic_workflow_llm import LLMSportsEdgeFlow


class SportsBettingChatGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Sports Edge AI Assistant")
        self.window.geometry("800x700")
        self.window.minsize(700, 600)

        # Outer background to mimic a device border (black)
        self.window.configure(bg="#000000")

        # Initialize workflow
        self.workflow = None
        self.loading = False
        self.send_enabled = False

        # Placeholder attributes for message area
        self.canvas = None
        self.messages_frame = None

        # Setup UI
        self.setup_ui()

        # Load workflow in background
        threading.Thread(target=self.load_workflow, daemon=True).start()

    def setup_ui(self):
        # Center white "phone" card – smaller black border
        phone_frame = tk.Frame(
            self.window,
            bg="white",
            bd=0,
            highlightthickness=0
        )
        phone_frame.pack(fill="both", expand=True, padx=20, pady=18)

        # Header bar (blue strip at top)
        header = tk.Frame(phone_frame, bg="#3b46fa", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Left side of header (title + subtitle)
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

        # Right side of header (Demo button + menu line)
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

        # Chat area container
        chat_container = tk.Frame(phone_frame, bg="white")
        chat_container.pack(fill="both", expand=True, padx=10, pady=(6, 0))

        # Canvas + scrollbar for scrollable messages
        self.canvas = tk.Canvas(
            chat_container,
            bg="white",
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            chat_container,
            orient="vertical",
            command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame inside canvas to hold message bubbles
        self.messages_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")

        # Update scrollregion when size changes
        self.messages_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Bottom input bar
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

        # Custom blue "Send" button built on a Canvas
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

        # Hint label above the input
        hint_label = tk.Label(
            phone_frame,
            text='Try: "Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%"',
            font=("Segoe UI", 9),
            bg="white",
            fg="#9ca3af"
        )
        hint_label.pack(fill="x", padx=18, pady=(4, 0))

        # Status label at bottom (inside black area)
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

        # Initial system messages (no emojis)
        self.add_message("system", "Welcome to Sports Edge Chat.")
        self.add_message(
            "system",
            "Once the AI loads, describe a matchup with odds and your win probability."
        )
        self.add_message(
            "system",
            "Example: 'Lakers vs Celtics, Lakers -140, Celtics +120, I predict Lakers 62%'."
        )

        self.input_field.focus_set()

    # ---------- Send button helpers (canvas-based) ----------

    def _on_send_click(self, event):
        if self.send_enabled:
            self.send_message()

    def _set_send_button_enabled(self, enabled: bool):
        """Redraw the custom send button in enabled/disabled state."""
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

        # Simple rounded-ish rectangle
        self.send_button.create_rectangle(
            0, 0, 80, 32,
            outline=fill,
            fill=fill,
            width=0,
            tags="btn_bg"
        )
        self.send_button.create_text(
            40, 16,
            text="Send",
            fill=text_color,
            font=("Segoe UI", 11, "bold"),
            tags="btn_label"
        )
        self.send_button.config(cursor=cursor)

        # Bind/unbind click
        self.send_button.bind("<Button-1>", self._on_send_click if enabled else lambda e: None)

    # ---------- AI workflow loading ----------

    def load_workflow(self):
        """Load the AI workflow in background"""
        try:
            self.workflow = LLMSportsEdgeFlow()
            agents_count = len(self.workflow.agents)

            def on_ready():
                self.status_label.config(
                    text=f"Ready — {agents_count} AI agents loaded"
                )
                self._set_send_button_enabled(True)
                self.add_message(
                    "system",
                    "You can now type a matchup with odds and your win probability."
                )

            self.window.after(0, on_ready)
        except Exception as e:
            def on_error():
                self.status_label.config(
                    text=f"Error loading AI agents: {e}"
                )
                self.add_message("system", f"Error loading AI workflow: {e}")
            self.window.after(0, on_error)

    # ---------- Message UI helpers ----------

    def _scroll_to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def add_message(self, sender, text):
        """
        Add a message bubble to the chat area.
        sender: 'user', 'ai', 'system', 'result', 'recommendation'
        """
        wrap_width = 480

        row = tk.Frame(self.messages_frame, bg="white")
        row.pack(fill="x", pady=6, padx=12)

        if sender == "user":
            # Right-aligned blue bubble
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
            # Left-aligned bubble with small avatar-style dot
            avatar = tk.Canvas(
                row,
                width=28,
                height=28,
                bg="white",
                highlightthickness=0,
                bd=0
            )
            avatar.pack(side="left", padx=(0, 6), pady=(4, 0))
            avatar.create_oval(4, 4, 24, 24, fill="#3b46fa", outline="")

            if sender == "ai":
                bubble_color = "#e6edff"
                text_color = "#111827"
                font_size = 11
            elif sender == "result":
                bubble_color = "#f0eaff"
                text_color = "#111827"
                font_size = 10
            else:  # recommendation
                bubble_color = "#e3f8e8"
                text_color = "#064e3b"
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
            # Centered lighter text (no bubble)
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

    # ---------- Chat logic ----------

    def send_message(self):
        """Handle user message"""
        if self.loading:
            return

        message = self.input_field.get().strip()
        if not message:
            return

        if self.workflow is None:
            self.add_message("system", "AI agents are still loading. Please wait a moment.")
            return

        self.input_field.delete(0, tk.END)
        self.add_message("user", message)

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
                self.window.after(
                    0,
                    lambda: self.add_message(
                        "ai",
                        "I could not understand that input. "
                        "Please use a format like: "
                        "'Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%'."
                    )
                )
                self.window.after(0, self.reset_input)
                return

            self.window.after(
                0,
                lambda: self.add_message("system", "Running AI analysis...")
            )

            # Build data for workflow
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
            self.window.after(0, lambda: self.add_message("ai", f"Error: {str(e)}"))
            self.window.after(
                0,
                lambda: self.status_label.config(
                    text="An error occurred during analysis."
                )
            )
        finally:
            self.window.after(0, self.reset_input)

    def parse_message(self, message):
        """Parse user message to extract game info"""
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
                away_odds = int(odds[1])   # <-- fixed typo here
            else:
                home_odds = -150
                away_odds = +130

            # Extract probability (assume last number is home win %)
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
        """Display analysis results as a series of AI messages"""
        self.add_message("ai", "Analysis complete. Here are the details:")

        # Fair odds
        fair_home = report["fair_probabilities"]["home"]
        fair_away = report["fair_probabilities"]["away"]
        self.add_message(
            "result",
            f"Fair odds (vig removed):\n"
            f"{parsed['home']}: {fair_home:.1%}\n"
            f"{parsed['away']}: {fair_away:.1%}"
        )

        # Model prediction
        model_home = report["model_probabilities"]["home"]
        model_away = report["model_probabilities"]["away"]
        self.add_message(
            "result",
            f"Your prediction:\n"
            f"{parsed['home']}: {model_home:.1%}\n"
            f"{parsed['away']}: {model_away:.1%}"
        )

        # Edge
        home_edge = report["edge_analysis"]["edge_pct"]["home"]
        away_edge = report["edge_analysis"]["edge_pct"]["away"]
        self.add_message(
            "result",
            f"Betting edge:\n"
            f"{parsed['home']}: {home_edge:+.2f}%\n"
            f"{parsed['away']}: {away_edge:+.2f}%"
        )

        # Recommendation
        rec = report["recommendation"]
        self.add_message("recommendation", rec)

        # Responsible betting reminder
        self.add_message(
            "system",
            "Reminder: Bet responsibly and never stake more than you can afford to lose."
        )

        self.status_label.config(text="Analysis complete")

    def reset_input(self):
        """Reset input controls"""
        self.loading = False
        if self.workflow is not None:
            self._set_send_button_enabled(True)
        else:
            self._set_send_button_enabled(False)
        self.input_field.focus()

    # Optional helpers

    def run_example(self):
        """Run an example analysis when Demo button is pressed"""
        if self.workflow is None:
            self.add_message(
                "system",
                "Agents are still loading; the demo will work once they are ready."
            )
            return
        self.input_field.delete(0, tk.END)
        self.input_field.insert(
            0,
            "Lakers vs Celtics, Lakers -140, Celtics +120, Lakers 62%"
        )
        self.send_message()

    def reset_conversation(self):
        """Clear chat and start fresh"""
        for child in self.messages_frame.winfo_children():
            child.destroy()
        self.add_message("system", "New conversation started.")

    def run(self):
        """Start the GUI"""
        self.window.mainloop()


def main():
    app = SportsBettingChatGUI()
    app.run()


if __name__ == "__main__":
    main()
