import pandas as pd

# Input and output
website_csv = "ucph_website_data.csv"
pdf_csv = "ucph_pdf_data.csv"
course_csv = "ucph_course_data.csv"
course_details_csv = "ucph_course_details.csv"
output_csv = "ucph_merged_data.csv"

# Load input data
df_program = pd.read_csv(website_csv)
df_pdf = pd.read_csv(pdf_csv)
df_courses = pd.read_csv(course_csv)
df_details = pd.read_csv(course_details_csv)

# Filter successfully matched course details
df_details = df_details[df_details["Matched Course Title"].notna()]

# Merge program-level info (website and PDF)
program_info = df_program.iloc[0].to_dict()
pdf_info = df_pdf.iloc[0].to_dict()

# Use fallback for missing program fields
for key, value in pdf_info.items():
    if key in program_info:
        if program_info[key] in ["Not specified", "Not available", "", None]:
            program_info[key] = value

# Merge with course and detail data
df_combined = df_courses.merge(
    df_details,
    how="left",
    left_on=["Program ID", "Course Title"],
    right_on=["Program ID", "Original PDF Title"],
    suffixes=('', '_detail')
)

# Drop matching helper columns
df_combined.drop(columns=["Original PDF Title", "Matched Course Title"], errors="ignore", inplace=True)

# Apply program_info to each row
for key, value in program_info.items():
    if key not in df_combined.columns:
        df_combined[key] = value

# Column order
final_columns = [
    "Program ID", "Program Title", "Institution", "Location", "Language", "Study Format",
    "Duration", "Total Credits", "Degree Type", "Specialization", "Modality", "Tuition Fees",
    "Academic Admission Requirements", "Language Admission Requirements",
    "Course Code", "Course Title", "Course Credits", "Course Description", "Prerequisites"
]

# Ensure all columns exist and reorder
df_final = df_combined[final_columns]
df_final.fillna("Not available", inplace=True)

# Keep only one row per Course Code
df_final = df_final.drop_duplicates(subset=["Course Code"])

# Export and save to CSV
df_final.to_csv(output_csv, index=False)
print(f"[OK] Final merged file saved to '{output_csv}'")