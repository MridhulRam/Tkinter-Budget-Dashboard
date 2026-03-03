import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

# --- CONFIGURATION ---
# REPLACE WITH YOUR EXACT PATH
FILE_PATH = "sample_data.xlsx"

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Financial Dashboard")
        self.root.geometry("1100x650") # Made window wider for the text

        # 1. Load Excel File
        self.sheet_names = self.get_sheet_names()
        if not self.sheet_names:
            return 

        # --- TOP CONTROL BAR ---
        control_frame = tk.Frame(root, pady=10, bg="#f0f0f0")
        control_frame.pack(fill=tk.X)

        # Label & Dropdown
        tk.Label(control_frame, text="Select Month:", bg="#f0f0f0", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
        self.selected_month = tk.StringVar()
        self.selected_month.set(self.sheet_names[0])
        self.dropdown = tk.OptionMenu(control_frame, self.selected_month, *self.sheet_names)
        self.dropdown.config(width=15, font=("Arial", 11))
        self.dropdown.pack(side=tk.LEFT, padx=10)

        # Button
        btn = tk.Button(control_frame, text="Analyze Health", command=self.generate_report, 
                        bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
        btn.pack(side=tk.LEFT, padx=10)

        # --- MAIN CONTENT AREA (Split Left/Right) ---
        content_frame = tk.Frame(root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # LEFT: Chart Area
        self.chart_frame = tk.LabelFrame(content_frame, text="Spending Breakdown", font=("Arial", 10, "bold"))
        self.chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = None

        # RIGHT: Text Report Area
        self.text_frame = tk.LabelFrame(content_frame, text="Financial Health Score", font=("Arial", 10, "bold"))
        self.text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # The actual text box widget
        self.report_text = tk.Text(self.text_frame, width=40, height=20, font=("Consolas", 10))
        self.report_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def get_sheet_names(self):
        if not os.path.exists(FILE_PATH):
            messagebox.showerror("Error", f"File not found:\n{FILE_PATH}")
            return []
        try:
            xl = pd.ExcelFile(FILE_PATH, engine='openpyxl')
            return xl.sheet_names
        except Exception as e:
            messagebox.showerror("Error", f"Could not read Excel file:\n{e}")
            return []

    def load_clean_data(self, sheet_name):
        """Loads data and fixes the column names/numbers."""
        try:
            df = pd.read_excel(FILE_PATH, sheet_name=sheet_name, engine='openpyxl')
            
            # 1. Clean Headers
            df.columns = df.columns.astype(str).str.strip()
            df = df.fillna(0)

            # 2. Define Map
            col_map = {
                'D-ticket':'D-ticket', 'Public transport':'Public transport', 'Taxi':'Taxi',
                'Shopping':'Shopping', 'Rent':'Rent', 'Subscriptions': 'Subscriptions',
                'Eating outside': 'Eating outside', 'Investment': 'Investment',
                'Trip expense': 'Trip expense', 'Trip stay': 'Trip stay',
                'Flight ticket booking': 'Flight ticket booking',
                'Money transfer within Germany':'Money transfer within Germany',
                'International transfer':'International transfer',
                'Entry tickets':'Entry tickets', 'Credit':'Credit'
            }

            # 3. Create missing columns & Force Numeric
            for c in col_map.values():
                if c not in df.columns:
                    df[c] = 0
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

            return df, col_map

        except Exception as e:
            messagebox.showerror("Data Error", str(e))
            return None, None

    def generate_report(self):
        """Master function: Draws Chart AND Writes Text."""
        month = self.selected_month.get()
        df, col_map = self.load_clean_data(month)
        
        if df is None: return

        # --- 1. PREPARE TOTALS ---
        # Grouping specifically for the Pie Chart
        chart_data = {
            'Transport': df[col_map['D-ticket']].sum() + df[col_map['Public transport']].sum() + df[col_map['Taxi']].sum(),
            'Shopping': df[col_map['Shopping']].sum(),
            'Rent': df[col_map['Rent']].sum(),
            'Subscriptions': df[col_map['Subscriptions']].sum(),
            'Eating Out': df[col_map['Eating outside']].sum(),
            'Investments': df[col_map['Investment']].sum(),
            'Travel': df[col_map['Trip expense']].sum() + df[col_map['Trip stay']].sum() + df[col_map['Flight ticket booking']].sum(),
            'Transfers': df[col_map['Money transfer within Germany']].sum() + df[col_map['International transfer']].sum(),
            'Entertainment': df[col_map['Entry tickets']].sum()
        }

        # --- 2. DRAW PIE CHART ---
        if self.canvas: self.canvas.get_tk_widget().destroy()

        labels = [k for k, v in chart_data.items() if v > 0]
        sizes = [v for k, v in chart_data.items() if v > 0]

        if sizes:
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Pastel1.colors)
            ax.set_title(f"Spending: {month}")
            
            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showinfo("Info", "No spending data found for this month.")

        # --- 3. CALCULATE HEALTH SCORE ---
        self.write_health_report(df, col_map, chart_data)

    def write_health_report(self, df, col_map, chart_data):
        """Calculates the score and updates the text box."""
        
        # A. Calculate Key Metrics
        credit = df[col_map['Credit']].sum()
        base_salary = 1234 
        total_income = base_salary + credit
        
        invested = df[col_map['Investment']].sum()
        eating_out = df[col_map['Eating outside']].sum()
        subs = df[col_map['Subscriptions']].sum()
        
        total_outflow = sum(chart_data.values())

        # B. The Game Logic
        score = 0
        feedback = []

        # Metric 1: Investments (Max 40)
        inv_ratio = invested / total_income if  total_income > 0 else 0
        if inv_ratio >= 0.05:
            score += 40
            feedback.append(f"✅ INVESTOR: Saved {inv_ratio:.05%} (>5%)")
        elif invested > 0:
            score += 20
            feedback.append(f"⚠️ STARTER: Saved {inv_ratio:.05%} (Aim for 5%)")
        else:
            feedback.append("❌ MISSED: No investments made.")

        # Metric 2: Dining (Max 30)
        if eating_out <= 100:
            score += 30
            feedback.append(f"✅ DISCIPLINE: Dining €{eating_out:.0f} (<€100)")
        else:
            over = eating_out - 100
            penalty = int(over / 5)
            score += max(0, 30 - penalty)
            feedback.append(f"❌ OVERSPENT: Dining is €{eating_out:.0f}")

        # Metric 3: Subscriptions (Max 30)
        if subs <= 100:
            score += 30
            feedback.append(f"✅ CLEAN: Subs €{subs:.0f} (<€50)")
        else:
            score += 10
            feedback.append(f"⚠️ HEAVY: Subs are €{subs:.0f}")

        # ... inside write_health_report ...

        # C. Update the Text Area
        self.report_text.delete(1.0, tk.END) # Clear previous text
        
        # --- NEW HEADER SECTION ---
        self.report_text.insert(tk.END, f"📊 MONTHLY SUMMARY: {self.selected_month.get()}\n")
        self.report_text.insert(tk.END, "-"*35 + "\n")
        
        # Breakdown of where money came from
        self.report_text.insert(tk.END, f"Base Salary:     €{base_salary:.2f}\n")
        self.report_text.insert(tk.END, f"Extra Credit:    €{credit:.2f}\n")
        self.report_text.insert(tk.END, f"TOTAL INCOME:    €{total_income:.2f}\n")
        self.report_text.insert(tk.END, "-"*35 + "\n")
        
        # Outflow and Net
        self.report_text.insert(tk.END, f"Total Spent:     €{total_outflow:.2f}\n")
        
        # Calculate Real Net Flow (Total Income - Spent)
        net_flow = total_income - total_outflow
        self.report_text.insert(tk.END, f"Net Cash Flow:   €{net_flow:.2f}\n\n")
        
        # Score Visualization
        self.report_text.insert(tk.END, "🏆 FINANCIAL HEALTH SCORE\n")
        self.report_text.insert(tk.END, f"      {score} / 100\n")
        
        bars = int(score / 10)
        health_bar = f"[{'█'*bars}{'░'*(10-bars)}]"
        self.report_text.insert(tk.END, f"{health_bar}\n\n")

        # Rank
        if score >= 90: rank = "GRANDMASTER"
        elif score >= 70: rank = "GOLD"
        elif score >= 50: rank = "SILVER"
        else: rank = "TRY AGAIN"
        self.report_text.insert(tk.END, f"RANK: {rank}\n\n")

        # Details
        self.report_text.insert(tk.END, "📝 ANALYST NOTES:\n")
        for item in feedback:
            self.report_text.insert(tk.END, f"{item}\n")

# --- RUN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()