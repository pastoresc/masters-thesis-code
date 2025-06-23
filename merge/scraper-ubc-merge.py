import pandas as pd

# Input
df_program = pd.read_csv("ubc_website_data.csv")
df_course_details = pd.read_csv("ubc_course-details_data.csv")

# Get Program ID
program_row = df_program.iloc[0]
program_id = program_row["Program ID"]

# Add program metadata to each course
for col in df_program.columns:
    if col != "Program ID":
        df_course_details[col] = program_row[col]

# Add Program ID to all rows
df_course_details["Program ID"] = program_id

# Column order
final_columns = [
    "Program ID", "Program Title", "Institution", "Location", "Language", "Study Format",
    "Duration", "Total Credits", "Degree Type", "Specialization", "Modality", "Tuition Fees",
    "Academic Admission Requirements", "Language Admission Requirements",
    "Course Code", "Course Title", "Course Credits", "Course Description", "Prerequisites"
]

# Validate column completeness
for col in final_columns:
    if col not in df_course_details.columns:
        df_course_details[col] = "Not Specified"

# Reorder and save
final_df = df_course_details[final_columns]
final_df.to_csv("ubc_merged_data.csv", index=False)

print("[OK] Merged data saved to 'ubc_merged_data.csv'")