from modules.processing import create_delaunay_mesh, filter_strain0_data
from modules.plotting import create_animated_mesh


def mesh_filter_plot_combined(datasets):

    # Create Delaunay meshes and filter for all timesteps of all stereo pairs:
    for stereo_pair in datasets:
        for timestep in stereo_pair:
            create_delaunay_mesh(timestep)
            filter_strain0_data(timestep)

    # Plot the meshes per timestep in interactive plot
    create_animated_mesh(datasets, z_scale=1)
