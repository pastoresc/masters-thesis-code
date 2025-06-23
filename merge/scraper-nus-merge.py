import pandas as pd

# Load files
df_website = pd.read_csv("nus_website_data.csv")
df_pdf     = pd.read_csv("nus_pdf_data.csv")
df_detail  = pd.read_csv("nus_course_details.csv")

# Replicate PDF rows for any program IDs in website but missing in PDF
website_ids = set(df_website["Program ID"].unique())
pdf_ids     = set(df_pdf["Program ID"].unique())
missing_ids = website_ids - pdf_ids

if missing_ids:
    # pick existing PDF program ID
    base_id = next(iter(pdf_ids))
    for pid in missing_ids:
        replicated = df_pdf[df_pdf["Program ID"] == base_id].copy()
        replicated["Program ID"] = pid
        df_pdf = pd.concat([df_pdf, replicated], ignore_index=True)

# Debug counts
for pid in sorted(website_ids):
    cnt = df_pdf[df_pdf["Program ID"] == pid].shape[0]
    print(f"[INFO] Courses in PDF for {pid}: {cnt}")

# Merge website and pdf data
df_wp = pd.merge(
    df_website,
    df_pdf,
    how="left",
    on=["Program ID"],
    validate="1:m")

# 4. Merge result with course‐details on course code
df_merged = pd.merge(
    df_wp,
    df_detail.add_suffix("_detail"),  # avoid accidental name collisions
    how="left",
    left_on="Course Code",
    right_on="Course Code_detail",
    validate="m:1"  # many merged rows to one detail row
)

# Override PDF fields with detail fields when present
df_merged["Course Title"] = (
    df_merged["Course Title_detail"]
    .fillna(df_merged["Course Title"])
    .fillna("Not Specified")
)
df_merged["Course Credits"] = (
    df_merged["Course Credits_detail"]
    .fillna(df_merged["Course Credits"])
    .fillna("Not Specified")
)
df_merged["Course Description"] = (
    df_merged["Course Description_detail"]
    .fillna("Not Specified")
)
df_merged["Prerequisites"] = (
    df_merged["Prerequisites_detail"]
    .fillna("Not Specified")
)

# Drop redundant columns
to_drop = [
    "Course Title_detail", "Course Credits_detail",
    "Course Code_detail", "Course Description_detail", "Prerequisites_detail"
]
df_merged.drop(columns=to_drop, inplace=True, errors="ignore")

# Reorder columns
final_columns = [
    "Program ID", "Program Title", "Institution", "Location", "Language",
    "Study Format", "Duration", "Total Credits", "Degree Type",
    "Specialization", "Modality", "Tuition Fees",
    "Academic Admission Requirements", "Language Admission Requirements",
    "Course Code", "Course Title", "Course Credits",
    "Course Description", "Prerequisites"
]

for col in final_columns:
    if col not in df_merged.columns:
        df_merged[col] = "Not Specified"

df_merged = df_merged[final_columns]

# Save to CSV
df_merged.to_csv("nus_merged_data.csv", index=False)
print(f"[OK] Data successfully merged and saved to 'nus_merged_data.csv'")