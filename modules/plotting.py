import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px


def plot_scatter_points(dataset, plot_save_path: str) -> None:
    fig = px.scatter_3d(x=dataset.x.flatten(),
                        y=dataset.y.flatten(),
                        z=dataset.z.flatten(),
                        )
    fig.show(renderer='browser')

    if plot_save_path:
        fig.write_html(plot_save_path, full_html=False, include_plotlyjs='cdn')

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
        cmin=0,
        cmax=2,
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


def multiple_meshes_single_timestep(datasets,
                                    timestep_index,
                                    plot_save_path=None,
                                    z_scale=1):

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
    fig = go.Figure(data=None, layout=layout)

    for dataset in datasets:
        fig.add_trace(go.Mesh3d(
            x=dataset[timestep_index].x_filtered,
            y=dataset[timestep_index].y_filtered,
            z=dataset[timestep_index].z_filtered,
            i=dataset[timestep_index].simplices_filtered[:, 0],
            j=dataset[timestep_index].simplices_filtered[:, 1],
            k=dataset[timestep_index].simplices_filtered[:, 2],
            intensity=dataset[timestep_index].strain_filtered,
            cmin=0,
            cmax=2,
            colorscale='Viridis',
            showscale=False
        ))

    fig.show()

    if plot_save_path != None:
        fig.write_html(plot_save_path, full_html=False, include_plotlyjs='cdn')

    return None

def create_animated_mesh(datasets, z_scale=1, plot_save_path=None):
    """
    Creates an animated 3D Mesh plot where each frame represents a timestep across all
    stereo pairs.
    Fixes the axis ranges and the color scale range.

    :param datasets: List of datasets, where each dataset corresponds to a stereo pair
                     and contains multiple timesteps.
    :param z_scale: Scaling factor for the z-axis.
    :return: None
    """
    # Initialize lists for frames and sliders
    frames = []
    sliders_dict = {
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'Timestep: ',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': []
    }

    # Determine global min/max ranges for x, y, z, and strain (for colorbar)
    x_min, x_max = float('inf'), float('-inf')
    y_min, y_max = float('inf'), float('-inf')
    z_min, z_max = float('inf'), float('-inf')
    strain_min, strain_max = float('inf'), float('-inf')

    # Calculate the overall ranges across all datasets and timesteps
    for stereo_pair in datasets:
        for timestep_data in stereo_pair:
            x_min = min(x_min, timestep_data.x_filtered.min())
            x_max = max(x_max, timestep_data.x_filtered.max())
            y_min = min(y_min, timestep_data.y_filtered.min())
            y_max = max(y_max, timestep_data.y_filtered.max())
            z_min = min(z_min, timestep_data.z_filtered.min())
            z_max = max(z_max, timestep_data.z_filtered.max())
            # strain_min = min(strain_min, timestep_data.strain_filtered.min())
            # strain_max = max(strain_max, timestep_data.strain_filtered.max())
            strain_min = -2
            strain_max = 30

    # Create frames for each timestep
    num_timesteps = len(datasets[0])

    for timestep_idx in range(num_timesteps):
        # Data for current timestep across all stereo pairs
        timestep_meshes = []

        for stereo_pair_idx, stereo_pair in enumerate(datasets):
            timestep_data = stereo_pair[timestep_idx]

            # Create a Mesh3d for each stereo pair at the current timestep
            mesh = go.Mesh3d(
                x=timestep_data.x_filtered,
                y=timestep_data.y_filtered,
                z=timestep_data.z_filtered,
                i=timestep_data.simplices_filtered[:, 0],
                j=timestep_data.simplices_filtered[:, 1],
                k=timestep_data.simplices_filtered[:, 2],
                intensity=timestep_data.strain_filtered,
                colorscale='Viridis',
                cmin=strain_min,  # Fix the colorbar range
                cmax=strain_max,  # Fix the colorbar range
                flatshading=True,
                opacity=1.0,  # Adjust for visibility of multiple stereo pairs
                name=f'Stereo Pair {stereo_pair_idx + 1}'
            )
            timestep_meshes.append(mesh)

        # Create the frame
        frame = go.Frame(data=timestep_meshes, name=f"frame_{timestep_idx}")
        frames.append(frame)

        # Add a slider step for each frame
        slider_step = {
            'args': [
                [f"frame_{timestep_idx}"],
                {
                    'frame': {'duration': 500, 'redraw': True},
                    'mode': 'immediate',
                    'transition': {'duration': 300}
                }
            ],
            'label': timestep_idx,
            'method': 'animate'
        }
        sliders_dict['steps'].append(slider_step)

    # Create the initial plot with the first timesteps data
    initial_data = frames[0].data

    # Create the layout with fixed axis ranges
    layout = go.Layout(
        scene=dict(
            aspectratio=dict(x=1, y=1, z=z_scale),
            xaxis=dict(title='X [mm]', range=[x_min, x_max]),  # Fix the x-axis range
            yaxis=dict(title='Y [mm]', range=[y_min, y_max]),  # Fix the y-axis range
            zaxis=dict(title='Z [mm]', range=[z_min, z_max]),  # Fix the z-axis range
        ),
        title="Animated 3D Mesh over Timesteps",
        sliders=[sliders_dict],
        updatemenus=[
            {
                'buttons': [
                    {
                        'args': [None, {'frame': {'duration': 500, 'redraw': True},
                                        'fromcurrent': True, 'mode': 'immediate'}],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {'frame': {'duration': 0, 'redraw': True},
                                          'mode': 'immediate'}],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }
        ]
    )

    # Create the figure
    fig = go.Figure(data=initial_data, layout=layout, frames=frames)

    # Show the plot
    fig.show()

    # Save plot
    if plot_save_path != None:
        fig.write_html(plot_save_path, full_html=False, include_plotlyjs='cdn')

    return None
