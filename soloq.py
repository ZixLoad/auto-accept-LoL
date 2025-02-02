import pyautogui
import cv2
import numpy as np
import time
import json
import os
import tkinter as tk
from pynput import mouse


COULEURS_CIBLES = [
    (42, 37, 30) 
]
TOLERANCE = 15  
CONFIG_FILE = "config.json" 
# Variables globales
X, Y = None, None
selection_mode = False  
def sauvegarder_position(x, y):
    """ Sauvegarde la position X, Y dans un fichier JSON """
    data = {"X": x, "Y": y}
    with open(CONFIG_FILE, "w") as file:
        json.dump(data, file)
    print(f"[💾] Position sauvegardée : X={x}, Y={y}")

def charger_position():
    """ Charge la dernière position enregistrée """
    if os.path.exists(CONFIG_FILE):  # Vérifie si le fichier existe
        with open(CONFIG_FILE, "r") as file:
            data = json.load(file)
            return data.get("X"), data.get("Y")
    return None, None  # Retourne None si pas de position sauvegardée

def activer_selection():
    """ Active le mode sélection : le prochain clic gauche enregistrera la position """
    global selection_mode
    selection_mode = True
    status_label.config(text="🖱️ Cliquez n'importe où pour définir la position...")

    # Lancer l'écoute des clics globaux
    listener = mouse.Listener(on_click=enregistrer_position)
    listener.start()

def enregistrer_position(x, y, button, pressed):
    """ Capture la position du prochain clic gauche sur l'écran """
    global X, Y, selection_mode
    if pressed and selection_mode:  # Vérifie si un clic gauche est fait
        X, Y = x, y
        position_label.config(text=f"Position : X={X}, Y={Y}")
        status_label.config(text="✅ Position enregistrée !")
        selection_mode = False  # Désactive la sélection
        sauvegarder_position(X, Y)  # 📌 Sauvegarde la position

def couleur_proche(c1, couleurs_cibles, tolerance):
    """ Vérifie si une couleur est proche d'une des couleurs enregistrées """
    return any(all(abs(c1[i] - c2[i]) < tolerance for i in range(3)) for c2 in couleurs_cibles)

def detecter_et_cliquer():
    """ Détecte la couleur et clique automatiquement """
    if X is None or Y is None:
        status_label.config(text="❌ Sélectionne d'abord la position !")
        return

    status_label.config(text="🔍 En attente du bouton...")
    root.update()

    while True:
        # Capture l'écran
        screenshot = pyautogui.screenshot()
        image = np.array(screenshot)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Vérifier la couleur
        couleur_pixel = image[Y, X]
        print(f"[INFO] Couleur détectée en ({X}, {Y}) : {couleur_pixel}")

        if couleur_proche(couleur_pixel, COULEURS_CIBLES, TOLERANCE):
            print("[✅] Bouton détecté ! Clic en cours...")
            pyautogui.click(X, Y)
            status_label.config(text="✅ Partie acceptée !")
            break

        time.sleep(1)  # Vérifier toutes les secondes

# Interface Graphique (GUI)
root = tk.Tk()
root.title("Auto-Accept LoL")
root.geometry("350x250")

# Charger la dernière position enregistrée
X, Y = charger_position()

# Instructions
instruction_label = tk.Label(root, text="Clique sur 'Sélectionner Position' puis clique sur le bouton Accepter.", fg="blue", wraplength=300)
instruction_label.pack(pady=5)

# Bouton de sélection de position
btn_select = tk.Button(root, text="Sélectionner Position", command=activer_selection)
btn_select.pack(pady=10)

# Affichage de la position choisie
if X is not None and Y is not None:
    position_label = tk.Label(root, text=f"Position : X={X}, Y={Y}", fg="black")
    status_label = tk.Label(root, text="✅ Position restaurée !", fg="green")
else:
    position_label = tk.Label(root, text="Position : Non définie", fg="black")
    status_label = tk.Label(root, text="🔵 Aucune position enregistrée.", fg="black")

position_label.pack(pady=5)

# Bouton de démarrage
btn_start = tk.Button(root, text="Démarrer", command=detecter_et_cliquer)
btn_start.pack(pady=20)

# Statut
status_label.pack(pady=5)

root.mainloop()
