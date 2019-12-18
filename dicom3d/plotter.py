
""" mathplotlib """
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt

class plotter():
	""" TBD """
	def __init__(self, figsize=(8,8), rows=1, columns=1, projection=None):

		# initialize fixure and axis
		figure = plt.figure(figsize=figsize)
		ax = figure.gca(projection=projection) if projection else None

		# prepare plot context and sub definitions
		self.plot_context = (figure, ax)
		self.plot_sub = (rows,columns,1)		

	def subplots(self, rows, columns):
		self.plot_sub = (rows,columns,1)

	def subnew(self):
		fig, _ = self.plot_context
		row, column, idx = self.plot_sub
		ax = fig.add_subplot(row, column, idx)
		self.plot_sub = (row, column, idx+1)
		self.plot_context = (fig, ax)

	def image(self, image, cmap="gray", title=None):
		_, ax = self.plot_context
		ax.imshow(image, cmap=cmap)
		if title is not None: plt.title(title)

	def plot_dataset(self, dataset, marker_coords=None, marker_line=None):
		fig, ax = self.plot_context

		w, h = dataset.Columns, dataset.Rows

		left, top, _     = self.coords_to_mm(dataset, (0,0))
		right, bottom, _ = self.coords_to_mm(dataset, (w,h))
		extent = [left, right, bottom, top]

		ax.imshow(dataset.pixel_array, extent=extent, cmap="gray")

		# artefacts
		if marker_coords is not None:
			circle = plt.Circle(marker_coords, 10, color='r', fill=None)
			ax.add_artist(circle)

		if marker_line is not None:
			pt1, pt2 = marker_line
			x1, y1 = pt1
			x2, y2 = pt2
			ax.plot([x1,x2],[y1,y2])

	def show(self):
		plt.show()

	def numpy(self):
		fig, _ = self.plot_context
		return fig.canvas.renderer.buffer_rgba()



	