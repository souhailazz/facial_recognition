import tkinter as tk
from tkinter import messagebox
import sqlite3
import cv2 
import face_recognition 
import numpy as np 
import json
from face_recognition import face_distance
from tkinter import ttk  
from datetime import datetime


# Connexion à la base de données
conn = sqlite3.connect('eng.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS employes (
                    id INTEGER PRIMARY KEY,
                    nom TEXT,
                    prenom TEXT,
                    poste TEXT,
                    departement TEXT,
                    photo BLOB,
                    face_encoding TEXT)''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS pointages (
                    id INTEGER PRIMARY KEY,
                    id_emp INTEGER,
                    date TEXT,
                    heure_arrivee TEXT,
                    heure_depart TEXT)''')
conn.commit()
cursor.execute('''CREATE TABLE IF NOT EXISTS production_tasks (
    id INTEGER PRIMARY KEY,
    id_emp INTEGER,
    project TEXT,
    hours_worked INTEGER,
    FOREIGN KEY (id_emp) REFERENCES employes(id)
)''')
conn.commit()


def capturer_image(type_pointage, nom=None, prenom=None, poste=None, departement=None):
    # Ouvrir la caméra pour capturer l'image de l'employé
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if ret:
        # Conversion de l'image en format compatible pour stockage dans la base de données
        _, img_encoded = cv2.imencode('.jpg', frame)
        photo_bytes = img_encoded.tobytes()

        if type_pointage == "ajout_employe":
            # Si c'est pour l'ajout d'un employé, nous n'avons pas besoin de faire une reconnaissance faciale
            enregistrer_employe(nom, prenom, poste, departement, photo_bytes)
            messagebox.showinfo("Succès", "Employé ajouté avec succès.")
        else:
            # Reconnaissance faciale sur l'image capturée
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            # Vérifier si un visage a été détecté
            if len(face_encodings) > 0:
                # Charger les visages enregistrés dans la base de données
                cursor.execute("SELECT id, nom, prenom, face_encoding FROM employes")
                rows = cursor.fetchall()
                known_face_encodings = []
                known_face_names = []

                for row in rows:
                    employe_id, employe_nom, employe_prenom, employe_face_encoding_str = row
                    employe_face_encoding = np.array(json.loads(employe_face_encoding_str))
                    known_face_encodings.append(employe_face_encoding)
                    known_face_names.append((employe_id, f"{employe_nom} {employe_prenom}"))

                # Comparaison des visages détectés avec les visages enregistrés
                for face_encoding in face_encodings:
                    # Comparaison avec les visages connus
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    id_emp = None

                    # Trouver la correspondance
                    if True in matches:
                        first_match_index = matches.index(True)
                        id_emp, name = known_face_names[first_match_index]
                        if type_pointage == "arrivee":
                            pointer_arrivee(id_emp, name)
                        elif type_pointage == "depart":
                            pointer_depart(id_emp, name)
                    else:
                        messagebox.showerror("Erreur", "Visage introuvable dans la base de données.")
            else:
                messagebox.showerror("Erreur", "Aucun visage détecté.")
def enregistrer_employe(nom, prenom, poste, departement, photo_bytes, face_encoding):
    # Convert face encoding to a JSON string
    face_encoding_json = json.dumps(face_encoding.tolist())

    # Insert the employee data into the database
    cursor.execute("INSERT INTO employes (nom, prenom, poste, departement, photo, face_encoding) VALUES (?, ?, ?, ?, ?, ?)",
                   (nom, prenom, poste, departement, photo_bytes, face_encoding_json))
    conn.commit()





def pointer_arrivee(id_emp, nom):
    now = datetime.now()
    heure = now.strftime("%H:%M:%S")
    date = now.strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO pointages (id_emp, date, heure_arrivee) VALUES (?, ?, ?)", (id_emp, date, heure))
    conn.commit()
    messagebox.showinfo("Succès", f"Pointage d'arrivée enregistré pour {nom} à {heure}.")

def pointer_depart(id_emp, nom):
    now = datetime.now()
    heure = now.strftime("%H:%M:%S")
    cursor.execute("UPDATE pointages SET heure_depart = ? WHERE id_emp = ? AND date = ?", (heure, id_emp, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    messagebox.showinfo("Succès", f"Pointage de départ enregistré pour {nom} à {heure}.")
def detecter_visages(image, cascade):
    # Convert the image to RGB format for face_recognition
    frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Detect faces and encodings
    face_locations = face_recognition.face_locations(frame_rgb)
    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
    
    if len(face_encodings) > 0:
        face_encoding = face_encodings[0]  # Assuming only one face is detected
        
        # Convert the face encoding to a JSON string
        face_encoding_str = json.dumps(face_encoding.tolist())
        
        # Fetch face encodings from the database
        cursor.execute("SELECT face_encoding, nom FROM employes")
        rows = cursor.fetchall()

        # Convert encodings to NumPy arrays
        database_encodings = [np.array(json.loads(row[0])) for row in rows]
        database_names = [row[1] for row in rows] 

        # Ensure that the face encodings are not empty
        if len(database_encodings) > 0:
            # Calculate face distances using the custom face_distance function
            face_distances = face_distance(database_encodings, np.array(json.loads(face_encoding_str)))

            # Check if any of the face distances are within tolerance
            matches = [distance <= 0.6 for distance in face_distances]

            if True in matches:
                match_index = matches.index(True)
                name = database_names[match_index] 
            else:
                name = "Inconnu"
        else:
            name = "Inconnu"
    else:
        name = "Inconnu"

    # Detect faces using OpenCV for drawing rectangles
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    visages = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Draw rectangles around detected faces
    for (x, y, w, h) in visages:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(image, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    
    return image


def reconnaissance_facial():
  
    
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    cascade = cv2.CascadeClassifier(cascade_path)

    # Démarrer la capture vidéo à partir de la webcam
    cap = cv2.VideoCapture(0)

    # Vérifier si la capture vidéo est ouverte
    if not cap.isOpened():
        print("Erreur: la webcam ne peut pas être ouverte.")
        return

    while True:
        # Lire l'image de la webcam
        ret, frame = cap.read()
       
        # Vérifier si la lecture de l'image a réussi
        if not ret:
            print("Erreur: Impossible de lire l'image de la webcam.")
            break
       
        # Détecter les visages dans l'image et afficher le nom attribué à chaque visage
        frame= cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = detecter_visages(frame, cascade)
        # Afficher l'image traitée
        cv2.imshow('Reconnaissance faciale', frame)

        key = cv2.waitKey(30)

        
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()



# Interface utilisateur pour l'ajout d'un employé
def ajouter_employe_interface():
    def ajouter_employe():
        nom = nom_entry.get()
        prenom = prenom_entry.get()
        poste = poste_entry.get()
        departement = departement_entry.get()

        # Mettre à jour les étiquettes avec les informations de l'employé
        nom_label.config(text="Nom: " + nom)
        prenom_label.config(text="Prénom: " + prenom)
        poste_label.config(text="Poste: " + poste)
        departement_label.config(text="Département: " + departement)
        
        # Ouvrir la caméra pour capturer l'image de l'employé
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Conversion de l'image en format compatible pour stockage dans la base de données
            _, img_encoded = cv2.imencode('.jpg', frame)
            photo_bytes = img_encoded.tobytes()
            
            # Enregistrer l'employé avec la photo dans la base de données
            face_encodings = face_recognition.face_encodings(frame)
            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]
                enregistrer_employe(nom, prenom, poste, departement, photo_bytes, face_encoding) 
            else:
                print("Erreur: Aucun visage détecté.")  # Handle the case where no face is detected

    root = tk.Tk()
    root.geometry("250x300")
    root.title("Ajouter Employé")

    tk.Label(root, text="Nom:").grid(row=0, column=0)
    nom_entry = tk.Entry(root)
    nom_entry.grid(row=0, column=1)

    tk.Label(root, text="Prénom:").grid(row=1, column=0)
    prenom_entry = tk.Entry(root)
    prenom_entry.grid(row=1, column=1)

    tk.Label(root, text="Poste:").grid(row=2, column=0)
    poste_entry = tk.Entry(root)
    poste_entry.grid(row=2, column=1)

    tk.Label(root, text="Département:").grid(row=3, column=0)
    departement_entry = tk.Entry(root)
    departement_entry.grid(row=3, column=1)

    ajouter_button = tk.Button(root, text="Ajouter employé", command=ajouter_employe)
    ajouter_button.grid(row=4, columnspan=2)

    # Ajouter des étiquettes pour afficher les informations de l'employé
    nom_label = tk.Label(root, text="")
    nom_label.grid(row=5, columnspan=2)

    prenom_label = tk.Label(root, text="")
    prenom_label.grid(row=6, columnspan=2)

    poste_label = tk.Label(root, text="")
    poste_label.grid(row=7, columnspan=2)

    departement_label = tk.Label(root, text="")
    departement_label.grid(row=8, columnspan=2)

    root.mainloop()


# Function to fetch all employees from the database
def fetch_all_employees():
    cursor.execute("SELECT * FROM employes")
    employees = cursor.fetchall()
    return employees



def show_employees_window():
    employees = fetch_all_employees()

    employees_window = tk.Toplevel()
    employees_window.title("Liste des Employés")

    # Function to update employee information in the database
    def update_employee_info(employee_id, nom_entry, prenom_entry, poste_entry, departement_entry):
        nom = nom_entry.get()
        prenom = prenom_entry.get()
        poste = poste_entry.get()
        departement = departement_entry.get()

        cursor.execute("UPDATE employes SET nom=?, prenom=?, poste=?, departement=? WHERE id=?", (nom, prenom, poste, departement, employee_id))
        conn.commit()
        messagebox.showinfo("Succès", "Informations de l'employé mises à jour.")

    for idx, employee in enumerate(employees):
        employee_id, nom, prenom, poste, departement, _, _ = employee

        # Create entry fields for each employee's information
        tk.Label(employees_window, text=f"Nom:").grid(row=idx, column=0)
        nom_entry = tk.Entry(employees_window)
        nom_entry.insert(0, nom)
        nom_entry.grid(row=idx, column=1)

        tk.Label(employees_window, text=f"Prénom:").grid(row=idx, column=2)
        prenom_entry = tk.Entry(employees_window)
        prenom_entry.insert(0, prenom)
        prenom_entry.grid(row=idx, column=3)

        tk.Label(employees_window, text=f"Poste:").grid(row=idx, column=4)
        poste_entry = tk.Entry(employees_window)
        poste_entry.insert(0, poste)
        poste_entry.grid(row=idx, column=5)

        tk.Label(employees_window, text=f"Département:").grid(row=idx, column=6)
        departement_entry = tk.Entry(employees_window)
        departement_entry.insert(0, departement)
        departement_entry.grid(row=idx, column=7)

        # Button to update employee information
        update_button = tk.Button(employees_window, text="Mettre à jour", command=lambda employee_id=employee_id, nom_entry=nom_entry, prenom_entry=prenom_entry, poste_entry=poste_entry, departement_entry=departement_entry: update_employee_info(employee_id, nom_entry, prenom_entry, poste_entry, departement_entry))
        update_button.grid(row=idx, column=8)

def add_production_task_interface():
    add_task_window = tk.Toplevel()
    add_task_window.title("Enregistrer une tâche de production")

    tk.Label(add_task_window, text="ID Employé:").grid(row=0, column=0)
    emp_id_entry = tk.Entry(add_task_window)
    emp_id_entry.grid(row=0, column=1)

    tk.Label(add_task_window, text="Projet:").grid(row=1, column=0)
    project_entry = tk.Entry(add_task_window)
    project_entry.grid(row=1, column=1)

    tk.Label(add_task_window, text="Heures travaillées:").grid(row=2, column=0)
    hours_entry = tk.Entry(add_task_window)
    hours_entry.grid(row=2, column=1)

    record_button = tk.Button(add_task_window, text="Enregistrer", command=lambda: save_production_task_to_db(int(emp_id_entry.get()), project_entry.get(), int(hours_entry.get())))
    record_button.grid(row=3, columnspan=2)

def save_production_task_to_db(id_emp, project, hours_worked):
    # Connect to the database
    conn = sqlite3.connect('eng.db')
    cursor = conn.cursor()

    # Execute the query to save the task to the database
    cursor.execute("INSERT INTO production_tasks (id_emp, project, hours_worked) VALUES (?, ?, ?)", (id_emp, project, hours_worked))
    conn.commit()
    print("Production task added successfully.")

    # Close the database connection
    cursor.close()
    conn.close()


def generate_production_report():
    cursor.execute("SELECT id_emp, nom, prenom, project, SUM(hours_worked) FROM production_tasks INNER JOIN employes ON production_tasks.id_emp = employes.id GROUP BY id_emp")
    production_data = cursor.fetchall()
    return production_data

# Function to generate production report
def generate_production_report_interface():
    report_data = generate_production_report()

    report_window = tk.Toplevel()
    report_window.title("Rapport de Production")

    # Create Treeview widget
    tree = ttk.Treeview(report_window, columns=("Employee ID", "Nom", "Prenom", "Projet", "Heures travaillées"), show="headings")
    tree.heading("Employee ID", text="ID Employé")
    tree.heading("Nom", text="Nom")
    tree.heading("Prenom", text="Prénom")
    tree.heading("Projet", text="Projet")
    tree.heading("Heures travaillées", text="Heures travaillées")
    tree.pack()

    # Insert data into Treeview
    for idx, data in enumerate(report_data, start=1):
        emp_id, nom, prenom, project, hours_worked = data
        tree.insert("", "end", values=(emp_id, nom, prenom, project, hours_worked))

    # Ensure the report window remains visible
    report_window.mainloop()


main_root = tk.Tk()
main_root.geometry("300x300")
main_root.title("Gestion Employés")

# Create a style for ttk widgets
style = ttk.Style(main_root)
style.theme_use("clam")  # Choose a theme (e.g., "clam")

# Button styles
style.configure("Main.TButton", font=("Helvetica", 10))

# Define button commands
def placeholder_command():
    pass

# Buttons using ttk widgets
buttons = [
    ("Ajouter Employé", ajouter_employe_interface),
    ("Reconnaissance Faciale", reconnaissance_facial),
    ("Pointer Arrivée", lambda: capturer_image("arrivee")),
    ("Pointer Départ", lambda: capturer_image("depart")),
    ("Afficher Employés", show_employees_window),
    ("Enregistrer une tâche de production", add_production_task_interface),
    ("Générer un rapport de production", generate_production_report_interface)
]

# Create buttons using ttk.Button
for button_text, command in buttons:
    button = ttk.Button(main_root, text=button_text, style="Main.TButton", command=command)
    button.pack(fill="x", padx=5, pady=2)

main_root.mainloop()