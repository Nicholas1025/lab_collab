import tkinter as tk
from tkinter import messagebox
from clips import Environment

# --------------------------
# 1. Create Environment
# --------------------------
env = Environment()

# --------------------------
# 2. Load CLIPS Rules SAFELY
# --------------------------
# Template
env.build("(deftemplate symptom (slot name) (slot value))")

# Rule 1
env.build(
    "(defrule covid-rule "
    "(symptom (name fever) (value yes)) "
    "(symptom (name cough) (value yes)) "
    "=> "
    "(assert (diagnosis covid))"
    ")"
)

# Rule 2
env.build(
    "(defrule healthy-rule "
    "(symptom (name fever) (value no)) "
    "(symptom (name cough) (value no)) "
    "=> "
    "(assert (diagnosis healthy))"
    ")"
)

# --------------------------
# 3. Tkinter GUI
# --------------------------
root = tk.Tk()
root.title("COVID-19 Diagnosis Expert System")
root.geometry("380x300")

tk.Label(root, text="COVID-19 Simple Expert System", font=("Arial", 14)).pack(pady=10)

tk.Label(root, text="Do you have fever?").pack()
fever_var = tk.StringVar(value="no")
tk.OptionMenu(root, fever_var, "yes", "no").pack()

tk.Label(root, text="Do you have cough?").pack()
cough_var = tk.StringVar(value="no")
tk.OptionMenu(root, cough_var, "yes", "no").pack()

# --------------------------
# 4. Inference Function
# --------------------------
def run_system():
    env.reset()

    env.assert_string(f"(symptom (name fever) (value {fever_var.get()}))")
    env.assert_string(f"(symptom (name cough) (value {cough_var.get()}))")

    env.run()

    diagnosis = None

    for fact in env.facts():
        # Look for implied fact (diagnosis xxx)
        if fact.template.name == "diagnosis":
            diagnosis = fact[0]   # <-- FIXED

    if diagnosis == "covid":
        messagebox.showinfo("Diagnosis Result", "⚠ Possible COVID-19 infection.")
    elif diagnosis == "healthy":
        messagebox.showinfo("Diagnosis Result", "✔ You appear healthy.")
    else:
        messagebox.showinfo("Diagnosis Result", "No diagnosis.")


tk.Button(root, text="Diagnose", command=run_system, font=("Arial", 12)).pack(pady=20)

root.mainloop()
