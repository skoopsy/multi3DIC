import pandas as pd
import numpy as np


class Config:
    """ General configuration class for prototyping"""
    debugging = True
    print_sep = str(50 * "=")

class ImportedDICDataset:
    """ Imported dataset class"""
    def __init__(self):
        self.x = []
        self.y = []
        self.z = []
        self.strain = []

class DICDataset:
    """ Main dataset class"""
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.strain = None


conf = Config()


def import_and_combine_timestep(paths: list[str], import_type: str, config: Config()):

    # Initialise
    importedData = ImportedDICDataset()

    importedData.x = []
    importedData.y = []
    importedData.z = []
    importedData.strain = []

    # Iterate through files
    for path in paths:

        csv_df = pd.read_csv(path)

        if config.debugging:
            print(config.print_sep)
            print(f"Loaded: {path}")
            print(f"Shape: {csv_df.shape}")
            print(f"Columns Found: {csv_df.columns}")
            print(config.print_sep)

        if import_type == 'LAVision':

            # Check columns and import data
            expected_cols = ['x[mm]', 'y[mm]', 'z[mm]', 'Maximum normal strain - RC[S]']
            if all(col in csv_df.columns for col in expected_cols):
                importedData.x.append(csv_df["x[mm]"].to_numpy())
                importedData.y.append(csv_df["y[mm]"].to_numpy())
                importedData.z.append(csv_df["z[mm]"].to_numpy())
                importedData.strain.append(csv_df[("Maximum normal strain - RC["
                                                 "S]")].to_numpy())
            else:
                print(f"Warning: Missing columns in {path}. Columns expected: "
                      f"{expected_cols}")

    break_point = 0
    return importedData


def merge_datasets(ImportedDICDataset):
    return None

file_paths = ['test_files/vector_field_export_cam1-2-0001.csv',
              'test_files/vector_field_export_cam2-3-0001.csv',
              'test_files/vector_field_export_cam3-4-0001.csv',]

importedData = import_and_combine_timestep(paths=file_paths,
                                           import_type='LAVision',
                                           config=conf)
data = merge_datasets(importedData)

break_point=0
