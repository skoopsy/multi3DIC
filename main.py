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
        self.delaunay = None
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
    index_map = np.zeros_like(mask, dtype=int)
    index_map[mask] = np.arange(len(DICDataset.x_filtered))

    # Filter simplices to remove any that contain removed points
    DICDataset.simplices_filtered = []
    for simplex in DICDataset.simplices:
        if mask[simplex].all():  # Only keep simplices where all points are kept
            DICDataset.simplices_filtered.append(index_map[simplex])

    DICDataset.simplices_filtered = np.array(DICDataset.simplices_filtered)

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

    DICDataset.delaunay = Delaunay(points_2d)
    DICDataset.simplices = DICDataset.delaunay.simplices

def filter_delaunay_mesh_strain(dicdataset):

    filter_bool = dicdataset.strain != 0
    filtered_simplices = []
    for simplex in dicdataset.delaunay.simplices:
        if all(filter_bool[i] for i in simplex):
            filtered_simplices.append(simplex)

    dicdataset.simplices_filtered = np.array(filtered_simplices)

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

    x_list = []
    y_list = []
    z_list = []
    strain_list = []

    for mesh in meshes:
        x_list.append(mesh.x)
        y_list.append(mesh.y)
        z_list.append(mesh.z)
        strain_list.append(mesh.strain)

    # Combine the lists of numpy arrays into single numpy arrays
    all_data.x = np.concatenate(x_list)
    all_data.y = np.concatenate(y_list)
    all_data.z = np.concatenate(z_list)
    all_data.strain = np.concatenate(strain_list)

    return all_data


import matplotlib.pyplot as plt
import matplotlib.tri as tri
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.figure_factory as ff

def plot_delaunay_meshes(x_list, y_list, z_list, simplices_list, strain_list):
    fig = go.Figure()

    for x, y, z, simplices, strain in zip(x_list, y_list, z_list, simplices_list,
                                          strain_list):
        # Create a Delaunay triangulation
        tri = Delaunay(np.vstack([x, y]).T)
        simplices = tri.simplices

        # Mesh3d requires i, j, k indices for vertices of each face
        i, j, k = simplices[:, 0], simplices[:, 1], simplices[:, 2]

        # Add the mesh3d trace to the figure
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            intensity=strain, colorscale='Viridis', colorbar=dict(title='Strain'),
            opacity=0.5
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z'
        ),
        title='Multi 3D Stereo DIC Pairs - Strain'
    )
    fig.show()


if __name__ == '__main__':

    data1 = import_data(path='test_files/vector_field_export_cam1-2-0001.csv',
                        import_type='LAVision')
    data2 = import_data(path='test_files/vector_field_export_cam2-3-0001.csv',
                        import_type='LAVision')
    data3 = import_data(path='test_files/vector_field_export_cam3-4-0001.csv',
                        import_type='LAVision')

    all_data = combine_stereo_pairs([data1, data2, data3])
    #filter_strain0_data(all_data)
    compute_delaunay_mesh(all_data)
    filter_delaunay_mesh_strain(all_data)

    filtered=False
    if filtered:
        plot_delaunay_mesh_strain(x=all_data.x_filtered,
                                  y=all_data.y_filtered,
                                  z=all_data.z_filtered,
                                  simplices=all_data.simplices,
                                  strain=all_data.strain_filtered,
                                  z_scale=0.5)
    else:
        plot_delaunay_mesh_strain(x=all_data.x,
                                  y=all_data.y,
                                  z=all_data.z,
                                  simplices=all_data.simplices_filtered,
                                  strain=all_data.strain)

    # Plot single datasets
    for data in [data1,data2,data3]:
        compute_delaunay_mesh(data)
        filter_strain0_data(data)
        plot_delaunay_mesh_strain(x=data.x_filtered,
                              y=data.y_filtered,
                              z=data.z_filtered,
                              simplices=data.simplices_filtered,
                              strain=data.strain_filtered)

    # Initialize lists to hold data for each dataset
    x_list = []
    y_list = []
    z_list = []
    simplices_list = []
    strain_list = []

    # Collect data from each dataset
    for data in [data1, data2, data3]:
        compute_delaunay_mesh(data)
        filter_strain0_data(data)

        x_list.append(data.x_filtered)
        y_list.append(data.y_filtered)
        z_list.append(data.z_filtered)
        simplices_list.append(data.simplices_filtered)
        strain_list.append(data.strain_filtered)

    # Plot all datasets on the same plot
    plot_delaunay_meshes(x_list, y_list, z_list, simplices_list, strain_list)