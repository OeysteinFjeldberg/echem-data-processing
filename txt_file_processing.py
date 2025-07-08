import pandas as pd
import os
import glob

# Define the path to the folder containing .txt files
folder_path_sample_1 = "/Users/oysteinfjeldberg/Dropbox/Job search/2024 Job Search/250711; Dunia Technical Exercise/sample_1"
folder_path_sample_2 = "/Users/oysteinfjeldberg/Dropbox/Job search/2024 Job Search/250711; Dunia Technical Exercise/sample_2"

# Use glob to get all .txt files in the folder
txt_files = glob.glob(os.path.join(folder_path_sample_1, "*.txt"))

# List to store individual DataFrames
df_list = []

# Read each file and append to the list
for file in txt_files:
    try:
        df = pd.read_csv(file, sep=None, engine='python')  # Automatically infers delimiter
        df['source_file'] = os.path.basename(file)  # Optionally tag each row with filename
        df_list.append(df)
    except Exception as e:
        print(f"Failed to read {file}: {e}")

# Combine all DataFrames into one
combined_df = pd.concat(df_list, ignore_index=True)

# Display or use the combined DataFrame
