import tkinter as tk
from tkinter import filedialog, ttk
from datetime import datetime
import pandas as pd
import re

# Variables globales
log_file = ""
lap_penalties = []

# Formats de dates possibles
date_formats = ["[%d/%m/%Y %H:%M:%S]", "[%d-%m-%y %H:%M:%S]"]

def parse_date(date_str):
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def convertir_hhmmss(texte):
    if len(texte) != 6 or not texte.isdigit():
        return None
    return f"{texte[0:2]}:{texte[2:4]}:{texte[4:6]}"

def analyser_log():
    global log_file, lap_penalties

    lap_penalties = []

    if not log_file:
        result_text.insert(tk.END, "❌ Aucun fichier sélectionné.\n")
        return

    # Récupérer heure de début et fin de course depuis l'interface et convertir
    start_time_str_raw = start_time_entry.get()
    end_time_str_raw = end_time_entry.get()

    start_time_str = convertir_hhmmss(start_time_str_raw)
    end_time_str = convertir_hhmmss(end_time_str_raw)

    if not start_time_str or not end_time_str:
        result_text.insert(tk.END, "❌ Format des heures invalide. Utilise HHMMSS ex: 083000\n")
        return

    try:
        today = datetime.today().date()
        start_time = datetime.strptime(f"{today} {start_time_str}", "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(f"{today} {end_time_str}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        result_text.insert(tk.END, "❌ Erreur conversion heures.\n")
        return

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("["):
                date_part = line.split("]")[0] + "]"
                msg_part = line.split("]")[1].strip()
                date_obj = parse_date(date_part)

                if date_obj:
                    # Vérifier si la ligne est dans la plage horaire de la course
                    if start_time <= date_obj <= end_time:
                        # Détection Lap Penalty uniquement sur Line 2
                        if ("LAP PENALTY" in msg_part.upper()) and ("LINE" in msg_part.upper()):
                            # Extraction numéro voiture avec regex
                            match = re.search(r"N°(\d+)", msg_part)
                            numero = match.group(1) if match else "Inconnu"

                            # Nettoyage message : suppression "Line 1 - " ou "Line 2 - "
                            msg_clean = re.sub(r"Line [12] - ", "", msg_part, flags=re.IGNORECASE)

                            lap_penalties.append({
                                "Numero": numero,
                                "Message": msg_clean,
                                "Date": date_obj.strftime("%Y-%m-%d"),
                                "Heure": date_obj.strftime("%H:%M:%S")
                            })

    # Affichage des résultats
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Analyse du fichier : {log_file}\n\n")
    result_text.insert(tk.END, f"Heure de début de course : {start_time_str}\n")
    result_text.insert(tk.END, f"Heure de fin de course : {end_time_str}\n\n")
    result_text.insert(tk.END, f"Nombre total de Lap Penalty (Line 2, pendant la course) : {len(lap_penalties)}\n\n")

    for i, lp in enumerate(lap_penalties, 1):
        result_text.insert(tk.END, f"{i}. N°{lp['Numero']} | {lp['Date']} {lp['Heure']} | {lp['Message']}\n")


def choisir_fichier():
    global log_file
    f = filedialog.askopenfilename(
        title="Choisir le fichier .log",
        filetypes=(("Fichiers log", "*.log"), ("Tous les fichiers", "*.*"))
    )
    if f:
        log_file = f
        result_text.insert(tk.END, f"✅ Fichier sélectionné : {log_file}\n")

def sauvegarder_excel():
    if not lap_penalties:
        result_text.insert(tk.END, "❌ Aucun Lap Penalty à sauvegarder.\n")
        return

    df = pd.DataFrame(lap_penalties)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"LapPenalty_{now}.xlsx"
    df.to_excel(filename, index=False)

    result_text.insert(tk.END, f"\n✅ Résultats sauvegardés dans : {filename}\n")

# ----- GUI avec Tkinter -----

root = tk.Tk()
root.title("Analyseur Lap Penalty (Log) ➔ Excel")

root.geometry("800x600")

# Bouton choisir fichier
choose_button = ttk.Button(root, text="Choisir fichier .log", command=choisir_fichier)
choose_button.pack(pady=5)

# Entrée heure de début
start_time_label = ttk.Label(root, text="Heure de début de course (ex: 083000) :")
start_time_label.pack()
start_time_entry = ttk.Entry(root)
start_time_entry.pack()

# Entrée heure de fin
end_time_label = ttk.Label(root, text="Heure de fin de course (ex: 165300) :")
end_time_label.pack()
end_time_entry = ttk.Entry(root)
end_time_entry.pack()

# Bouton analyser
analyse_button = ttk.Button(root, text="Analyser le log", command=analyser_log)
analyse_button.pack(pady=5)

# Zone de texte pour afficher les résultats
result_text = tk.Text(root, height=20)
result_text.pack(pady=5)

# Bouton sauvegarder Excel
save_excel_button = ttk.Button(root, text="Sauvegarder en Excel", command=sauvegarder_excel)
save_excel_button.pack(pady=5)

root.mainloop()
