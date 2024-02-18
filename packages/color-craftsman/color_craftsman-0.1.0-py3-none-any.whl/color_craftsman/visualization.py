import matplotlib.pyplot as plt
from color_craftsman.color_utils.color_space import rgb_to_hex


def visualize_palette(colors, color_format="rgb", show=True):
    if not color_format == "hex":
        if color_format == "rgb":
            # Convert to hex
            colors = [rgb_to_hex(color) for color in colors]
        else:
            raise ValueError(f"Unknown color format {color_format}")

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plotting the swatches and adding color codes
    for i, color in enumerate(colors):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
        ax.text(i + 0.5, -1.0, colors[i], ha="center", fontsize=10, rotation=90)

    # Setting the x-axis and y-axis limits
    ax.set_xlim(0, len(colors))
    ax.set_ylim(0, 1)

    # Removing the x-axis and y-axis
    ax.axis("off")

    # Set the aspect of the axis to be equal
    ax.set_aspect("equal")

    # Set the figure size to be the exact size of the swatches
    fig.set_size_inches(len(colors), 2)

    # Display the plot
    if show:
        plt.show()
    else:
        return fig, ax
