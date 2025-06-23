import pandas as pd
import glob

# Input and output
MERGED_PATTERN = "*_merged_data.csv"
OUTPUT_FILE = "master_programs_data_merged.csv"

# Define column order
COLUMN_ORDER = [
    "Program ID", "Program Title", "Institution", "Location", "Language",
    "Study Format", "Duration", "Total Credits", "Degree Type", "Specialization",
    "Modality", "Tuition Fees", "Academic Admission Requirements", "Language Admission Requirements",
    "Course Code", "Course Title", "Course Credits", "Course Description", "Prerequisites"
]

def merge_all_merged_data():
    merged_files = glob.glob(MERGED_PATTERN)
    
    if not merged_files:
        print("[ERROR] No merged CSV files found.")
        return

    dataframes = []
    for file in merged_files:
        try:
            df = pd.read_csv(file)

            # Reorder and align columns (ignore missing optional columns)
            missing_cols = [col for col in COLUMN_ORDER if col not in df.columns]
            for col in missing_cols:
                df[col] = "Not Specified"

            df = df[COLUMN_ORDER]
            dataframes.append(df)
            print(f"[OK] Loaded and aligned: {file}")
        except Exception as e:
            print(f"[WARNING] Could not read {file}: {e}")

    if not dataframes:
        print("[ERROR] No data could be loaded.")
        return

    combined_df = pd.concat(dataframes, ignore_index=True)

    # Remove duplicates based on program ID and course code
    combined_df.drop_duplicates(subset=["Program ID", "Course Code"], inplace=True)

    # Save to CSV
    combined_df.to_csv(OUTPUT_FILE, index=False)
    print(f"[OK] Combined merged data saved to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    merge_all_merged_data()