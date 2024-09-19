from modules.processing import (create_delaunay_mesh, filter_strain0_data,
                                filter_strain0_points,
                                combine_filtered_stereo_pairs,
                                combine_unfiltered_stereo_pairs)
from modules import plotting


def timesteps_combine_filter_neighbours_mesh_filter_plot(datasets):
    """
    Method:
    1. Combine point clouds
    2. Check nearest neighbours of combined point cloud.
        - If the nearest neighbours are all == 0 strain then keep.
        - If a nearest neighbour == 0 strain but others are not:
            - Remove strain==0 point
    3. Run Delaunay tesselation
    4. Filter 0 strain
    5. Plot

    This may remove the issues with mesh_filter_plot_combined().
    """
    return None


def timestep_mesh_filter_plot_overlay(datasets, timestep_index: int, plot_save_path=None):
    """
    For a single time step:
    1. Delaunay mesh on each stereo pair
    2. filter simplicies with strain == 0 points
    3. Plot all 3 meshes on same plot
    """

    for dataset in datasets:
        data = dataset[timestep_index]
        create_delaunay_mesh(data)
        filter_strain0_data(data)

    plotting.multiple_meshes_single_timestep(datasets=datasets,
                                             timestep_index=timestep_index,
                                             plot_save_path=plot_save_path,
                                             z_scale=1)
    return None


def timesteps_mesh_filter_plot_overlay(datasets, plot_save_path=None):
    """
    Method:
    1. 3 sets of point clouds
    2. Delaunay tesselate individual sets
    3. Filter delaunay simplicies with strain == 0 points
    4. Plot 3 mesh sets on top of each other
    """
    print(str(20*'='))
    print(f"Starting timestep mesh filtering overlay for {len(datasets)} datasets")

    # Create Delaunay meshes and filter for all timesteps of all stereo pairs:
    for stereo_pair in datasets:
        for timestep in stereo_pair:
            create_delaunay_mesh(timestep)
            print(f"mesh created for stereo_pair, timestep {timestep}")
            filter_strain0_data(timestep)
            print(f"filtering strain 0 for stereo_pair, timestep {timestep}")
    # Plot the meshes per timestep in interactive plot
    plotting.create_animated_mesh(datasets, z_scale=1, plot_save_path=plot_save_path)


def timesteps_combine_mesh_filter_plot(datasets):
    """
    Method:
    1. Combine point clouds
    2. Delaunay tesselation
    3. Filter simplicies with strain == 0 points
    4. Plot
    This seems to have an issue where there are so many strain == 0 points
    mixed with good points that most simplicies are removed.
    """
    return None


def timestep_combine_filter_plot_scatter(datasets, timestep_index, plot_save_path=None):
    """
    Method:
    1. Combine point clouds
    2. Filter out strain == 0 points
    3. Plot combination as scatter plot

    :param datasets:
    :param timestep_index:
    :param plot_save_path:
    :return:
    """
    print(str(20 * '='))
    print(f"Starting timestep mesh filtering overlay for {len(datasets)} datasets")

    datasets = [dataset[timestep_index] for dataset in datasets]
    combined_data = combine_unfiltered_stereo_pairs(datasets)
    print("stereo pairs combined")
    filter_strain0_points(combined_data)
    print("filtered points")
    plotting.plot_scatter_points(combined_data, plot_save_path)
    print("scatter points")

    return None
