"""
load_beta_matrix.py
Loads a manageable portion of the methylation beta-value matrix from GEO.
- Reads first 500 CpG rows using pandas
- Avoids loading full dataset to reduce memory cost
- Splits columns into:
    * beta-value matrix
    * detection p-value matrix
- Prepares clean DataFrames for downstream analysis
"""

import gzip
import pandas as pd #Pandas is used to read tables.
from pathlib import Path

# --------------------------
# Locate project directories
# --------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Path to the compressed beta matrix (Points to the beta-value matrix).
BETA_FILE = RAW_DIR / "GSE147058_processed_matrix.txt.gz"

print("Loading from:", BETA_FILE)

# --------------------------
# Load only a small chunk (first 500 CpG sites)
# --------------------------
# nrows = limits number of rows loaded (excluding header)
df = pd.read_csv( #Reads only the first 500 CpG rows (to avoid memory overload).
    BETA_FILE,
    compression="gzip",
    sep="\t",
    nrows=500
)

# ---------------------------
# Display basic information 
# ---------------------------
print("\nDataFrame shape:", df.shape) # df.shape Shows dimensions (rows × columns).
print("\nColumns:")
# Check the true name of the CpG column before renaming
print(df.columns) # View column names

print("\nFirst 5 rows:")
print(df.head()) #Shows the 5 top of the table.

# -----------------------------------------------------------------------------------------------
# Split beta values and detection p-values
# Beta matrix: contains true epigenetic methylation values for each probe/sample.
# Detection P-value matrix: indicates measurement quality; low values mean high-confidence data.
# -----------------------------------------------------------------------------------------------

id_col = df.columns[0]           # First column (should be 'Unnamed: 0') contains the CpG names.
value_cols = df.columns[1:]      # Beta + Detection p-values

# even indices → list of beta columns
beta_cols = [c for i, c in enumerate(value_cols) if i % 2 == 0] # From value_cols, we select every second column: these are the beta-value columns (true methylation levels, 0–1).

# odd indices → detection p-value columns (list of p-values)
detp_cols = [c for i, c in enumerate(value_cols) if i % 2 == 1] # Selecting the detection p-value columns: Illumina’s measure of signal quality for each probe.

# Build two DataFrames with all beta and p-values columns
beta_chunk = df[[id_col] + beta_cols].copy() # Select the desired columns from df and build a clean, independent DataFrame using .copy().
detp_chunk = df[[id_col] + detp_cols].copy()

# Use CpG IDs as index
beta_chunk = beta_chunk.rename(columns={id_col: "CpG_ID"}).set_index("CpG_ID") # Rename CpG column and use it as row index
detp_chunk = detp_chunk.rename(columns={id_col: "CpG_ID"}).set_index("CpG_ID") # Rename CpG column and use it as row index

print("\nBeta chunk shape:", beta_chunk.shape)
print("Detection p-value chunk shape:", detp_chunk.shape)

print("\nBeta chunk (first 5 rows):")
print(beta_chunk.head())

# ---------------------------------------------------------------------------------------
# Save clean chunks to data/processed
# Save the cleaned beta and detection p-value chunks (first 500 CpGs) to data/processed/
# ---------------------------------------------------------------------------------------
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" # Path to the folder where cleaned data will be saved
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)  # Create processed/ folder if it doesn't exist

beta_out = PROCESSED_DIR / "beta_values_chunk_500cpg.csv" # Output path for cleaned beta matrix
detp_out = PROCESSED_DIR / "detection_pvalues_chunk_500cpg.csv" # Output path for cleaned detection p-values

# Save as CSV (CpG_ID as index)
beta_chunk.to_csv(beta_out)
detp_chunk.to_csv(detp_out)

print("\nSaved beta chunk to:", beta_out) # Save beta matrix as CSV
print("Saved detection p-value chunk to:", detp_out) # Save detection p-values as CSV

