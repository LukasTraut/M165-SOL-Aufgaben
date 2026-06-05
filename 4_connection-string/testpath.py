import os

path_value = os.environ.get("PATH", "Variable nicht gefunden")
print("Inhalt der Umgebungsvariable PATH:")
print(path_value) 