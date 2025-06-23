import pandas as pd

# Input and output
website_csv = "upcfib_website_data.csv"
admission_csv = "upcfib_admission_data.csv"
course_csv = "upcfib_course_data.csv"
output_csv = "upcfib_merged_data.csv"

# Load inputs
website_df = pd.read_csv(website_csv)
admission_df = pd.read_csv(admission_csv)
course_df = pd.read_csv(course_csv)

# Merge program metadata
program_df = pd.merge(website_df, admission_df, on="Program ID", how="left")

# Get program IDs
program_ids = program_df["Program ID"].tolist()

# Duplicate all course rows for each program ID
course_expanded = pd.concat([
    course_df.assign(**{"Program ID": pid}) for pid in program_ids
], ignore_index=True)

# Merge all program info into each course
merged_df = pd.merge(course_expanded, program_df, on="Program ID", how="left")

# Column order
final_column_order = [
    "Program ID",
    "Program Title",
    "Institution",
    "Location",
    "Language",
    "Study Format",
    "Duration",
    "Total Credits",
    "Degree Type",
    "Specialization",
    "Modality",
    "Tuition Fees",
    "Academic Admission Requirements",
    "Language Admission Requirements",
    "Course Code",
    "Course Title",
    "Course Credits",
    "Course Description",
    "Prerequisites"
]

# Apply order and save to CSV
merged_df = merged_df[final_column_order]
merged_df.to_csv(output_csv, index=False)
print(f"[OK] Merged data saved to '{output_csv}'")