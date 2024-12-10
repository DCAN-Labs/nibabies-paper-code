from glob import glob
import nibabel as nib
import pandas as pd
import argparse
import os
import re

def save_pconn_to_csv(pconn_file, output_file, delimiter=','):
    # Load the .pconn file using nibabel
    cifti = nib.load(pconn_file)
    
    # Get the data matrix
    data_matrix = cifti.get_fdata()

    # Extract ROI labels from cifti.header.get_index_map(1).parcels
    parcels_info = cifti.header.get_index_map(1).parcels
    roi_labels = [parcel.name for parcel in parcels_info]  # Get the names of the parcels

    # Check if ROI labels match the dimensions of the data matrix
    if len(roi_labels) != data_matrix.shape[0]:
        raise ValueError(f"Number of ROI labels ({len(roi_labels)}) does not match the data matrix dimensions {data_matrix.shape}.")

    # Convert the data matrix to a pandas DataFrame with ROI labels as headers, needed for headers file
    # df = pd.DataFrame(data_matrix, index=roi_labels, columns=roi_labels) 
    
    # Convert data matrix to DataFrame without ROI headers 
    df = pd.DataFrame(data_matrix)
    
    # Save the DataFrame to CSV/TSV
    df.to_csv(output_file, sep=delimiter, index=False, header=False)

    print(f"Data matrix saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a .pconn CIFTI file to a CSV or TSV file with ROI labels.")
    parser.add_argument("pconn_path", type=str, help="Path to the dir with .pconn.nii files to convert")
    parser.add_argument("output_path", type=str, help="Path to the output path to place CSV/TSV file")
    parser.add_argument("--delimiter", type=str, default=",", help="Delimiter for the output file, default is ',' for CSV. Use '\\t' for TSV.")

    args = parser.parse_args()

    paths = glob(os.path.join(args.pconn_path, "*.pconn.nii"))
    
    for path in paths:
        filename = path.split('/')[-1]
        match = re.match(r'^(sub-[A-Za-z0-9]+_ses-[A-Za-z0-9]+_task-[A-Za-z0-9]+_run-[0-9]+_)', filename)
        output_file = args.output_path + match.group(1) + "pconn.csv"
        save_pconn_to_csv(path, output_file, delimiter=args.delimiter)
