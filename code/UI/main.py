import pygame
import uvicorn
import json
import os
import argparse
from multiprocessing import Process, Manager
from typing import List, Tuple, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# --- Pydantic Modelle ---

class Circle(BaseModel):
    """Repräsentiert einen Kreis, der gezeichnet werden soll."""
    name: str = Field(..., description="Eindeutiger Name des Kreises")
    x: int = Field(..., description="X-Koordinate des Kreismittelpunkts in Pixeln")
    y: int = Field(..., description="Y-Koordinate des Kreismittelpunkts in Pixeln")
    radius: int = Field(..., gt=0, description="Radius des Kreises in Pixeln")
    color: Tuple[int, int, int] = Field(..., description="RGB-Farbe des Kreises (z.B. [255, 0, 0] für Rot)")

class CircleList(BaseModel):
    """Liste von Kreisen für die API."""
    circles: List[Circle]

class Config(BaseModel):
    """Konfigurationsmodell für das Programm."""
    background_image: str = Field(..., description="Pfad zum Hintergrundbild")
    state_file: str = Field(..., description="Pfad zur JSON-Datei für den Programmzustand")

# --- Globale Variablen für den Pygame-Prozess (werden über Manager geteilt) ---
# Diese werden im Hauptprozess initialisiert und an den Pygame-Prozess übergeben.
# shared_circles: Manager.list[Circle]
# shared_background_image_path: str
# shared_state_file_path: str

# --- Funktionen zur Zustandsverwaltung ---

def load_circles_state(state_file_path: str) -> List[Circle]:
    """Lädt den Zustand der Kreise aus einer JSON-Datei."""
    if os.path.exists(state_file_path):
        try:
            with open(state_file_path, 'r') as f:
                data = json.load(f)
                # Validierung der geladenen Daten mit Pydantic
                return [Circle(**item) for item in data]
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Fehler beim Laden der Zustandsdatei '{state_file_path}': {e}. Starte mit leerem Zustand.")
            return []
    return []

def save_circles_state(state_file_path: str, circles: List[Circle]):
    """Speichert den aktuellen Zustand der Kreise in einer JSON-Datei."""
    try:
        # Konvertiere Pydantic-Objekte in Dictionaries für JSON-Serialisierung
        data_to_save = [circle.model_dump() for circle in circles]
        with open(state_file_path, 'w') as f:
            json.dump(data_to_save, f, indent=2)
    except IOError as e:
        print(f"Fehler beim Speichern der Zustandsdatei '{state_file_path}': {e}")

# --- Pygame-Prozess ---

def pygame_process(background_image_path: str, state_file_path: str):
    """
    Der separate Prozess, der das Pygame-Fenster und die Zeichenlogik verwaltet.
    """
    pygame.init()

    # Lade das Hintergrundbild
    try:
        screen = pygame.display.set_mode((1024,512))
        background_image = pygame.image.load(background_image_path).convert()
        screen_width, screen_height = background_image.get_size()
    except pygame.error as e:
        print(f"Fehler beim Laden des Hintergrundbildes '{background_image_path}': {e}")
        print("Starte mit Standardauflösung (800x600) und ohne Hintergrundbild.")
        screen_width, screen_height = 1024, 512
        background_image = None # Setze auf None, um Fehler beim Blitting zu vermeiden

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Circle Renderer")

    running = True
    clock = pygame.time.Clock()

    # Lade den initialen Zustand der Kreise beim Start des Pygame-Prozesses
    initial_circles = load_circles_state(state_file_path)
    # Füge die geladenen Kreise zur shared_circles Liste hinzu
    #shared_circles.extend(initial_circles)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Hintergrund zeichnen
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((0, 0, 0)) # Schwarzer Hintergrund, wenn kein Bild geladen

        # Kreise zeichnen (aus der geteilten Liste)
        # Erstelle eine Kopie, um Iterationsfehler zu vermeiden, wenn die Liste von FastAPI geändert wird
        # current_circles = list(shared_circles)
        # for circle in current_circles:
        #     try:
        #         pygame.draw.circle(screen, circle.color, (circle.x, circle.y), circle.radius)
        #     except TypeError as e:
        #         print(f"Fehler beim Zeichnen des Kreises {circle.name}: {e}. Überprüfe Farb- oder Koordinatenwerte.")
        #     except Exception as e:
        #         print(f"Ein unerwarteter Fehler ist beim Zeichnen von Kreis {circle.name} aufgetreten: {e}")


        pygame.display.flip()
        clock.tick(60) # Begrenze die Bildrate auf 60 FPS

    pygame.quit()
    print("Pygame-Fenster geschlossen.")

# --- FastAPI Anwendung ---

app = FastAPI(
    title="Pygame Circle API",
    description="API zur Steuerung von Kreisen in einem Pygame-Fenster.",
    version="1.0.0"
)

# Diese Variablen werden im Hauptprozess gesetzt, bevor Uvicorn gestartet wird
# und sind dann für die FastAPI-Routen verfügbar.
#_shared_circles_list: Optional[Manager.list] = None
#_state_file: Optional[str] = None

@app.post("/circles", response_model=CircleList, summary="Aktualisiert die Liste der Kreise")
async def update_circles(circle_list: CircleList):
    """
    Aktualisiert die Liste der im Pygame-Fenster angezeigten Kreise.
    Alle vorhandenen Kreise werden durch die neue Liste ersetzt.
    """
    if _shared_circles_list is None or _state_file is None:
        raise HTTPException(status_code=500, detail="Server nicht korrekt initialisiert.")

    # Leere die aktuelle Liste und füge die neuen Kreise hinzu
    _shared_circles_list[:] = [] # Löscht alle Elemente der Manager.list
    _shared_circles_list.extend(circle_list.circles)

    # Speichere den neuen Zustand in der JSON-Datei
    save_circles_state(_state_file, list(_shared_circles_list))

    return CircleList(circles=list(_shared_circles_list))

@app.get("/circles", response_model=CircleList, summary="Gibt die aktuelle Liste der Kreise zurück")
async def get_circles():
    """
    Gibt die aktuell im Pygame-Fenster angezeigten Kreise zurück.
    """
    if _shared_circles_list is None:
        raise HTTPException(status_code=500, detail="Server nicht korrekt initialisiert.")
    return CircleList(circles=list(_shared_circles_list))


# --- Hauptausführung ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pygame Circle Renderer mit FastAPI Steuerung.")
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Pfad zur Konfigurationsdatei (Standard: config.json)"
    )
    args = parser.parse_args()

    # Lade die Konfiguration
    try:
        with open(args.config, 'r') as f:
            config_data = json.load(f)
        app_config = Config(**config_data)
    except FileNotFoundError:
        print(f"Fehler: Konfigurationsdatei '{args.config}' nicht gefunden.")
        exit(1)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Fehler beim Parsen der Konfigurationsdatei '{args.config}': {e}")
        exit(1)

    # Initialisiere den Manager für die geteilte Liste
    manager = Manager()
    shared_circles = manager.list() # Eine Liste, die zwischen Prozessen geteilt werden kann

    # Setze die globalen Variablen für die FastAPI-App
    _shared_circles_list = shared_circles
    _state_file = app_config.state_file

    print(f"Starte Pygame-Prozess mit Hintergrundbild: {app_config.background_image}")
    print(f"Zustand wird gespeichert/geladen in: {app_config.state_file}")

    # Starte den Pygame-Prozess in einem separaten Thread/Prozess
    # Der Pygame-Prozess muss in einem separaten Prozess laufen,
    # da er seine eigene Event-Schleife hat, die den Hauptthread blockieren würde.
    p = Process(target=pygame_process, args=(app_config.background_image, app_config.state_file))
    p.start()

    # Starte den FastAPI-Server im Hauptprozess
    print("\nFastAPI-Server startet auf http://127.0.0.1:8000")
    print("API-Dokumentation unter http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)

    # Warte auf das Beenden des Pygame-Prozesses, wenn FastAPI beendet wird
    p.join()
    print("Programm beendet.")