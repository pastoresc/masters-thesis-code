import pandas as pd

# Input and output
website_file = "uoh_website_data.csv"
courses_file = "uoh_course_data.csv"
course_details_file = "uoh_course_details_data.csv"

output_file = "uoh_merged_data.csv"

# Load data
website_df = pd.read_csv(website_file)
courses_df = pd.read_csv(courses_file)
course_details_df = pd.read_csv(course_details_file)

# Prepare course code in lowercase for consistent merging
courses_df['Course Code'] = courses_df['Course Code'].str.strip().str.lower()
course_details_df['Course Code'] = course_details_df['Course Code'].str.strip().str.lower()

# Merge courses with course details
merged_courses = pd.merge(
    courses_df,
    course_details_df,
    on='Course Code',
    how='left',
    suffixes=('', '_details')
)

# Restore Course Code to uppercase after merge
merged_courses['Course Code'] = merged_courses['Course Code'].str.upper()

# Extract program info to populate all course rows
program_id = website_df.at[0, 'Program ID'] if 'Program ID' in website_df.columns else 'UOH001'
program_title = website_df.at[0, 'Program Title'] if 'Program Title' in website_df.columns else ''
institution = website_df.at[0, 'Institution'] if 'Institution' in website_df.columns else ''
location = website_df.at[0, 'Location'] if 'Location' in website_df.columns else ''
language = website_df.at[0, 'Language'] if 'Language' in website_df.columns else ''
study_format = website_df.at[0, 'Study Format'] if 'Study Format' in website_df.columns else ''
duration = website_df.at[0, 'Duration'] if 'Duration' in website_df.columns else ''
total_credits = website_df.at[0, 'Total Credits'] if 'Total Credits' in website_df.columns else ''
degree_type = website_df.at[0, 'Degree Type'] if 'Degree Type' in website_df.columns else ''
specialization = website_df.at[0, 'Specialization'] if 'Specialization' in website_df.columns else ''
modality = website_df.at[0, 'Modality'] if 'Modality' in website_df.columns else ''
tuition_fees = website_df.at[0, 'Tuition Fees'] if 'Tuition Fees' in website_df.columns else ''
academic_admission = website_df.at[0, 'Academic Admission Requirements'] if 'Academic Admission Requirements' in website_df.columns else ''
language_admission = website_df.at[0, 'Language Admission Requirements'] if 'Language Admission Requirements' in website_df.columns else ''

# Fill program-wide attributes across all course rows
merged_courses['Program ID'] = program_id
merged_courses['Program Title'] = program_title
merged_courses['Institution'] = institution
merged_courses['Location'] = location
merged_courses['Language'] = language
merged_courses['Study Format'] = study_format
merged_courses['Duration'] = duration
merged_courses['Total Credits'] = total_credits
merged_courses['Degree Type'] = degree_type
merged_courses['Specialization'] = specialization
merged_courses['Modality'] = modality
merged_courses['Tuition Fees'] = tuition_fees
merged_courses['Academic Admission Requirements'] = academic_admission
merged_courses['Language Admission Requirements'] = language_admission

# Reorder columns for output
final_columns = [
    "Program ID", "Program Title", "Institution", "Location", "Language", "Study Format",
    "Duration", "Total Credits", "Degree Type", "Specialization", "Modality", "Tuition Fees",
    "Academic Admission Requirements", "Language Admission Requirements",
    "Course Code", "Course Title", "Course Credits", "Course Description", "Prerequisites"
]

merged_courses = merged_courses[final_columns]

# Save to CSV
merged_courses.to_csv(output_file, index=False)
print(f"[OK] Merged data saved to '{output_file}' with {len(merged_courses)} entries.")