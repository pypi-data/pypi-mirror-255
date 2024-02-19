import matplotlib.pyplot as plt
import config


class GaiaCMDAxis(plt.Axes):
    background_image = plt.imread(config.DATA_DIR / "gaia_cmd_background.png")
    left, right = -1.5, 5.4
    bottom, top = 19.0, -5.0
    extent = (left, right, bottom, top)
    aspec_ratio = (right - left) / abs(top - bottom)

    def __init__(self, fig, rect=None, **kwargs):
        # Set default rect
        if rect is None:
            rect = [0.125, 0.110, 0.775, 0.770]

        # Set matplotlib style
        plt.style.use("./gaia_cmd_plotter/gaia_cmd.mplstyle")

        # Call the parent class constructor
        super().__init__(fig, rect, **kwargs)

        # Set background image
        self.imshow(self.background_image, extent=self.extent, aspect=self.aspec_ratio)

        # Set axis labels
        self.set_xlabel(r"$\mathrm{G_{BP} - G_{RP}}$")
        self.set_ylabel(r"$\mathrm{M_G}$")


def main() -> None:
    fig = plt.figure(figsize=(8, 8))
    ax = GaiaCMDAxis(fig)
    fig.add_axes(ax)
    ax.plot(2.3, 5.5, mfc="r", mec="k", marker="o", ms=7)
    plt.savefig(config.TEST_DIR / "test_cmd.pdf")


if __name__ == "__main__":
    main()
