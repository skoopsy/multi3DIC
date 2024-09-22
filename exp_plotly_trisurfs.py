import plotly.figure_factory as ff

import numpy as np
from scipy.spatial import Delaunay

u = np.linspace(0, 2*np.pi, 20)
v = np.linspace(0, 2*np.pi, 20)
u,v = np.meshgrid(u,v)
u = u.flatten()
v = v.flatten()

x = (3 + (np.cos(v)))*np.cos(u)
y = (3 + (np.cos(v)))*np.sin(u)
z = np.sin(v)

points2D = np.vstack([u,v]).T
tri = Delaunay(points2D)
simplices = tri.simplices

fig = ff.create_trisurf(x=x, y=y, z=z,
                         simplices=simplices,
                         title="Torus", aspectratio=dict(x=2, y=2, z=0.6))
fig.update_layout(
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

fig.show()
fig.write_html('plots/torus.html', full_html=False, include_plotlyjs='cdn')

import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_trisurf(x, y, z, triangles=simplices, edgecolors='k')
ax.set_box_aspect([1,1,0.25])
plt.show()


