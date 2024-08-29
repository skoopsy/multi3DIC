import numpy as np
from scipy.spatial import Delaunay


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


def filter_strain0_data(DICDataset):
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
