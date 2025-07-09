import pandas as pd
import os
import glob
import matplotlib.pyplot as plt

# Define the path to the folder containing .txt files
folders_containing_data_files = {
    'Sample 1': '/Users/oysteinfjeldberg/Dropbox/Job search/2024 Job Search/250711; Dunia Technical Exercise/sample_1',
    'Sample 2': '/Users/oysteinfjeldberg/Dropbox/Job search/2024 Job Search/250711; Dunia Technical Exercise/sample_2'
}

# List to store individual DataFrames
df_list = []

possible_current_density_columns = ["i(A/cm²)", "Ampl(A)"]
possible_voltage_columns = ["E(V)", "Bias(V)"]
possible_time_columns = ["T(s)", "Time(Sec)"]

# Loop over each folder-label pair
for folder_name, folder_path in folders_containing_data_files.items():
    # Everything in this loop is for a given sample folder
    txt_files = glob.glob(os.path.join(folder_path, "*.txt")) # Create list of file paths to all .txt files in folders
    txt_files.sort()
    
    accumulated_test_time_so_far = 0
    for file in txt_files:
        # Everything in this loop is for a given .txt file
        try:
            df = pd.read_csv(file, engine='python', sep=r"\s+", on_bad_lines='skip')  # Automatically detect delimiter            
            df['source_file'] = os.path.basename(file) # Tag with file name
            df['source_folder'] = folder_name  # Tag with folder name
            
            # print("# of columns is ", len(df.columns) - 2, " in ", df['source_folder'].unique(), " during ", df['source_file'].unique())
            # print("Columns is ", df.columns, " in ", df['source_folder'].unique(), " during ", df['source_file'].unique())
            # if file[-9:] == "02-CV.txt":
            #     print(df)
            #     df.to_csv('/Users/oysteinfjeldberg/Dropbox/Programming/GitHub repositories/echem-data-processing/individual_file_sample_1_02_CV.csv', index=False)            
                # if folder_name == "Sample 1":
                #     df.to_csv('/Users/oysteinfjeldberg/Dropbox/Programming/GitHub repositories/echem-data-processing/individual_file_sample_1_02_CV.csv', index=False)            
                # else:
                #     df.to_csv('/Users/oysteinfjeldberg/Dropbox/Programming/GitHub repositories/echem-data-processing/individual_file_sample_2_02_CV.csv', index=False)                

            # Standardize current density column
            loop_number = 0
            for col in df.columns:
                if col.strip() in possible_current_density_columns:
                    df = df.rename(columns={col: "Current density (A/cm2)"})
                    break  # Stop after first match                            

                loop_number += 1
                if loop_number == len(df.columns):
                    if 'OCP' or 'OCV' in df['source_file']:
                        df['Current density (A/cm2)'] = 0 * len(df)
                    else:
                        df['Current density (A/cm2)'] = [None] * len(df)

            # Standardize name of column for voltage applied
            for col in df.columns:
                if col.strip() in possible_voltage_columns:
                    df = df.rename(columns={col: "Voltage (V)"})
                    break  # Stop after first match            

            # Standardize name of column for time since technique start
            for col in df.columns:
                if col.strip() in possible_time_columns:
                    df = df.rename(columns={col: "Time since technique start (s)"})
                    break  # Stop after first match            
            # Add column for time since test start
            df['Time since test start (s)'] = accumulated_test_time_so_far + df["Time since technique start (s)"]            
            # Update counter for testing time so far so that it's valid for next loop
            accumulated_test_time_so_far += df["Time since technique start (s)"].max()

            df_list.append(df)
            # print("Folder name is ", folder_name, "and file is ", os.path.basename(file))
        except Exception as e:
            print(f"Failed to read {file}: {e}")

# Combine all DataFrames into one
full_dataframe = pd.concat(df_list, ignore_index=True)

# for row in full_dataframe['Current density (A/cm2)']:
#     if isinstance(row, (int, float)) == False:
#         print(full_dataframe.iloc[int(row)])

full_dataframe.to_csv('/Users/oysteinfjeldberg/Dropbox/Programming/GitHub repositories/echem-data-processing/output.csv', index=False)

# Display or use the combined DataFrame
plt.figure(figsize=(10, 6))
plt.scatter(x=full_dataframe["Time since test start (s)"], y=full_dataframe["Voltage (V)"], color='b', label='Voltage (V)')
plt.scatter(x=full_dataframe["Time since test start (s)"], y=full_dataframe["Current density (A/cm2)"], color='g', label='Current (A/cm2)')
plt.xlabel("Time since test start (s)")
plt.ylabel("Value")
plt.title("Voltage and Current vs Time")
plt.legend()
plt.show()