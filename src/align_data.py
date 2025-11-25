import pandas as pd
from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parents[1] # Find the current file from the parent one (folder)
PROC = PROJECT_ROOT / "data" / "processed"

# --- Load processed files ---
metadata = pd.read_csv(PROC / "metadata_clean.csv") # Read the metadata file 
beta = pd.read_csv(PROC / "beta_values_chunk_500cpg.csv") # Read the beta_values_chunk file 

# --- Extract GSM_ID from beta columns ---
# In GSE72680, the first column (index 0) is CpG_ID; others are sample columns (Illumina IDs)
beta_cols = beta.columns[1:] # take from the second column (index 1) till the end.

# Convert tje illumina_id to a DataFrame, for alignment
beta_cols_df = pd.DataFrame({
    "illumina_id": beta_cols
})
# Add GSM_ID = NaN placeholder (because this dataset offers no mapping)
beta_cols_df["GSM_ID"] = None # Shows that Illumina IDs # GSM_ID in this GSE

# To compare the number of samples in metadata and beta files (make sure they're the same)
print("\n(beta) sample columns:", len(beta_cols)) # Displays the number of columns in beta file
print("(metadata) GSM_ID entries:", metadata["GSM_ID"].nunique()) # Displays the number of GSM in the metadata file

# --- Alignment (shows the limitations of this process) ---
# Since GSM_ID does NOT correspond to the beta column names,
# we simply keep metadata intact and keep beta intact.
# We CANNOT merge on GSM_ID or Sample_Name for this dataset.

print("\nWARNING: Beta sample IDs (Illumina) and metadata sample IDs (GSM_ID) do NOT match.")
print("Direct alignment is impossible for this GSE.")
print("Proceeding with separate files for downstream descriptive analysis.")

# --- Save cleaned versions (unchanged) ---
metadata.to_csv(PROC / "metadata_aligned.csv", index=False) #Save metadata in e new file
beta.to_csv(PROC / "beta_values_aligned.csv", index=False) # Save the beta-matrix in a new file

print("\nSaved:")
print(" - metadata_aligned.csv")
print(" - beta_values_aligned.csv")
