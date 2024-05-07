# facial_recognition
projet de reconnaissance faciale pour gerer les employes dans une entreprise 
Gestion des Employés avec Reconnaissance Faciale
Ce projet est une application Python qui permet de gérer les employés d'une entreprise en utilisant la reconnaissance faciale pour la gestion des présences et d'autres fonctionnalités liées à la gestion des tâches de production.

Fonctionnalités
Gestion des Employés:
Ajout et mise à jour des informations des employés.
Stockage des informations telles que le nom, le prénom, le poste et le département dans une base de données SQLite.
Capture et enregistrement de la photo des employés pour la reconnaissance faciale.
Reconnaissance Faciale:
Identification des employés par reconnaissance faciale lors de leur arrivée et de leur départ.
Comparaison des visages capturés avec les visages enregistrés dans la base de données.
Gestion des pointages (arrivée et départ) avec horodatage.
Gestion des Tâches de Production:
Enregistrement des tâches de production effectuées par les employés, y compris le projet et le nombre d'heures travaillées.
Possibilité de générer un rapport de production pour voir le nombre d'heures travaillées par projet et par employé.
Interface Utilisateur Conviviale:
Interface graphique (GUI) basée sur Tkinter pour une interaction facile.
Boutons intuitifs pour accéder aux différentes fonctionnalités de l'application.
Prérequis
Avant d'exécuter l'application, assurez-vous d'installer les bibliothèques Python suivantes :

tkinter : Pour la création de l'interface utilisateur.
sqlite3 : Pour la gestion de la base de données SQLite.
cv2 (OpenCV) : Pour la capture d'image à partir de la webcam et la reconnaissance faciale.
face_recognition : Pour la reconnaissance faciale.
numpy : Pour le traitement des tableaux d'images.
json : Pour la manipulation des données JSON.
datetime : Pour la gestion des dates et heures.
Vous pouvez installer ces bibliothèques via pip en exécutant la commande suivante :

bash
Copy code
pip install tkinter sqlite3 opencv-python-headless face_recognition numpy
Utilisation
Clonez ce dépôt sur votre machine locale.
Assurez-vous que vous avez installé tous les prérequis.
Exécutez le script Python main.py.
Utilisez l'interface graphique pour ajouter des employés, enregistrer les pointages, gérer les tâches de production, et générer des rapports.
Contribution
Les contributions sous forme de pull requests sont les bienvenues. Pour les changements importants, veuillez d'abord ouvrir une issue pour discuter de ce que vous souhaitez modifier.

Auteur
Ce projet a été développé par [AZZIMANI SOUHAIL].
