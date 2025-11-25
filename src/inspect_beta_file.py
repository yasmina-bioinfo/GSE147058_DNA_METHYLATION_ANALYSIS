"""
inspect_beta_file.py
This script performs a basic diagnostic to ensure the raw GEO file can be located and opened.
- Checks the file path
- Verifies existence
- Opens the .gz file
- Displays the first 10 lines
It does NOT load data into memory or perform analysis.
"""

import gzip            #Imports the gzip module to read compressed .gz files.
from pathlib import Path  # Imports Path, a modern way to handle file paths in Python.

# ----- Définir le chemin du fichier brut -----
# Finds the root directory of the project by going one level above the script’s location.

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Ensures the script runs correctly even if the project directory is moved, by using relative paths.

RAW_DIR = PROJECT_ROOT / "data" / "raw"
# STANDARD : Builds the path to the data/raw/ folder where raw GEO files are stored.

BETA_FILE = RAW_DIR / "GSE147058_processed_matrix.txt.gz"
# Points to the compressed beta-value matrix for the GSE147058 dataset.

print("File Path :", BETA_FILE) #Prints the exact path to the file (good for debugging).
print("Exists ?", BETA_FILE.exists()) #Checks if the file actually exists on the system.

# ----- Reads and displays the 10 firt lines of the file -----
# Opens the .gz file in text mode for reading. "rt" = read text.

with gzip.open(BETA_FILE, mode="rt") as f:
    print("\nFirst lines of the beta file :\n") #Prints a header before showing the file content.
    for i in range(10): #Loops to read only the first 10 lines (the whole file is too big).
        line = f.readline() #Reads the next line of the file.
        if not line: #Stops the loop if the end of file is reached.
            break #Exits the loop.
        print(line.rstrip("\n")) #Prints each line without the trailing newline character.
