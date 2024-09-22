import numpy as np
from scipy.spatial import Delaunay

from modules import classes
from modules.classes import DICDataset


def create_delaunay_mesh(DICDataset) -> None:
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


def filter_strain0_data(DICDataset) -> None:
    """
    Fixes Region of Interest (ROI) issue where the mesh is the full
    resolution of the camera which captures noise. This removes
    data points which correspond to a zero strain reading.

    This could bite back if the ROI has areas of 0 strain, but
    due to noise the measurements are unlikely to == 0.
    """
    try:
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
    except Exception as e:
        print(f"Warning: Could not filter {DICDataset}")
        print(f"Exception: {e}")
    return None

def combine_filtered_stereo_pairs(meshes):
    combined_data = DICDataset()

    combined_data.x_filtered = np.concatenate([mesh.x_filtered for mesh in meshes])
    combined_data.y_filtered = np.concatenate([mesh.y_filtered for mesh in meshes])
    combined_data.z_filtered = np.concatenate([mesh.z_filtered for mesh in meshes])
    combined_data.strain_filtered = np.concatenate([mesh.strain_filtered for mesh in meshes])

    return combined_data


def combine_unfiltered_stereo_pairs(meshes):
    combined_data = DICDataset()

    combined_data.x = np.concatenate([mesh.x for mesh in meshes])
    combined_data.y = np.concatenate([mesh.y for mesh in meshes])
    combined_data.z = np.concatenate([mesh.z for mesh in meshes])
    combined_data.strain = np.concatenate([mesh.strain for mesh in meshes])

    return combined_data


def filter_strain0_points(DICDataset) -> None:
    try:
        mask = DICDataset.strain != 0
        DICDataset.x = DICDataset.x[mask]
        DICDataset.y = DICDataset.y[mask]
        DICDataset.z = DICDataset.z[mask]
        DICDataset.strain = DICDataset.strain[mask]
    except Exception as e:
        print(f"Warning: Could not filter {DICDataset}")
        print(f"Exception: {e}")

    return None