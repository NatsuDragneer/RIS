import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox
from openpyxl import Workbook

def analyser_voitures(file_path):
    df = pd.read_csv(file_path, sep=';')
    df.columns = [
        'Index', 'Type', 'CarNumber', 'Time', 'Zero1', 'NaN1', 'Zero2', 'MaxTime', 'Zero3', 'Date'
    ]

    # Conversion de la colonne Date
    df['Date'] = pd.to_datetime(df['Date'], format='%y-%m-%d %H:%M')

    # Conversion de Time en timedelta
    df['Time_td'] = pd.to_timedelta(df['Time'])

    # Création de DateTime finale (si Time est utile, ajouter + Time_td)
    df['DateTime'] = df['Date']

    car_passage_counts = {}

    for car in df['CarNumber'].unique():
        car_df = df[df['CarNumber'] == car].sort_values('DateTime')

        valid_passages = []
        last_time = None

        for _, row in car_df.iterrows():
            current_time = row['DateTime']

            if last_time is None:
                valid_passages.append(current_time)
                last_time = current_time
            else:
                if current_time - last_time >= timedelta(minutes=15):
                    valid_passages.append(current_time)
                    last_time = current_time

        car_passage_counts[car] = len(valid_passages)

    good = {car: count for car, count in car_passage_counts.items() if count >= 18}
    not_good = {car: count for car, count in car_passage_counts.items() if count < 18}

    return good, not_good

def ouvrir_fichier():
    file_path = filedialog.askopenfilename(title="Sélectionne le fichier CSV", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    good, not_good = analyser_voitures(file_path)

    # Affichage GUI
    listbox_good.delete(0, tk.END)
    listbox_not_good.delete(0, tk.END)

    for car, count in sorted(good.items()):
        listbox_good.insert(tk.END, f"{car} : {count}")

    for car, count in sorted(not_good.items()):
        listbox_not_good.insert(tk.END, f"{car} : {count}")

    # Stocker pour l'export
    global export_data
    export_data = {'good': good, 'not_good': not_good}

def exporter_xlsx():
    if not export_data:
        messagebox.showerror("Erreur", "Aucune donnée à exporter.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if not save_path:
        return

    wb = Workbook()
    ws_good = wb.active
    ws_good.title = "Good"

    ws_good.append(["CarNumber", "PassageCount"])
    for car, count in export_data['good'].items():
        ws_good.append([car, count])

    ws_not_good = wb.create_sheet(title="Not Good")
    ws_not_good.append(["CarNumber", "PassageCount"])
    for car, count in export_data['not_good'].items():
        ws_not_good.append([car, count])

    wb.save(save_path)
    messagebox.showinfo("Export", f"Exporté avec succès vers {save_path}")

# 🖥️ GUI Tkinter
root = tk.Tk()
root.title("Analyse voitures")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

btn_open = tk.Button(frame, text="📂 Ouvrir fichier CSV", command=ouvrir_fichier)
btn_open.grid(row=0, column=0, columnspan=2, pady=5)

# Colonnes Good et Pas Good
tk.Label(frame, text="✅ Good (>=18)").grid(row=1, column=0)
tk.Label(frame, text="❌ Pas Good (<18)").grid(row=1, column=1)

listbox_good = tk.Listbox(frame, width=30)
listbox_good.grid(row=2, column=0, padx=5, pady=5)

listbox_not_good = tk.Listbox(frame, width=30)
listbox_not_good.grid(row=2, column=1, padx=5, pady=5)

# Bouton Export
btn_export = tk.Button(frame, text="💾 Exporter en XLSX", command=exporter_xlsx)
btn_export.grid(row=3, column=0, columnspan=2, pady=10)

export_data = None

root.mainloop()
