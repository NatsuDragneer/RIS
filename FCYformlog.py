import tkinter as tk
from tkinter import filedialog, ttk
from datetime import datetime, timedelta

# Variables globales
total_fcy_count = 0
currently_in_fcy = False
fcy_start_time = None
fcy_durations = []
total_fcy_duration = timedelta()
log_file = ""

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
    """
    Convertit un string du type HHMMSS en HH:MM:SS
    Exemple : '165300' -> '16:53:00'
    """
    if len(texte) != 6 or not texte.isdigit():
        return None
    return f"{texte[0:2]}:{texte[2:4]}:{texte[4:6]}"

def analyser_log():
    global total_fcy_count, currently_in_fcy, fcy_start_time, fcy_durations, total_fcy_duration, log_file

    # Reset des variables
    total_fcy_count = 0
    currently_in_fcy = False
    fcy_start_time = None
    fcy_durations = []
    total_fcy_duration = timedelta()

    if not log_file:
        result_text.insert(tk.END, "❌ Aucun fichier sélectionné.\n")
        return

    # Conversion heures de début et fin
    start_time_str_raw = start_time_entry.get()
    end_time_str_raw = end_time_entry.get()

    start_time_str = convertir_hhmmss(start_time_str_raw)
    end_time_str = convertir_hhmmss(end_time_str_raw)

    if not start_time_str or not end_time_str:
        result_text.insert(tk.END, "❌ Format des heures invalide. Utilise HHMMSS ex: 083000\n")
        return

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("["):
                date_part = line.split("]")[0] + "]"
                msg_part = line.split("]")[1].strip()
                date_obj = parse_date(date_part)

                if date_obj:
                    # Détection FCY
                    if ("FCY REGULATION" in msg_part) or ("FULL COURSE YELLOW" in msg_part):
                        if not currently_in_fcy:
                            total_fcy_count += 1
                            currently_in_fcy = True
                            fcy_start_time = date_obj

                    # Détection GREEN FLAG
                    if "GREEN FLAG" in msg_part:
                        if currently_in_fcy:
                            fcy_end_time = date_obj
                            duration = fcy_end_time - fcy_start_time
                            fcy_durations.append((fcy_start_time, fcy_end_time, duration))
                            total_fcy_duration += duration
                            currently_in_fcy = False
                            fcy_start_time = None

    # Affichage des résultats
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Analyse du fichier : {log_file}\n\n")
    result_text.insert(tk.END, f"Heure de début de course : {start_time_str}\n")
    result_text.insert(tk.END, f"Heure de fin de course : {end_time_str}\n\n")
    result_text.insert(tk.END, f"Nombre total de FCY : {total_fcy_count}\n")
    result_text.insert(tk.END, f"Durée totale de tous les FCY : {str(total_fcy_duration).split('.')[0]}\n\n")

    for i, (start, end, dur) in enumerate(fcy_durations, 1):
        result_text.insert(tk.END, f"FCY {i} : {start} ➔ {end} | Durée : {str(dur).split('.')[0]}\n")

def choisir_fichier():
    global log_file
    f = filedialog.askopenfilename(
        title="Choisir le fichier .log",
        filetypes=(("Fichiers log", "*.log"), ("Tous les fichiers", "*.*"))
    )
    if f:
        log_file = f
        result_text.insert(tk.END, f"✅ Fichier sélectionné : {log_file}\n")

def sauvegarder_resultats():
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"resultats_FCY_log_{now}.txt"

    start_time_str = convertir_hhmmss(start_time_entry.get())
    end_time_str = convertir_hhmmss(end_time_entry.get())

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Analyse du fichier : {log_file}\n")
        f.write(f"Date de sauvegarde : {now}\n\n")
        f.write(f"Heure de début de course : {start_time_str}\n")
        f.write(f"Heure de fin de course : {end_time_str}\n\n")
        f.write(f"Nombre total de FCY : {total_fcy_count}\n")
        f.write(f"Durée totale de tous les FCY : {str(total_fcy_duration).split('.')[0]}\n\n")

        for i, (start, end, dur) in enumerate(fcy_durations, 1):
            f.write(f"FCY {i} : {start} ➔ {end} | Durée : {str(dur).split('.')[0]}\n")

    result_text.insert(tk.END, f"\n✅ Résultats sauvegardés dans : {filename}\n")

# ----- GUI avec Tkinter -----

root = tk.Tk()
root.title("Analyseur FCY (Log)")

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

# Bouton sauvegarder
save_button = ttk.Button(root, text="Sauvegarder les résultats", command=sauvegarder_resultats)
save_button.pack(pady=5)

root.mainloop()
