def lire_logs(filepath):
    """
    Lit un fichier texte ligne par ligne et extrait :
    - numéro de voiture (ex: [529])
    - vitesse (ex: 88)
    - nom de l'équipe
    """
    resultats = []

    with open(filepath, 'r', encoding='utf-8') as file:
        lignes = file.readlines()

        for ligne in lignes:
            if "average speed" in ligne:
                # On coupe la ligne en parties séparées par des virgules
                parties = ligne.split(',')

                try:
                    # Partie description = index 4
                    description = parties[4]

                    # Découpe la description en mots pour extraire la vitesse
                    tokens = description.split()
                    
                    # Vitesse = mot avant "kph"
                    vitesse_index = tokens.index("kph") - 1
                    vitesse = tokens[vitesse_index]

                    # ➡️ Numéro de voiture : situé dans la colonne 9 (index 8), example : [529] Ohres - Europierre - Sofrat
                    # On récupère cette partie et on split pour isoler [529]
                    voiture_partie = parties[8].strip() if len(parties) > 8 else "Inconnu"
                    
                    # ⚠️ Extraction précise : le numéro est entre crochets
                    if '[' in voiture_partie and ']' in voiture_partie:
                        voiture_id = voiture_partie.split(']')[0].replace('[', '')
                    else:
                        voiture_id = "Inconnu"

                    # Nom de l'équipe : colonne 8 aussi mais on retire le [529]
                    equipe_nom = voiture_partie.split(']')[-1].strip() if ']' in voiture_partie else voiture_partie

                    # Ajoute au résultat
                    resultats.append({
                        'voiture_id': voiture_id,
                        'vitesse': vitesse,
                        'equipe': equipe_nom
                    })

                except Exception as e:
                    print(f"❌ Erreur lors du parsing de la ligne : {e}")
                    continue

    return resultats


def afficher_resultats(resultats):
    """
    Affiche proprement les voitures qui dépassent sous FCY
    """
    print("🚨 Dépassements détectés sous FCY :\n")
    for r in resultats:
        print(f"Voiture #{r['voiture_id']} ({r['equipe']}) -> {r['vitesse']} km/h")


# 🏁 Exécution principale
if __name__ == "__main__":
    filepath = "alerts-20240509-114320.txt"  # 🔧 Mets ici ton fichier .txt

    resultats = lire_logs(filepath)
    afficher_resultats(resultats)
