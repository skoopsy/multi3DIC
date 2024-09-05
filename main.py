import sys

from modules import classes, importing, methods

if __name__ == '__main__':

    # Initialisation
    sys.path.append("..")
    CONF = classes.Config()

    # Stereo pair directories
    stereo_pair_dirs = ["test_files/cam1-2/",
                        "test_files/cam2-3/",
                        "test_files/cam3-4/"]

    # Import and organise data
    datasets = importing.load_multiple_stereo_pairs(stereo_pair_dirs=stereo_pair_dirs,
                                                    config=CONF)

    # Use one of the methods to process and plot data
    data_processing_method = 3
    match data_processing_method:
        case 1:
            # timestep: mesh -> filter -> plot overlay
            save_path = "plots/3d_plot_one_timestep_mesh_filter_plot_001.html"
            methods.timestep_mesh_filter_plot_overlay(datasets=datasets,
                                                      timestep_index=1,
                                                      plot_save_path=save_path)
        case 2:
            # timesteps: mesh -> filter -> plot overlay
            save_path = "plots/3d_plot_timesteps_mesh_filter_plot_001.html"
            methods.timesteps_mesh_filter_plot_overlay(datasets=datasets,
                                                       plot_save_path=save_path)
        case 3:
            # timestep: combine -> filter -> plot scatter
            save_path = "plots/3d_plot_timestep_combine_filter_plot_scatter_001.html"
            methods.timestep_combine_filter_plot_scatter(datasets=datasets,
                                                         timestep_index=1,
                                                         plot_save_path=save_path)


