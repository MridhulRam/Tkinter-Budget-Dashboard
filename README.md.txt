# 💰 Python Financial Dashboard

An interactive desktop application built with Python and Tkinter that analyzes monthly spending from an Excel spreadsheet and calculates a "Financial Health Score."

## Features
* **Automated Data Cleaning:** Reads and standardizes Excel data using Pandas.
* **Interactive UI:** Select different months via a Tkinter dropdown menu.
* **Visual Analytics:** Automatically generates Matplotlib pie charts of monthly outflow.
* **Gamified Health Score:** Calculates a score (0-100) based on savings rate, vice spending, and subscription costs.

## How to Run
1. Clone this repository.
2. Install the required libraries: `pip install -r requirements.txt`
3. Place a file named `sample_data.xlsx` in the same folder.
4. Run `python interactive budget.py`.