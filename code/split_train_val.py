import os
import shutil
import argparse

def split_data(source_folder, train_ratio=0.7):
    """
    Teilt Dateien aus einem Quellordner in 'train'- und 'val'-Datensätze auf.

    Args:
        source_folder (str): Der Pfad zum Ordner, der die Originaldateien enthält.
        train_ratio (float): Der Anteil der Dateien, der in den 'train'-Ordner kopiert werden soll (z.B. 0.7 für 70%).
                             Der Rest geht in den 'val'-Ordner.
    """
    if not os.path.isdir(source_folder):
        print(f"Fehler: Der Quellordner '{source_folder}' existiert nicht.")
        return

    # Zielordner erstellen
    train_folder = os.path.join(source_folder, 'train')
    val_folder = os.path.join(source_folder, 'val')

    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)

    # Alle Dateien im Quellordner auflisten (Unterordner werden ignoriert)
    files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    
    if not files:
        print(f"Keine Dateien im Ordner '{source_folder}' gefunden, die aufgeteilt werden könnten.")
        return

    # Dateien sortieren, damit die Namesgleichheit von images und labeln gegeben
    files.sort()    

    # Aufteilungsindex berechnen
    num_files = len(files)
    num_train = int(num_files * train_ratio)

    # Dateien aufteilen
    train_files = files[:num_train]
    val_files = files[num_train:]

    print(f"Gesamtanzahl der Dateien: {num_files}")
    print(f"Anzahl der Dateien für 'train': {len(train_files)}")
    print(f"Anzahl der Dateien für 'val': {len(val_files)}")

    # Dateien in die entsprechenden Ordner kopieren
    print("\nKopiere Dateien in den 'train'-Ordner...")
    for file_name in train_files:
        src_path = os.path.join(source_folder, file_name)
        dst_path = os.path.join(train_folder, file_name)
        shutil.copy2(src_path, dst_path) # copy2 behält Metadaten wie Erstellungs-/Änderungsdatum

    print("Kopieren in den 'train'-Ordner abgeschlossen.")

    print("\nKopiere Dateien in den 'val'-Ordner...")
    for file_name in val_files:
        src_path = os.path.join(source_folder, file_name)
        dst_path = os.path.join(val_folder, file_name)
        shutil.copy2(src_path, dst_path)

    print("Kopieren in den 'val'-Ordner abgeschlossen.")
    print("\nDatenaufteilung erfolgreich!")

# --- Beispielhafte Nutzung ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="splits the dataset."
    )
    parser.add_argument(
        "source_folder",
        type=str,
        help="source folder"
    )
    parser.add_argument(
        "--ratio",
        type=float,
        default=0.7,
        help="ratio"
    )

    args = parser.parse_args()

    # Führe die Funktion mit den Kommandozeilenargumenten aus
    split_data(args.source_folder, args.ratio)