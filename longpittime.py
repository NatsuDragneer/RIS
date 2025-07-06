import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import scrolledtext
import time
import threading
from plyer import notification  # pip install plyer

# ===========================
# CONFIGURATION DU SCRIPT
# ===========================

xml_file = r"C:\RIS\xml\live.xml"
BOX_LONG_THRESHOLD = 7200  # 2h en secondes
SCAN_INTERVAL = 1  # intervalle de scan en secondes

# ===========================
# FONCTION DE CONVERSION hh:mm:ss -> secondes
# ===========================
def convert_hhmmss_to_seconds(time_str):
    try:
        parts = time_str.strip().split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h)*3600 + int(m)*60 + int(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m)*60 + int(s)
        else:
            return float(time_str.replace(",", "."))
    except Exception as e:
        print(f"❌ Erreur conversion '{time_str}': {e}")
        return 0

# ===========================
# FONCTION DE CONVERSION secondes -> hh:mm:ss
# ===========================
def seconds_to_hhmmss(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# ===========================
# FONCTION DE NOTIFICATION
# ===========================
def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=5  # affiché pendant 5 sec
    )

# ===========================
# FONCTION DE DETECTION
# ===========================
def detect_box_long(gui_output, pitlong_output, detected_pitlongs):
    while True:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            found_long_pit = False

            for vehicle in root.findall(".//lineinfo"):
                car_number_elem = vehicle.find("numero")
                car_number = car_number_elem.text if car_number_elem is not None else "Inconnu"

                pit_time_elem = vehicle.find("time_stop")
                pit_time_str = pit_time_elem.text if pit_time_elem is not None else ""

                if pit_time_str and pit_time_str != ".":
                    pit_time = convert_hhmmss_to_seconds(pit_time_str)

                    if pit_time > BOX_LONG_THRESHOLD:
                        found_long_pit = True

                        if car_number not in detected_pitlongs:
                            # Convertir en hh:mm:ss pour affichage
                            pit_time_hms = seconds_to_hhmmss(pit_time)
                            msg = f"🚨 Box long détecté pour voiture #{car_number} : {pit_time_hms} (hh:mm:ss)"
                            gui_output.insert(tk.END, msg + "\n")
                            gui_output.see(tk.END)
                            pitlong_output.insert(tk.END, msg + "\n")
                            pitlong_output.see(tk.END)
                            send_notification("Pit Long Detecté", msg)
                            detected_pitlongs.add(car_number)
                        else:
                            # Déjà détecté, ne pas réafficher mais garde found_long_pit à True
                            pass

            # Log scan à chaque boucle
            gui_output.insert(tk.END, f"{time.strftime('%H:%M:%S')} : Scan effectué\n")
            gui_output.see(tk.END)

        except Exception as e:
            gui_output.insert(tk.END, f"❌ Erreur : {e}\n")
            gui_output.see(tk.END)

        time.sleep(SCAN_INTERVAL)

# ===========================
# FONCTION POUR THREADING
# ===========================
def start_detection_thread(gui_output, pitlong_output):
    detected_pitlongs = set()  # mémorise les pit long déjà détectés
    t = threading.Thread(target=detect_box_long, args=(gui_output, pitlong_output, detected_pitlongs), daemon=True)
    t.start()

# ===========================
# GUI PRINCIPALE
# ===========================
def create_gui():
    window = tk.Tk()
    window.title("Détecteur de Box Longs")
    window.geometry("800x600")

    frame_top = tk.Frame(window)
    frame_top.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    tk.Label(frame_top, text="Logs :").pack(anchor="w")
    gui_output = scrolledtext.ScrolledText(frame_top, wrap=tk.WORD, width=90, height=15)
    gui_output.pack(padx=5, pady=5)

    tk.Label(frame_top, text="Voitures avec pit long détecté :").pack(anchor="w")
    pitlong_output = scrolledtext.ScrolledText(frame_top, wrap=tk.WORD, width=90, height=10, bg="#ffe6e6")
    pitlong_output.pack(padx=5, pady=5)

    start_btn = tk.Button(window, text="Démarrer la détection", command=lambda: start_detection_thread(gui_output, pitlong_output))
    start_btn.pack(pady=10)

    window.mainloop()

# ===========================
# LANCER GUI
# ===========================
if __name__ == "__main__":
    create_gui()
