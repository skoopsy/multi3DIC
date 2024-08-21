import pandas as pd
import numpy as np
import plotly.figure_factory as ff
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

    :param  path :string
    :param  import_type :string
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


def create_delaunay_mesh(DICDataset):
    """
    Construct a Delaunay triangular mesh from a DICDataset with x,y
    coordinates as an attribute in the DICDataset object.

    Only uses x, y points for delaunay tesselation.

    :param DICDataset :DICDataset object
    :return: None
    """
    # Create array of 2d points (xy)
    points_2d = np.vstack([DICDataset.x, DICDataset.y]).T

    # Use Delaunay meshing to connect 2d points
    tri = Delaunay(points_2d)
    DICDataset.simplices = tri.simplices

    return None


def plot_delaunay_mesh(x, y, z, simplices, z_scale=1):
    # Just for testing, using go for strain map.
    fig = ff.create_trisurf(x=x, y=y, z=z,
                            simplices=simplices,
                            title="DIC Surface Map",
                            aspectratio=dict(x=1, y=1, z=z_scale))
    fig.show()

    return None


def plot_delaunay_mesh_strain(x, y, z, simplices, strain, plot_save_path, z_scale=1):
    # Create trisurface plot
    mesh = go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=simplices[:, 0],
        j=simplices[:, 1],
        k=simplices[:, 2],
        intensity=strain,
        cmin = 0,
        cmax = 2,
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
        title="DIC Surface Map CAM3-4",
        autosize=False,
        width=250,
        height=250,
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=30,
            pad=4
        )
    )

    # Create the figure and plot
    fig = go.Figure(data=[mesh], layout=layout)
    fig.show()
    fig.write_html(plot_save_path, full_html=False, include_plotlyjs='cdn')

    return None

def filter_strain0_data(DICDataset):
    """
    Fixes Region of Interest (ROI) issue where the mesh is the full
    resolution of the camera which captures noise. This removes
    data points which correspond to a zero strain reading.

    This could bite back if the ROI has areas of 0 strain, but
    due to noise the measurements are unlikely to == 0.
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

    data = import_data(path='test_files/cam3-4/vector_field_export_cam3-4-0001.csv',
                       import_type='LAVision')
    create_delaunay_mesh(data)
    filter_strain0_data(data)

    data1 = import_data(path='test_files/cam2-3/vector_field_export_cam2-3-0001.csv',
                       import_type='LAVision')
    create_delaunay_mesh(data1)
    filter_strain0_data(data1)

    data2 = import_data(path='test_files/cam1-2/vector_field_export_cam1-2-0001.csv',
                        import_type='LAVision')
    create_delaunay_mesh(data2)
    filter_strain0_data(data2)

    #plot_delaunay_mesh_strain(x=data.x_filtered,
    #                          y=data.y_filtered,
    #                          z=data.z_filtered,
    #                          simplices=data.simplices_filtered,
    #                          strain=data.strain_filtered,
    #
    #                          plot_save_path='plots/3d_plot_single_stereo_pair_filtered_cam3-4.html')

    plot_save_path='plots/3d_plot_single_stereo_pair_filtered_combined.html'
    z_scale=0.3
    # Create trisurface plot
    mesh = go.Mesh3d(
        x=data.x_filtered,
        y=data.y_filtered,
        z=data.z_filtered,
        i=data.simplices_filtered[:, 0],
        j=data.simplices_filtered[:, 1],
        k=data.simplices_filtered[:, 2],
        intensity=data.strain_filtered,
        cmin = 0,
        cmax = 2,
        colorscale='Viridis',
        colorbar=dict(title='Strain'),
        flatshading=True
    )

    # Set up layout with scaling
    layout = go.Layout(
        scene=dict(
            aspectmode='data',
            xaxis=dict(title='X [mm]'),
            yaxis=dict(title='Y [mm]'),
            zaxis=dict(title='Z [mm]'),
        ),
        title="DIC Surface Map Combined",
        autosize=False,
        width=500,
        height=500,
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=30,
            pad=4
        )
    )

    # Create the figure and plot
    fig = go.Figure(data=[mesh], layout=layout)
    fig.add_trace(go.Mesh3d(
        x=data1.x_filtered,
        y=data1.y_filtered,
        z=data1.z_filtered,
        i=data1.simplices_filtered[:, 0],
        j=data1.simplices_filtered[:, 1],
        k=data1.simplices_filtered[:, 2],
        intensity=data1.strain_filtered,
        cmin=0,
        cmax=2,
        colorscale='Viridis',
        showscale=False

    ))

    fig.add_trace(go.Mesh3d(
        x=data2.x_filtered,
        y=data2.y_filtered,
        z=data2.z_filtered,
        i=data2.simplices_filtered[:, 0],
        j=data2.simplices_filtered[:, 1],
        k=data2.simplices_filtered[:, 2],
        intensity=data2.strain_filtered,
        cmin=0,
        cmax=2,
        colorscale='Viridis',
        showscale=False

    ))
    fig.show()
    fig.write_html(plot_save_path, full_html=False, include_plotlyjs='cdn')
