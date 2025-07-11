import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import re
import matplotlib.cm as cm

# Decide what to plot among the following options:
# Option 1: 'I & V vs t for full data set' --> Includes all data
# Option 2: 'V vs t at 1 A/cm2' --> Includes only 1 A/cm2 data points regardless of technique (includes 1 A/cm2 during CP, CV, OCP, OCV, and EIS)
# Option 3: 'V vs t at 1 A/cm2 during CP' --> Includes only 1 A/cm2 data points during CP technique (excludes 1 A/cm2 during CV, OCP, OCV, and EIS)
# Option 4: 'CV'
# Option 5: 'GEIS at 1 A/cm2'
What_to_plot = 'I & V vs t for full data set'

# Define the path to the folder containing .txt files
folders_containing_data_files = {
    'Sample 1': '/Users/oysteinfjeldberg/Dropbox/Job search/2024 Job Search/250711; Dunia Technical Exercise/sample_1',
    'Sample 2': '/Users/oysteinfjeldberg/Dropbox/Job search/2024 Job Search/250711; Dunia Technical Exercise/sample_2'
}

# List to store individual DataFrames
df_list = []

current_density_label = "Current density (A/cm2)"
voltage_label = "Voltage (V)"
test_time_label = "Time since test start (s)"
technique_time_label = "Time since technique start (s)"
file_label = "source_file"
folder_label = "source_folder"
technique_label = "Technique"
Z_real_label = 'Z, real (ohm*cm2)'
Z_imaginary_label = '-Z, imaginary (ohm*cm2)'

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

            file_name = os.path.basename(file) # Tag with file name
            df[file_label] = file_name
            df[folder_label] = folder_name  # Tag with folder name

            # Classify as technique
            match = re.search(r'-(.*?)([-.])', file_name)
            if match:
                df[technique_label] = match.group(1)
            else:
                df[technique_label] = "Unknown"


            # if '-' in file_name:
            #     technique_raw = file_name.split('-', 1)[1]  # Split only at the first hyphen
            #     df[technique_label] = technique_raw.removesuffix('.txt')
            # else:
            #     df[technique_label] = "Unknown"

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
                    df = df.rename(columns={col: current_density_label})
                    break  # Stop after first match                            

                loop_number += 1
                if loop_number == len(df.columns):
                    if 'OCP' in df[file_label] or 'OCV' in df[file_label]:
                        df[current_density_label] = 0 * len(df)
                    else:
                        df[current_density_label] = [None] * len(df)

            if current_density_label in df.columns:
                if df[technique_label].iloc[0] == 'GEIS':
                    df[current_density_label] *= 10

            # Standardize name of column for voltage applied
            for col in df.columns:
                if col.strip() in possible_voltage_columns:
                    df = df.rename(columns={col: voltage_label})
                    break  # Stop after first match            

            # Standardize name of column for time since technique start
            for col in df.columns:
                if col.strip() in possible_time_columns:
                    df = df.rename(columns={col: technique_time_label})
                    break  # Stop after first match            
            # Add column for time since test start
            df[test_time_label] = accumulated_test_time_so_far + df[technique_time_label]            
            # Update counter for testing time so far so that it's valid for next loop
            accumulated_test_time_so_far += df[technique_time_label].max()

            # Standardize name of column for Z' and Z''
            for col in df.columns:
                if col.strip() == "Z'(Ohm.cm²)":
                    df = df.rename(columns={col: Z_real_label})
                    break  # Stop after first match            
            for col in df.columns:
                if col.strip() == "Z''(Ohm.cm²)":
                    df = df.rename(columns={col: Z_imaginary_label})
                    break  # Stop after first match            
            
            if Z_imaginary_label in df.columns:
                df[Z_imaginary_label] = -1 * df[Z_imaginary_label]

            df_list.append(df)
            # print("Folder name is ", folder_name, "and file is ", os.path.basename(file))
        except Exception as e:
            print(f"Failed to read {file}: {e}")

# Combine all dataframes into one
full_dataframe = pd.concat(df_list, ignore_index=True)
full_dataframe.to_csv('/Users/oysteinfjeldberg/Dropbox/Programming/GitHub repositories/echem-data-processing/output.csv', index=False)

target_current = 1.00
# V_vs_t_at_1A_df = full_dataframe[full_dataframe[current_density_label].round(2) == target_current]

CV_dataframe = full_dataframe[full_dataframe[technique_label] == 'CV']
CV_dataframe_BOL = CV_dataframe[full_dataframe[test_time_label] < 8000]
CV_dataframe_EOL = CV_dataframe[full_dataframe[test_time_label] > 49000]
EIS_dataframe = full_dataframe[full_dataframe[technique_label].isin(['GEIS', 'PEIS'])]
PEIS_dataframe = full_dataframe[full_dataframe[technique_label] == 'PEIS']
GEIS_dataframe = full_dataframe[full_dataframe[technique_label] == 'GEIS']
GEIS_dataframe_at_1Acm2 = full_dataframe[(full_dataframe[technique_label] == 'GEIS') & (full_dataframe[current_density_label].round(2) == target_current)]

# Option 1: 'I & V vs t for full data set' --> Includes all data
# Option 2: 'V vs t at 1 A/cm2' --> Includes only 1 A/cm2 data points regardless of technique (includes 1 A/cm2 during CP, CV, OCP, OCV, and EIS)
# Option 3: 'V vs t at 1 A/cm2 during CP' --> Includes only 1 A/cm2 data points during CP technique (excludes 1 A/cm2 during CV, OCP, OCV, and EIS)
# Option 4: 'CV'
# Option 5: 'EIS'

plt.close('all')
if What_to_plot == 'I & V vs t for full data set':
    # Plot I and V vs time
    fig, axs = plt.subplots(2, figsize=(10, 8), sharex=True)
    fig.suptitle("Electrochemical performance vs time by sample")
    for sample, group in full_dataframe.groupby(folder_label):
        axs[0].scatter(group[test_time_label], group[voltage_label], label=sample)
        axs[1].scatter(group[test_time_label], group[current_density_label], label=sample)
    axs[0].set_ylabel(voltage_label)
    axs[1].set_ylabel(current_density_label)
    axs[1].set_xlabel(test_time_label)
    axs[0].legend()
    axs[1].legend()
elif What_to_plot == 'CV':
    # Plot I vs V
    # Plot I vs V, colored by test time, vertically stacked by sample
    samples = CV_dataframe_BOL[folder_label].unique()
    fig, axs = plt.subplots(len(samples), 1, figsize=(10, 5 * len(samples)), sharex=True)
    fig.suptitle("CV: I vs V colored by test time", fontsize=16)

    # Ensure axs is always iterable
    if len(samples) == 1:
        axs = [axs]

    for ax, sample in zip(axs, samples):
        group = CV_dataframe_BOL[CV_dataframe_BOL[folder_label] == sample]
        scatter = ax.scatter(
            group[voltage_label],
            group[current_density_label],
            c=group[test_time_label],
            cmap='viridis',
            edgecolor='k',
            s=20
        )
        ax.set_title(sample)
        ax.set_ylabel(current_density_label)
        ax.grid(False)

    axs[-1].set_xlabel(voltage_label)
    plt.colorbar(scatter, ax=axs, label='Test time (s)', orientation='vertical')

    # fig, axs = plt.subplots(1, figsize=(10, 8), sharex=True)
    # fig.suptitle("I vs V by sample")
    # for sample, group in IV_dataframe.groupby(folder_label):
    #     axs.scatter(group[voltage_label], group[current_density_label], label=sample)
    # axs.set_ylabel(current_density_label)
    # axs.set_xlabel(voltage_label)
    # axs.legend()
elif What_to_plot == 'GEIS at 1 A/cm2':
    # Plot Nyquist
    # Get unique sample names
    samples = GEIS_dataframe_at_1Acm2[folder_label].unique()

    # Create one subplot per sample, stacked vertically
    # fig, axs = plt.subplots(len(samples), 1, figsize=(10, 5 * len(samples)), sharex=True)
    fig, axs = plt.subplots(len(samples), 1, figsize=(10, 5 * len(samples)), sharex=True)
    # Get global y-limits across all samples to unify them
    global_ymin = GEIS_dataframe_at_1Acm2[Z_imaginary_label].min()
    global_ymax = GEIS_dataframe_at_1Acm2[Z_imaginary_label].max()

    fig.suptitle("EIS Nyquist plot colored by test time", fontsize=16)

    if len(samples) == 0:
        raise ValueError("No samples found in GEIS_dataframe_at_1Acm2. Check your filtering logic.")

    # If there's only one sample, axs is not a list — convert to list for consistency
    if len(samples) == 1:
        axs = [axs]

    # Plot each sample separately
    for ax, sample in zip(axs, samples):
        group = GEIS_dataframe_at_1Acm2[GEIS_dataframe_at_1Acm2[folder_label] == sample]
        scatter = ax.scatter(
            group[Z_real_label],
            group[Z_imaginary_label],
            c=group[test_time_label],
            cmap='viridis',
            edgecolor='k',
            s=20
        )
        ax.set_title(sample)
        ax.set_ylabel(Z_imaginary_label)
        ax.set_ylim(global_ymin, global_ymax)  # Apply shared y-limits
        ax.set_aspect('equal', adjustable='box')  # Square aspect
        ax.grid(True)

    # for ax, sample in zip(axs, samples):
    #     group = GEIS_dataframe_at_1Acm2[GEIS_dataframe_at_1Acm2[folder_label] == sample]
    #     scatter = ax.scatter(
    #         group[Z_real_label],
    #         group[Z_imaginary_label],
    #         c=group[test_time_label],
    #         cmap='viridis',
    #         edgecolor='k',
    #         s=20
    #     )
    #     ax.set_title(sample)
    #     ax.set_ylabel(Z_imaginary_label)
    #     ax.grid(True)

    axs[-1].set_xlabel(Z_real_label)

    cbar = fig.colorbar(scatter, ax=axs, label='Test time (s)', orientation='vertical', shrink=0.9, pad=0.02)

    # plt.colorbar(scatter, ax=axs, label='Test time (s)', orientation='vertical')    
    
    # fig, axs = plt.subplots(1, figsize=(10, 8), sharex=True)
    # fig.suptitle("EIS")
    # for sample, group in GEIS_dataframe.groupby(folder_label):
    #     axs.scatter(group[Z_real_label], group[Z_imaginary_label], label=sample)
    # axs.set_ylabel(Z_imaginary_label)
    # axs.set_xlabel(Z_real_label)

# Show plot
plt.tight_layout()
plt.show()