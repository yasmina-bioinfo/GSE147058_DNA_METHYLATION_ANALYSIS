"""
Read the SOFT file
Find each "SAMPLE"
Extract : 
    GSM_ID
    Sample_Name
    characteristics (age, sex, trauma..)
Transform everything into a DataFrame
Save in metadata_clean.csv
"""

import gzip
from pathlib import Path
import pandas as pd

# --------------------------
# Locate project folders
# --------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1] # Find automatically the project folder
RAW_DIR = PROJECT_ROOT / "data" / "raw" # Path to the raw files (SOFT, beta_values...)
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" # Create the file to put the metadata
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)  # Create processed file if missing

# Path to the SOFT family file
SOFT_FILE = RAW_DIR / "GSE147058_family.soft.gz" # Locate the raw file (SOFT)
print("Reading SOFT file from:", SOFT_FILE)

# -----------------------------------------------------------------------
# Parse SOFT file: collect samples, build a dictionnary for each sample
# -----------------------------------------------------------------------
samples = [] # create an empty list to store all the samples
current = None  # will store info for one GSM

with gzip.open(SOFT_FILE, mode="rt") as f: # open the SOFT file in .txt mode, and name it f 
    for line in f: 
        line = line.rstrip("\n") # clean every line of the file and delete the \n 

        # Start of a new SAMPLE section 
        if line.startswith("^SAMPLE"): #start a new sample block
            if current is not None: # If a previous sample was being collected, save it first.
                samples.append(current) 
                # Create a new dictionary fo store GSM info
            current = {"characteristics_raw": []} # Prepare an empy list for raw characteristics.

        elif current is not None:
            # Strip leading/trailing spaces to make the test more robust
            stripped = line.strip()
            # GEO accession (GSM ID)
            if stripped.startswith("!Sample_geo_accession"):
                current["GSM_ID"] = stripped.split("=", 1)[1].strip() # Extract only the ID after the "=", no spaces.

            # Sample name / title (here, GSE72680 uses !Sample_title)
            elif stripped.startswith("!Sample_name") or stripped.startswith("!Sample_title"): # The name matches with the matrix beta column (sample_title is the name in this SOFT file)
                value = stripped.split("=", 1)[1].strip()
                current["Sample_Name"] = value

            # Phenotypic / clinical info
            elif stripped.startswith("!Sample_characteristics_ch1"): # extract infos (sex, age, trauma...) after the "="
                char = stripped.split("=", 1)[1].strip()
                current["characteristics_raw"].append(char) # Add everything in a list

            # End of SAMPLE section (we reach SERIES or PLATFORM)
            # If the file reaches a point where no more SAMPLE blocks follow
            # (e.g., we encounter ^SERIES or ^PLATFORM), finalize and store
            # the current sample before closing the section.
            elif stripped.startswith("^SERIES") or stripped.startswith("^PLATFORM"):
                samples.append(current)
                current = None # No more active file.

# Add last SAMPLE if file ended inside a sample block
# If the file ends while a SAMPLE is still open, save it.
# This ensures the last sample is not lost.
if current is not None:
    samples.append(current)

print(f"Number of samples found: {len(samples)}")

# Debug: show a few GSM_ID -> Sample_Name mappings
print("Example GSM_ID -> Sample_Name values:")
for s in samples[:10]:
    print(s.get("GSM_ID"), "->", s.get("Sample_Name"))

# --------------------------
# Transform characteristics into columns
# --------------------------
rows = [] # An empty list which will store one cleaned row per sample.

for s in samples: # Loop through all parsed samples from the SOFT file
    # Create the base row for this sample: GSM ID, sample name,
    # and the raw characteristics text (joined for reference)
    row = {
        "GSM_ID": s.get("GSM_ID", ""),
        "Sample_Name": s.get("Sample_Name", ""),
        "characteristics_raw": "; ".join(s.get("characteristics_raw", [])),
    }

    # Each characteristic looks like "Sex: Female" or "Age: 32"
    # Convert each raw characteristic ("Key: Value") into a clean column.
    # Example: "Sex: Female" → key="sex", value="Female"
    # Column names are normalized (lowercase, underscores).
    for ch in s.get("characteristics_raw", []):
        if ":" in ch:
            key, val = ch.split(":", 1)
            key = key.strip().lower().replace(" ", "_")  # sex, age, trauma_score, etc.
            val = val.strip()
            row[key] = val

    rows.append(row) # Store the cleaned row for this sample

metadata_df = pd.DataFrame(rows) # Convert all cleaned rows into a DataFrame


# --------------------------
# Save clean metadata table
# --------------------------
# Export the cleaned metadata to CSV and display shape + first rows
# to validate that parsing was successful.
meta_out = PROCESSED_DIR / "metadata_clean.csv"
metadata_df.to_csv(meta_out, index=False) # Save the DataFrame created previously without writting the index column.

print("\nMetadata shape:", metadata_df.shape) # Display the number of rows (samples) and columns (characteristics)
print("Saved metadata to:", meta_out) # Show where the file has been saved.
print("\nFirst 5 rows:") 
print(metadata_df.head())
