import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.spatial import Delaunay
import sys
sys.path.append("..")


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
        self.trisurface = None  # Depreciate
        self.simplices = None
        self.simplices_filtered = None


def import_data(path, import_type):
    """
    Loads a vector field file into a DICDataset object. The vector field file is assumed
    to have been produced by DIC software producing xyz coordinates along with the
    associated strain values. This import currently imports a single timestep.

    :param  path :str
    :param  import_type :str
    :return: None
    """
    csv_df = pd.read_csv(path)

    # Instantiate class to store data
    dic_data = DICDataset()

    if import_type == 'LAVision':
        # Put data in numpy arrays
        dic_data.x = csv_df['x[mm]'].to_numpy()
        dic_data.y = csv_df['y[mm]'].to_numpy()
        dic_data.z = csv_df['z[mm]'].to_numpy()
        dic_data.strain = csv_df['Maximum normal strain - RC[S]'].to_numpy()

    return dic_data


def filter_strain0_data(DICDataset):
    """
    Fixes Region of Interest (ROI) issue where the mesh is the full
    resolution of the camera which captures noise. This removes
    data points which correspond to a zero strain reading.

    This could bite back if the ROI has areas of 0 strain, but
    due to noise the measurements are unlikely to == 0.
    """
    mask = DICDataset.strain != 0
    DICDataset.x_filtered = DICDataset.x[mask]
    DICDataset.y_filtered = DICDataset.y[mask]
    DICDataset.z_filtered = DICDataset.z[mask]
    DICDataset.strain_filtered = DICDataset.strain[mask]

    # Create mapping from old indices to new
    # index_map = np.zeros_like(mask, dtype=int)
    # index_map[mask] = np.arange(len(DICDataset.x_filtered))

    # Filter simplices to remove any that contain removed points
    # DICDataset.simplices_filtered = []
    # for simplex in DICDataset.simplices:
    #    if mask[simplex].all():  # Only keep simplices where all points are kept
    #        DICDataset.simplices_filtered.append(index_map[simplex])

    # DICDataset.simplices_filtered = np.array(DICDataset.simplices_filtered)

    return None


def compute_delaunay_mesh(DICDataset, filtered: bool = False):
    """
    Construct a Delaunay triangular mesh from a DICDataset with x,y,z
    coordinates as an attribute in the DICDataset object.

    :param DICDataset :DICDataset object
    :return: None
    """
    if filtered:
        points_2d = np.vstack((DICDataset.x_filtered, DICDataset.y_filtered)).T
    else:
        points_2d = np.vstack((DICDataset.x, DICDataset.y)).T

    delaunay = Delaunay(points_2d)
    DICDataset.simplices_filtered = delaunay.simplices


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
def combine_stereo_pairs(meshes):
    all_data = DICDataset
    vertext_offset = 0
    all_data.x = []
    all_data.y = []
    all_data.z = []
    all_data.strain = []

    for mesh in meshes:
        all_data.x.append(mesh.x)
        all_data.y.append(mesh.y)
        all_data.z.append(mesh.z)
        all_data.strain.append(mesh.strain)

    return all_data

if __name__ == '__main__':

    data1 = import_data(path='test_files/vector_field_export_cam1-2-0001.csv',
                        import_type='LAVision')
    data2 = import_data(path='test_files/vector_field_export_cam2-3-0001.csv',
                        import_type='LAVision')
    data3 = import_data(path='test_files/vector_field_export_cam3-4-0001.csv',
                        import_type='LAVision')

    all_data = combine_stereo_pairs([data1, data2, data3])
    filter_strain0_data(all_data)
    compute_delaunay_mesh(all_data, filtered=True)

    plot_delaunay_mesh_strain(x=all_data.x_filtered, y=all_data.y_filtered,
                              z=all_data.z_filtered,
                              simplices=all_data.simplices_filtered,
                              strain=all_data.strain_filtered)
