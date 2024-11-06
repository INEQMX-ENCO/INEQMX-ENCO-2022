import pandas as pd
from ydata_profiling import ProfileReport
#import sweetviz as sv

# Load transformed data from the interim directory for ENCO
df_enco = pd.read_csv('data/processed/enco/enco_interim_tidy.csv')  # Replace with the correct interim file

# Generate the profiling report using ydata-profiling
profile_enco_ydata = ProfileReport(df_enco, title="ENCO YData Profiling Report", explorative=True)

# Save the ydata-profiling report to the MkDocs 'docs/assets/' directory
profile_enco_ydata.to_file('docs/assets/processed_enco_profiling_report.html')

print("YData profiling report for ENCO saved to docs/assets/processed_enco_profiling_report.html")

# Generate the Sweetviz report for ENCO
#profile_enco_sweetviz = sv.analyze(df_enco)

# Save the Sweetviz report to the MkDocs 'docs/assets/' directory
#profile_enco_sweetviz.show_html('docs/assets/interim_enco_sweetviz_report.html')

#print("Sweetviz report for ENCO saved to docs/assets/interim_enco_sweetviz_report.html")


# Load transformed data from the interim directory for ENIGH
df_enigh = pd.read_csv('data/processed/enigh/enigh_processed_tidy.csv')  # Replace with the correct interim file

# Generate the profiling report using ydata-profiling
profile_enigh_ydata = ProfileReport(df_enigh, title="ENIGH YData Profiling Report", explorative=True)

# Save the ydata-profiling report to the MkDocs 'docs/assets/' directory
profile_enigh_ydata.to_file('docs/assets/processed_enigh_profiling_report.html')

print("YData profiling report for ENIGH saved to docs/assets/processed_enigh_profiling_report.html")

# Generate the Sweetviz report for ENIGH
#profile_enigh_sweetviz = sv.analyze(df_enigh)

# Save the Sweetviz report to the MkDocs 'docs/assets/' directory
#profile_enigh_sweetviz.show_html('docs/assets/interim_enigh_sweetviz_report.html')

#print("Sweetviz report for ENIGH saved to docs/assets/processed_enigh_sweetviz_report.html")