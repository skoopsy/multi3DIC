import pandas as pd
import numpy as np
from scipy.spatial import Delaunay # compute_delaunay_mesh()
import plotly.graph_objects as go # plot_mesh_interactive()


class Config:
    """ General configuration class for prototyping"""
    debugging = True
    print_sep = str(50 * "=")


class DICDataset:
    """ Main dataset class"""
    def __init__(self):
        self.x = None
        self.y = None
        self.z = None
        self.strain = None
        self.simplices = None


conf = Config()


def import_and_combine_timestep(paths: list[str], import_type: str, config: Config()):

    # Initialise
    imported_data = DICDataset()

    imported_data.x = []
    imported_data.y = []
    imported_data.z = []
    imported_data.strain = []

    # Iterate through files
    for path in paths:

        csv_df = pd.read_csv(path)

        if config.debugging:
            print(config.print_sep)
            print(f"Loaded: {path}")
            print(f"Shape: {csv_df.shape}")
            print(f"Columns Found: {csv_df.columns}")

        if import_type == 'LAVision':

            # Check columns and import data
            expected_cols = ['x[mm]', 'y[mm]', 'z[mm]', 'Maximum normal strain - RC[S]']
            if all(col in csv_df.columns for col in expected_cols):
                imported_data.x.append(csv_df["x[mm]"].to_numpy())
                imported_data.y.append(csv_df["y[mm]"].to_numpy())
                imported_data.z.append(csv_df["z[mm]"].to_numpy())
                imported_data.strain.append(csv_df["Maximum normal strain - RC[""S]"
                                                   ].to_numpy())
            else:
                print(f"Warning: Missing columns in {path}. Columns expected: "
                      f"{expected_cols}")

    return imported_data


def merge_datasets(imported_data: DICDataset):
    merged_data = DICDataset()

    merged_data.x = np.concatenate(imported_data.x, axis=0)
    merged_data.y = np.concatenate(imported_data.y, axis=0)
    merged_data.z = np.concatenate(imported_data.z, axis=0)
    merged_data.strain = np.concatenate(imported_data.strain, axis=0)

    if conf.debugging:
        i = len(imported_data.x)
        print(conf.print_sep)
        print(f"{i} datasets found and merged.")

    return merged_data


def filter_strain0(DICDataset):
    if conf.debugging:
        print(conf.print_sep)
        print("Filtering...")

    # Create boolean mask based on strain values
    mask = DICDataset.strain != 0

    # Filter everything with mask
    DICDataset.x = DICDataset.x[mask]
    DICDataset.y = DICDataset.y[mask]
    DICDataset.z = DICDataset.z[mask]
    DICDataset.strain = DICDataset.strain[mask]

    if conf.debugging:
        total_entries = len(mask)
        entries_removed = total_entries - np.count_nonzero(mask)
        print(f"Entries removed: {entries_removed} of {total_entries}")
        print(f"Entries remaining: {total_entries-entries_removed}")

    return None


def compute_delaunay_mesh(DICDataset):
    z = DICDataset.z
    points_2d = np.column_stack((DICDataset.x, DICDataset.y))
    tri = Delaunay(points_2d)

    DICDataset.simplices = tri.simplices

    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(points_2d[:, 0], points_2d[:, 1], z, triangles=tri.simplices,
                    cmap=plt.cm.Spectral)

    plt.show()
    
    return None


def plot_mesh_interactive(DICDataset):
    """
    Using plotly go.Mesh3D to make 3d interactive plot specified
    with custom triangles

    Note: If you only specify points then it will automatically perform
    a delaunay tessilation, we do not want that due to the filtering, in
    this case we specify i,j, and k.
    """

    fig = go.Figure(data=go.Mesh3d(x=DICDataset.x,
                                   y=DICDataset.y,
                                   z=DICDataset.z,
                                   i=DICDataset.simplices[:,0],
                                   j=DICDataset.simplices[:,1],
                                   k=DICDataset.simplices[:,2],
                                   intensity=DICDataset.strain,
                                   colorbar=dict(title='Strain'),
                                   opacity=0.9),
                    layout=go.Layout(title="DIC Surface Map (Automatic Delaunay "
                                           "Tessilation (Plotly)",
                                     scene=dict(
                                         xaxis=dict(title='X [mm]'),
                                         yaxis=dict(title='Y [mm]'),
                                         zaxis=dict(title='Z [mm]'),
                                     )
                                     ))
    fig.show()

    return None


file_paths = ['test_files/vector_field_export_cam1-2-0001.csv',
              'test_files/vector_field_export_cam2-3-0001.csv',
              'test_files/vector_field_export_cam3-4-0001.csv',]

imported_data = import_and_combine_timestep(paths=file_paths,
                                            import_type='LAVision',
                                            config=conf)
data = merge_datasets(imported_data)
filter_strain0(data)
compute_delaunay_mesh(data)
plot_mesh_interactive(data)
