import pandas as pd
from ydata_profiling import ProfileReport

# Load transformed data from the interim directory
df = pd.read_csv('data/interim/enco/enco_interim_tidy.csv')  # Replace with the correct interim file

# Generate the profiling report
profile = ProfileReport(df, title="ENCO Data Profiling Report", explorative=True)

# Save the report to the MkDocs 'docs/assets/' directory
profile.to_file('docs/assets/interim_enco_profiling_report.html')

print("Profiling report saved to docs/assets/interim_enco_profiling_report.html")

# Load transformed data from the interim directory
df2 = pd.read_csv('data/interim/enigh/enigh_tidy_data.csv')  # Replace with the correct interim file

# Generate the profiling report
profile = ProfileReport(df, title="ENIGH Data Profiling Report", explorative=True)

# Save the report to the MkDocs 'docs/assets/' directory
profile.to_file('docs/assets/interim_enigh_profiling_report.html')

print("Profiling report saved to docs/assets/interim_enigh_profiling_report.html")