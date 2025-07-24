import cv2
import time
import os
import argparse
import simpleaudio as sa # Für die Soundausgabe
import numpy as np; 

cam_num = 0


def play_sound():
    """Spielt einen kurzen Piepton ab."""
    frequency = 800  # Hz
    duration = 0.1   # Sekunden
    samplerate = 44100  # Samples pro Sekunde

    t = np.linspace(0, duration, int(samplerate * duration), False)
    # Generiere eine Sinuswelle mit angegebener Frequenz und Amplitude
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    # Konvertiere zu 16-Bit-Integern
    audio = audio * (2**15 - 1) / np.max(np.abs(audio))
    audio = audio.astype(np.int16)

    play_obj = sa.play_buffer(audio, 1, 2, samplerate)
    play_obj.wait_done()

def capture_images(output_dir, base_filename, interval_ms):
    """
    Nimmt Bilder von der USB-Kamera auf und speichert sie.

    Args:
        output_dir (str): Das Verzeichnis, in dem die Bilder gespeichert werden.
        base_filename (str): Der Basisname für die Bilddateien.
        interval_ms (int): Das Aufnahmeintervall in Millisekunden.
    """
    # Erstelle das Ausgabeverzeichnis, falls es nicht existiert
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialisiere die Kamera
    cap = cv2.VideoCapture(cam_num)  # 0 steht für die Standard-USB-Kamera

    if not cap.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        return

    image_counter = 1
    last_capture_time = time.time() * 1000  # Aktuelle Zeit in Millisekunden

    print(f"Starte Bildaufnahme. Drücken Sie 'q', um das Programm zu beenden.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Fehler: Konnte keinen Frame von der Kamera lesen.")
            break

        # Aktuelles Bild anzeigen
        cv2.imshow("Aktuelles Bild (Druecke 'q' zum Beenden)", frame)

        current_time = time.time() * 1000
        if current_time - last_capture_time >= interval_ms:
            # Dateiname mit führenden Nullen
            filename = os.path.join(output_dir, f"{base_filename}{image_counter:04d}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Bild gespeichert: {filename}")
            play_sound() # Ton nach dem Speichern abspielen
            image_counter += 1
            last_capture_time = current_time

        # Beenden bei Tastendruck 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Kamera und Fenster schließen
    cap.release()
    cv2.destroyAllWindows()
    print("Bildaufnahme beendet.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nimmt Bilder von einer USB-Kamera auf und speichert sie.")
    parser.add_argument("--output_dir", type=str, default="output_images",
                        help="Das Verzeichnis, in dem die Bilder gespeichert werden. (Standard: output_images)")
    parser.add_argument("--base_filename", type=str, default="bild",
                        help="Der Basisname für die Bilddateien. (Standard: bild)")
    parser.add_argument("--interval_ms", type=int, default=3000,
                        help="Das Aufnahmeintervall in Millisekunden. (Standard: 3000 ms, also 3 Sekunden)")

    args = parser.parse_args()

    capture_images(args.output_dir, args.base_filename, args.interval_ms)