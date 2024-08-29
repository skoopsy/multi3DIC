from pathlib import Path  # Importing filenames
import pandas as pd

from modules.classes import DICDataset, Config


def get_csv_file_paths(directories: list[str]) -> list[list[str]]:
    """ for given directories imports all csv files into a list where each element is
    the directory"""

    dataset_paths = [
        sorted(
            [str(file) for file in Path(directory).iterdir() if file.suffix == ".csv"],
            key=lambda x: Path(x).stem  # Sort alphanumerically
        )
        for directory in directories
    ]

    # Check len of files is same for each directory
    file_cnt = [len(dataset) for dataset in dataset_paths]
    if len(set(file_cnt)) != 1:
        print(f"Warning: Found {len(set(file_cnt))} files in {directories}")

    return dataset_paths


def import_data(path, import_type: str, config: Config) -> DICDataset:
    """
    Loads a vector field file into a DICDataset object and puts it in a list. The vector
    field file is assumed to have been produced by DIC software producing xyz
    coordinates along with the associated strain values. This import currently imports
    a single timestep.

    """
    # Initialise
    imported_data = DICDataset()

    csv_df = pd.read_csv(path)

    if config.debug:
        print(config.print_sep)
        print(f"Loaded: {path}")
        print(f"Shape: {csv_df.shape}")
        print(f"Columns Found: {csv_df.columns}")

    if import_type == 'LAVision':

        # Check columns and place data into lists of separate numpy arrays
        expected_cols = ['x[mm]', 'y[mm]', 'z[mm]', 'Maximum normal strain - RC[S]']
        if all(col in csv_df.columns for col in expected_cols):
            imported_data.x = csv_df["x[mm]"].to_numpy()
            imported_data.y = csv_df["y[mm]"].to_numpy()
            imported_data.z = csv_df["z[mm]"].to_numpy()
            imported_data.strain = csv_df["Maximum normal strain - RC[""S]"].to_numpy()
        else:
            print(f"Warning: Missing columns in {path}. Columns expected: "
                  f"{expected_cols}")
    else:
        print(f"Warning: incorrect import_type: {import_type}")

    return imported_data

def load_multiple_stereo_pairs(stereo_pair_dirs: list[str], config: Config):

    stereo_pair_fpaths = get_csv_file_paths(stereo_pair_dirs)

    # Put each dataset with all timesteps in a list of stereo pairs where each index is a
    # stereo pair, and each stereo pair is a list of timesteps for that pair.
    datasets = [[import_data(path=timestep, import_type='LAVision', config=config)
                 for timestep in stereo_pair]
                for stereo_pair in stereo_pair_fpaths]

    return datasets