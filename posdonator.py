import xml.etree.ElementTree as ET

# Charger le fichier XML
tree = ET.parse('C:/RIS/xml/live.xml')  # remplace 'live.xml' par ton fichier
root = tree.getroot()

# Demander à l'utilisateur le numéro de voiture recherché
numero_voiture_recherchee = input("Entrez le numéro de la voiture : ")

# Parcourir chaque <lineinfo> dans le XML
for lineinfo in root.findall('lineinfo'):
    numero = lineinfo.find('numero').text
    position = lineinfo.find('position').text

    # Si le numéro correspond à celui recherché
    if numero == numero_voiture_recherchee:
        print(f"La voiture #{numero} est à la position {position}.")
        break  # Arrêter la boucle une fois trouvée
else:
    # Si aucune voiture correspondante n'est trouvée
    print(f"❌ Voiture #{numero_voiture_recherchee} non trouvée.")
