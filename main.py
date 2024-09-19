import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go
from scipy.spatial import Delaunay
import sys
sys.path.append("..")
import os

class DICDataset:
    """ Class to hold data from a stereo DIC dataset """
    def __init__(self):
        self.x = None
        self.x_filtered = None
        self.y = None
        self.y_filtered = None
        self.z = None
        self.z_filtered = None
        self.strain = None
        self.strain_filtered = None
        self.trisurface = None # Depreciate
        self.simplices = None
        self.simplices_filtered = None

def import_data(path, import_type):
    """
    Loads a vector field file into a
    DICDataset object.
    """
    csv_df = pd.read_csv(path)

    # Instantiate class to store data
    data = DICDataset()

    if import_type == 'LAVision':
        # Put data in numpy arrays
        data.x = csv_df['x[mm]'].to_numpy()
        data.y = csv_df['y[mm]'].to_numpy()
        data.z = csv_df['z[mm]'].to_numpy()
        data.strain = csv_df['Maximum normal strain - RC[S]'].to_numpy()

    return data

def create_delaunay_mesh(DICDataset):
    """
    Construct a Delaunay triangular mesh from a DICDataset with x,y,z
    coordinates as an attribute in the DICDataset object.

    :param DICDataset:
    :return: None
    """
    # Create array of 2d points (xy)
    points2D = np.vstack([DICDataset.x,DICDataset.y]).T

    # Use Delaunay meshing to connect 2d points
    tri = Delaunay(points2D)
    DICDataset.simplices = tri.simplices

    return None

def plot_delaunay_mesh(x,y,z,simplices, z_scale=1):
    # Just for testing, using go for strain map.
    fig = ff.create_trisurf(x=x, y=y, z=z,
                            simplices=simplices,
                            title="DIC Surface Map",
                            aspectratio=dict(x=1, y=1, z=z_scale))
    fig.show()

    return None

def plot_delaunay_mesh_strain(x, y, z, simplices, strain, z_scale=1):
    # Create trisurface plot
    mesh = go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=simplices[:, 0],
        j=simplices[:, 1],
        k=simplices[:, 2],
        intensity=strain,
        colorscale='Viridis',
        colorbar=dict(title='Strain'),
        flatshading=True
    )

    # Set up layout with scaling
    layout = go.Layout(
        scene=dict(
            aspectratio=dict(x=1, y=1, z=z_scale),
            xaxis=dict(title='X [mm]'),
            yaxis=dict(title='Y [mm]'),
            zaxis=dict(title='Z [mm]'),
        ),
        title="DIC Surface Map"
    )

    # Create the figure and plot
    fig = go.Figure(data=[mesh], layout=layout)
    fig.show()

    return None
def filter_strain0_data(DICDataset):
    """
    Fixes Region of interest issue where the mesh is the full
    resolution of the camera which captures noise. This removes
    data points which correspond to a zero strain reading.

    This could bite back if the ROI has areas of 0 strain but
    due to measurement noise I do not think the values will ever == 0.
    """

    # Filter out points where strain = 0
    mask = DICDataset.strain != 0
    DICDataset.x_filtered = DICDataset.x[mask]
    DICDataset.y_filtered = DICDataset.y[mask]
    DICDataset.z_filtered = DICDataset.z[mask]
    DICDataset.strain_filtered = DICDataset.strain[mask]

    # Create mapping from old indices to new
    index_map = np.zeros_like(mask, dtype=int)
    index_map[mask] = np.arange(len(DICDataset.x_filtered))

    # Filter simplices to remove any that contain removed points
    DICDataset.simplices_filtered = []
    for simplex in DICDataset.simplices:
        if mask[simplex].all():  # Only keep simplices where all points are kept
            DICDataset.simplices_filtered.append(index_map[simplex])

    DICDataset.simplices_filtered = np.array(DICDataset.simplices_filtered)

    return None


if __name__ == '__main__':

    data = import_data(path='test_files/vector_field_export_cam1-2-0001.csv',
                        import_type='LAVision')

    create_delaunay_mesh(data)

    filter_strain0_data(data)

    plot_delaunay_mesh_strain(x=data.x_filtered, y=data.y_filtered,
                              z=data.z_filtered,
                              simplices=data.simplices_filtered,
                              strain=data.strain_filtered)
