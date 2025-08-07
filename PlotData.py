"A module for the PlotData class"

from matplotlib.figure import Figure

class PlotData:

    """
    A class to handle detials of how we are plotting our data
    """

    def __init__(self, x, y_list, labels=None, xlabel="", ylabel="", title=""):
        self.x = x
        self.y_list = y_list  # List of y data arrays
        if labels is not None:
            self.labels = labels
        else:
            self.labels = [f"Series {i+1}" for i in range(len(y_list))]
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title

        print(f"PlotData initialized with {len(y_list)} series, x length: {len(x)}")
        print(f"Labels: {self.labels}")

    def plot(self, ax=None):
        "create the plot figure according to how this object was setup"
        fig = None
        if ax is None:
            # Create a new figure if no axes are provided
            fig = Figure(figsize=(4, 3))
            ax = fig.add_subplot(111)


        for y, label in zip(self.y_list, self.labels):
            # print(f"now x is", type(self.x))
            # print(f"Plotting series: {label} with {len(y)} points and {len(self.x)} x points")
            ax.plot(self.x, y, label=label)
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.legend()

        x = 0.75
        y = 0.75
        ax.text(x, y, "source", transform=ax.transAxes,
                        fontsize=12, color="black", ha="right", va="top")
        return fig, ax
