import tkinter as tk
from tkinter import filedialog, ttk
from datetime import datetime, timedelta
import pandas as pd
import re
import os

# ------ Variables globales ------
log_file_1 = ""
log_file_2 = ""

# FCY variables
total_fcy_count = 0
fcy_durations = []
total_fcy_duration = timedelta()

# Lap Penalty variables
lap_penalties = []

# Formats de dates dans le log
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

def analyser_fcy(log_file, start_time, end_time):
    global total_fcy_count, fcy_durations, total_fcy_duration
    currently_in_fcy = False
    fcy_start_time = None

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("["):
                date_part = line.split("]")[0] + "]"
                msg_part = line.split("]")[1].strip()
                date_obj = parse_date(date_part)

                if date_obj and start_time <= date_obj <= end_time:
                    if ("FCY REGULATION" in msg_part) or ("FULL COURSE YELLOW" in msg_part):
                        if not currently_in_fcy:
                            total_fcy_count += 1
                            currently_in_fcy = True
                            fcy_start_time = date_obj

                    if "GREEN FLAG" in msg_part:
                        if currently_in_fcy:
                            fcy_end_time = date_obj
                            duration = fcy_end_time - fcy_start_time
                            fcy_durations.append({
                                "Start": fcy_start_time,
                                "End": fcy_end_time,
                                "Duration": str(duration).split('.')[0]
                            })
                            total_fcy_duration += duration
                            currently_in_fcy = False
                            fcy_start_time = None

def analyser_lap_penalty(log_file, start_time, end_time):
    global lap_penalties

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("["):
                date_part = line.split("]")[0] + "]"
                msg_part = line.split("]")[1].strip()
                date_obj = parse_date(date_part)

                if date_obj and start_time <= date_obj <= end_time:
                    if ("LAP PENALTY" in msg_part.upper()) and ("LINE" in msg_part.upper()):
                        match = re.search(r"N°(\d+)", msg_part)
                        numero = match.group(1) if match else "Inconnu"
                        msg_clean = re.sub(r"Line [12] - ", "", msg_part, flags=re.IGNORECASE)
                        lap_penalties.append({
                            "Numero": numero,
                            "Message": msg_clean,
                            "Date": date_obj.strftime("%Y-%m-%d"),
                            "Heure": date_obj.strftime("%H:%M:%S")
                        })

def save_fcy_excel(epreuve_name):
    if not fcy_durations:
        result_text.insert(tk.END, "❌ Aucun FCY à sauvegarder.\n")
        return

    df = pd.DataFrame(fcy_durations)

    # ➕ Calculer la durée totale cumulée
    total_seconds = sum([
        (datetime.strptime(row['Duration'], "%H:%M:%S") - datetime.strptime("00:00:00", "%H:%M:%S")).total_seconds()
        for _, row in df.iterrows()
    ])
    total_duration = str(timedelta(seconds=int(total_seconds)))

    # ➕ Ajouter une ligne "TOTAL"
    df = pd.concat([df, pd.DataFrame([{
        "Start": "TOTAL",
        "End": "",
        "Duration": total_duration
    }])], ignore_index=True)

    # ➕ Sauvegarder dans dossier FCY_exports
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = "./FCY_exports"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/FCY_{epreuve_name}_{now}.xlsx"
    df.to_excel(filename, index=False)
    result_text.insert(tk.END, f"✅ FCY sauvegardé : {filename} (Durée totale : {total_duration})\n")


def save_lap_penalty_excel(epreuve_name):
    if not lap_penalties:
        result_text.insert(tk.END, "❌ Aucun Lap Penalty à sauvegarder.\n")
        return

    df = pd.DataFrame(lap_penalties)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = "./LapPenalty_exports"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/LapPenalty_{epreuve_name}_{now}.xlsx"
    df.to_excel(filename, index=False)
    result_text.insert(tk.END, f"✅ Lap Penalty sauvegardé : {filename}\n")

def analyser_log():
    if not log_file_1:
        result_text.insert(tk.END, "❌ Choisis au moins un fichier log.\n")
        return

    epreuve_name = epreuve_entry.get()
    if not epreuve_name:
        result_text.insert(tk.END, "❌ Entre le nom de l'épreuve.\n")
        return

    heure_deb = convertir_hhmmss(heure_deb_entry.get())
    heure_fin = convertir_hhmmss(heure_fin_entry.get())

    if not heure_deb or not heure_fin:
        result_text.insert(tk.END, "❌ Heures invalides.\n")
        return

    global total_fcy_count, fcy_durations, total_fcy_duration, lap_penalties
    total_fcy_count = 0
    fcy_durations = []
    total_fcy_duration = timedelta()
    lap_penalties = []

    result_text.delete(1.0, tk.END)

    # Date start log1
    with open(log_file_1, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("["):
                date_part = line.split("]")[0] + "]"
                date_deb = parse_date(date_part)
                break

    if not date_deb:
        result_text.insert(tk.END, "❌ Impossible de lire la date du log 1.\n")
        return

    start_time = datetime.strptime(f"{date_deb.date()} {heure_deb}", "%Y-%m-%d %H:%M:%S")

    # Date end log2
    if log_file_2:
        with open(log_file_2, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("["):
                    date_part = line.split("]")[0] + "]"
                    date_fin = parse_date(date_part)
                    break

        if not date_fin:
            result_text.insert(tk.END, "❌ Impossible de lire la date du log 2.\n")
            return

        end_time = datetime.strptime(f"{date_fin.date()} {heure_fin}", "%Y-%m-%d %H:%M:%S")
    else:
        end_time = datetime.strptime(f"{date_deb.date()} {heure_fin}", "%Y-%m-%d %H:%M:%S")

    full_time = end_time - start_time

    if mode_selectionne.get() == "FCY":
        if log_file_2:
            analyser_fcy(log_file_1, start_time, datetime.strptime(f"{date_deb.date()} 23:59:59", "%Y-%m-%d %H:%M:%S"))
            analyser_fcy(log_file_2, datetime.strptime(f"{date_fin.date()} 00:00:00", "%Y-%m-%d %H:%M:%S"), end_time)
        else:
            analyser_fcy(log_file_1, start_time, end_time)

        result_text.insert(tk.END, f"✅ FCY total : {total_fcy_count}\n")
        result_text.insert(tk.END, f"Durée totale FCY : {str(total_fcy_duration).split('.')[0]}\n")
        result_text.insert(tk.END, f"Durée totale course : {str(full_time).split('.')[0]}\n\n")
        for i, fcy in enumerate(fcy_durations, 1):
            result_text.insert(tk.END, f"FCY {i} : {fcy['Start']} ➜ {fcy['End']} | Durée : {fcy['Duration']}\n")
        save_fcy_excel(epreuve_name)

    else:
        if log_file_2:
            analyser_lap_penalty(log_file_1, start_time, datetime.strptime(f"{date_deb.date()} 23:59:59", "%Y-%m-%d %H:%M:%S"))
            analyser_lap_penalty(log_file_2, datetime.strptime(f"{date_fin.date()} 00:00:00", "%Y-%m-%d %H:%M:%S"), end_time)
        else:
            analyser_lap_penalty(log_file_1, start_time, end_time)

        result_text.insert(tk.END, f"✅ Total Lap Penalty : {len(lap_penalties)}\n")
        result_text.insert(tk.END, f"Durée totale course : {str(full_time).split('.')[0]}\n\n")
        for i, lp in enumerate(lap_penalties, 1):
            result_text.insert(tk.END, f"{i}. {lp['Date']} {lp['Heure']} - N°{lp['Numero']} ➜ {lp['Message']}\n")
        save_lap_penalty_excel(epreuve_name)


def choisir_fichier1():
    global log_file_1
    f = filedialog.askopenfilename(title="Fichier log Jour 1", filetypes=(("Log", "*.log"),))
    if f:
        log_file_1 = f
        result_text.insert(tk.END, f"✅ Jour 1 : {log_file_1}\n")

def choisir_fichier2():
    global log_file_2
    f = filedialog.askopenfilename(title="Fichier log Jour 2", filetypes=(("Log", "*.log"),))
    if f:
        log_file_2 = f
        result_text.insert(tk.END, f"✅ Jour 2 : {log_file_2}\n")

root = tk.Tk()
root.title("Analyseur Log FCY/Lap Penalty ➔ Excel")
root.geometry("950x800")

mode_selectionne = tk.StringVar(value="FCY")

ttk.Label(root, text="Nom de l'épreuve :").pack()
epreuve_entry = ttk.Entry(root)
epreuve_entry.pack()

ttk.Label(root, text="Mode d'analyse :").pack()
ttk.Radiobutton(root, text="FCY", variable=mode_selectionne, value="FCY").pack()
ttk.Radiobutton(root, text="Lap Penalty", variable=mode_selectionne, value="Penalty").pack()

ttk.Button(root, text="Choisir log Jour 1", command=choisir_fichier1).pack(pady=5)
ttk.Button(root, text="Choisir log Jour 2 (optionnel)", command=choisir_fichier2).pack(pady=5)

ttk.Label(root, text="Heure début (ex: 165300)").pack()
heure_deb_entry = ttk.Entry(root)
heure_deb_entry.pack()

ttk.Label(root, text="Heure fin (ex: 175300)").pack()
heure_fin_entry = ttk.Entry(root)
heure_fin_entry.pack()

ttk.Button(root, text="Analyser et Sauvegarder", command=analyser_log).pack(pady=10)

result_text = tk.Text(root, height=30)
result_text.pack(pady=5)

root.mainloop()
