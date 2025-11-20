"""
COVID-19 Diagnosis Expert System
A rule-based expert system using CLIPS (clipspy) for COVID-19 symptom diagnosis
with a tkinter GUI interface.
"""

import os
import sys

# Fix tkinter Tcl/Tk path issues on Windows with virtual environments
if sys.platform == "win32" and hasattr(sys, 'base_prefix'):
    # Get the base Python installation path
    base_python = sys.base_prefix
    tcl_path = os.path.join(base_python, 'tcl')
    
    # Set Tcl/Tk environment variables if not already set
    if os.path.exists(tcl_path) and 'TCL_LIBRARY' not in os.environ:
        # Find tcl8.6 directory
        tcl_dirs = [d for d in os.listdir(tcl_path) if d.startswith('tcl8')]
        tk_dirs = [d for d in os.listdir(tcl_path) if d.startswith('tk8')]
        
        if tcl_dirs:
            os.environ['TCL_LIBRARY'] = os.path.join(tcl_path, tcl_dirs[0])
        if tk_dirs:
            os.environ['TK_LIBRARY'] = os.path.join(tcl_path, tk_dirs[0])

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import clips


class CovidExpertSystem:
    """COVID-19 Expert System using CLIPS"""
    
    def __init__(self):
        self.env = clips.Environment()
        self.setup_rules()
    
    def setup_rules(self):
        """Define the knowledge base with rules for COVID-19 diagnosis"""
        
        # Define templates for facts
        self.env.build("(deftemplate patient (slot name (type STRING)) (slot fever (type SYMBOL) (allowed-symbols yes no)) (slot cough (type SYMBOL) (allowed-symbols yes no)) (slot breathing-difficulty (type SYMBOL) (allowed-symbols yes no)) (slot fatigue (type SYMBOL) (allowed-symbols yes no)) (slot loss-of-taste-smell (type SYMBOL) (allowed-symbols yes no)) (slot contact-with-positive (type SYMBOL) (allowed-symbols yes no)))")
        
        self.env.build("(deftemplate diagnosis (slot patient-name (type STRING)) (slot result (type STRING)) (slot recommendation (type STRING)) (slot risk-level (type SYMBOL) (allowed-symbols low medium high critical)))")
        
        # Rule 1: Critical Case Detection - Most severe, checked first
        # If patient has fever + cough + breathing difficulty + fatigue
        self.env.build("""
(defrule critical-case
    "Detects critical cases requiring immediate medical attention"
    (patient 
        (name ?name)
        (fever yes)
        (cough yes)
        (breathing-difficulty yes)
        (fatigue yes))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "CRITICAL - Severe COVID-19 Symptoms")
        (recommendation "EMERGENCY: Seek immediate medical attention. Call emergency services. Severe respiratory distress detected.")
        (risk-level critical))))
""")
        
        # Rule 2: High Risk COVID-19 - Breathing difficulty variant
        # If patient has fever + cough + breathing difficulty (but not all 4 critical symptoms)
        self.env.build("""
(defrule high-risk-covid-breathing
    "Detects high-risk COVID-19 cases with breathing issues"
    (patient 
        (name ?name)
        (fever yes)
        (cough yes)
        (breathing-difficulty yes))
    (not (diagnosis (patient-name ?name) (risk-level critical)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "HIGH RISK for COVID-19")
        (recommendation "URGENT: Get PCR test immediately. Self-isolate. Contact healthcare provider. Monitor oxygen levels.")
        (risk-level high))))
""")
        
        # Rule 3: High Risk COVID-19 - Loss of taste/smell variant
        # If patient has fever + cough + loss of taste/smell
        self.env.build("""
(defrule high-risk-covid-taste-smell
    "Detects high-risk COVID-19 cases with loss of taste or smell"
    (patient 
        (name ?name)
        (fever yes)
        (cough yes)
        (loss-of-taste-smell yes))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "HIGH RISK for COVID-19")
        (recommendation "URGENT: Get PCR test immediately. Self-isolate. Contact healthcare provider. Monitor symptoms closely.")
        (risk-level high))))
""")
        
        # Rule 4: Medium Risk - Fever and fatigue
        self.env.build("""
(defrule medium-risk-fever-fatigue
    "Detects medium-risk cases with fever and fatigue"
    (patient 
        (name ?name)
        (fever yes)
        (fatigue yes))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "MEDIUM RISK for COVID-19")
        (recommendation "Get tested for COVID-19. Self-monitor symptoms. Avoid contact with others. Rest and stay hydrated.")
        (risk-level medium))))
""")
        
        # Rule 5: Medium Risk - Cough and fatigue
        self.env.build("""
(defrule medium-risk-cough-fatigue
    "Detects medium-risk cases with cough and fatigue"
    (patient 
        (name ?name)
        (cough yes)
        (fatigue yes))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "MEDIUM RISK for COVID-19")
        (recommendation "Get tested for COVID-19. Self-monitor symptoms. Avoid contact with others. Rest and stay hydrated.")
        (risk-level medium))))
""")
        
        # Rule 6: Medium Risk - Contact with positive case and fever
        self.env.build("""
(defrule medium-risk-contact-fever
    "Detects medium-risk cases with contact history and fever"
    (patient 
        (name ?name)
        (contact-with-positive yes)
        (fever yes))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "MEDIUM RISK for COVID-19")
        (recommendation "Get tested for COVID-19 due to exposure. Self-isolate until test results. Monitor symptoms daily.")
        (risk-level medium))))
""")
        
        # Rule 7: Medium Risk - Contact with positive case and cough
        self.env.build("""
(defrule medium-risk-contact-cough
    "Detects medium-risk cases with contact history and cough"
    (patient 
        (name ?name)
        (contact-with-positive yes)
        (cough yes))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "MEDIUM RISK for COVID-19")
        (recommendation "Get tested for COVID-19 due to exposure. Self-isolate until test results. Monitor symptoms daily.")
        (risk-level medium))))
""")
        
        # Rule 8: Low Risk Assessment - Default rule
        self.env.build("""
(defrule low-risk-assessment
    "Provides assessment for low-risk cases"
    (patient (name ?name))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "LOW RISK for COVID-19")
        (recommendation "Symptoms appear mild. Continue monitoring. Practice good hygiene. Consult doctor if symptoms worsen.")
        (risk-level low))))
""")
    
    def diagnose(self, patient_data):
        """
        Run diagnosis on patient data
        
        Args:
            patient_data: Dictionary containing patient information and symptoms
            
        Returns:
            Dictionary with diagnosis results
        """
        # Reset the environment
        self.env.reset()
        
        # Assert patient facts
        fact_string = f"""(patient
            (name "{patient_data['name']}")
            (fever {patient_data['fever']})
            (cough {patient_data['cough']})
            (breathing-difficulty {patient_data['breathing_difficulty']})
            (fatigue {patient_data['fatigue']})
            (loss-of-taste-smell {patient_data['loss_of_taste_smell']})
            (contact-with-positive {patient_data['contact_with_positive']})
        )"""
        
        self.env.assert_string(fact_string)
        
        # Run the rules
        self.env.run()
        
        # Extract diagnosis
        results = []
        for fact in self.env.facts():
            if fact.template.name == 'diagnosis':
                results.append({
                    'patient_name': fact['patient-name'],
                    'result': fact['result'],
                    'recommendation': fact['recommendation'],
                    'risk_level': str(fact['risk-level'])
                })
        
        return results[0] if results else {
            'patient_name': patient_data['name'],
            'result': 'Unable to diagnose',
            'recommendation': 'Please consult a healthcare professional',
            'risk_level': 'unknown'
        }


class CovidDiagnosisGUI:
    """Tkinter GUI for COVID-19 Expert System"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("COVID-19 Diagnosis Expert System")
        self.root.geometry("700x800")
        self.root.resizable(False, False)
        
        # Initialize expert system
        self.expert_system = CovidExpertSystem()
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="COVID-19 Diagnosis Expert System",
            font=('Arial', 18, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="Please answer the following questions about your symptoms",
            font=('Arial', 10)
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Patient Name
        ttk.Label(main_frame, text="Patient Name:", font=('Arial', 11, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.name_entry = ttk.Entry(main_frame, width=30, font=('Arial', 10))
        self.name_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Symptom questions
        self.symptom_vars = {}
        symptoms = [
            ("fever", "Do you have fever (≥37.8°C/100°F)?"),
            ("cough", "Do you have a persistent cough?"),
            ("breathing_difficulty", "Do you have difficulty breathing or shortness of breath?"),
            ("fatigue", "Are you experiencing unusual tiredness or fatigue?"),
            ("loss_of_taste_smell", "Have you lost your sense of taste or smell?"),
            ("contact_with_positive", "Have you been in close contact with a confirmed COVID-19 case?")
        ]
        
        row = 3
        for key, question in symptoms:
            ttk.Label(main_frame, text=question, font=('Arial', 10)).grid(
                row=row, column=0, sticky=tk.W, pady=10, columnspan=2
            )
            row += 1
            
            var = tk.StringVar(value="no")
            self.symptom_vars[key] = var
            
            frame = ttk.Frame(main_frame)
            frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
            
            ttk.Radiobutton(frame, text="Yes", variable=var, value="yes").pack(side=tk.LEFT, padx=(20, 10))
            ttk.Radiobutton(frame, text="No", variable=var, value="no").pack(side=tk.LEFT)
            
            row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        self.diagnose_btn = ttk.Button(
            button_frame,
            text="Get Diagnosis",
            command=self.run_diagnosis,
            width=20
        )
        self.diagnose_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = ttk.Button(
            button_frame,
            text="Reset Form",
            command=self.reset_form,
            width=20
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        row += 1
        
        # Results area
        ttk.Label(main_frame, text="Diagnosis Results:", font=('Arial', 12, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5)
        )
        row += 1
        
        self.results_text = scrolledtext.ScrolledText(
            main_frame,
            width=70,
            height=12,
            font=('Arial', 10),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.results_text.grid(row=row, column=0, columnspan=2, pady=(0, 10))
        
        # Configure text tags for colored output
        self.results_text.tag_config('critical', foreground='red', font=('Arial', 11, 'bold'))
        self.results_text.tag_config('high', foreground='orangered', font=('Arial', 11, 'bold'))
        self.results_text.tag_config('medium', foreground='orange', font=('Arial', 11, 'bold'))
        self.results_text.tag_config('low', foreground='green', font=('Arial', 11, 'bold'))
        self.results_text.tag_config('bold', font=('Arial', 10, 'bold'))
        
        # Disclaimer
        row += 1
        disclaimer = ttk.Label(
            main_frame,
            text="⚠ Disclaimer: This is an educational tool. Always consult healthcare professionals for medical advice.",
            font=('Arial', 9, 'italic'),
            foreground='gray',
            wraplength=650
        )
        disclaimer.grid(row=row, column=0, columnspan=2, pady=(10, 0))
    
    def run_diagnosis(self):
        """Run the expert system diagnosis"""
        # Validate input
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter patient name")
            return
        
        # Collect patient data
        patient_data = {
            'name': name,
            'fever': self.symptom_vars['fever'].get(),
            'cough': self.symptom_vars['cough'].get(),
            'breathing_difficulty': self.symptom_vars['breathing_difficulty'].get(),
            'fatigue': self.symptom_vars['fatigue'].get(),
            'loss_of_taste_smell': self.symptom_vars['loss_of_taste_smell'].get(),
            'contact_with_positive': self.symptom_vars['contact_with_positive'].get()
        }
        
        # Run diagnosis
        try:
            diagnosis = self.expert_system.diagnose(patient_data)
            self.display_results(diagnosis)
        except Exception as e:
            messagebox.showerror("Error", f"Diagnosis failed: {str(e)}")
    
    def display_results(self, diagnosis):
        """Display diagnosis results in the text area"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Format output
        self.results_text.insert(tk.END, "=" * 70 + "\n")
        self.results_text.insert(tk.END, f"Patient: {diagnosis['patient_name']}\n\n", 'bold')
        
        # Add result with appropriate color
        risk_level = diagnosis['risk_level']
        self.results_text.insert(tk.END, "Diagnosis: ", 'bold')
        self.results_text.insert(tk.END, f"{diagnosis['result']}\n\n", risk_level)
        
        # Add recommendation
        self.results_text.insert(tk.END, "Recommendation:\n", 'bold')
        self.results_text.insert(tk.END, f"{diagnosis['recommendation']}\n\n")
        
        # Add risk level
        self.results_text.insert(tk.END, "Risk Level: ", 'bold')
        self.results_text.insert(tk.END, f"{risk_level.upper()}\n", risk_level)
        
        self.results_text.insert(tk.END, "=" * 70 + "\n")
        
        self.results_text.config(state=tk.DISABLED)
    
    def reset_form(self):
        """Reset all form fields"""
        self.name_entry.delete(0, tk.END)
        for var in self.symptom_vars.values():
            var.set("no")
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = CovidDiagnosisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
