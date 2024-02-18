import numpy as np
from color_craftsman.color_utils.color_space import (
    hex_to_rgb,
    rgb_to_hex,
    find_distant_colors,
    gen_random_rgb,
)
import colorspacious


def generate_palette(
    num_colors,
    min_dist=3,
    max_iters=1000,
    seed=None,
    output_format="rbg",
    colorblind_safe=False,
    deuteranomaly_safe=None,
    protanomaly_safe=None,
    tritanomaly_safe=None,
):
    if output_format not in ["rgb", "hex"]:
        raise ValueError("output_format must be 'rgb' or 'hex'")

    np.random.seed(seed)
    base_color = colorspacious.cspace_convert(
        gen_random_rgb(seed=seed), "sRGB255", "CAM02-UCS"
    )[..., np.newaxis]
    palette = [base_color]

    palette = find_distant_colors(
        palette,
        num_colors,
        min_dist,
        max_iters,
        seed,
        colorblind_safe,
        deuteranomaly_safe,
        protanomaly_safe,
        tritanomaly_safe,
    )

    # Convert to RGB
    palette = [
        np.clip(
            colorspacious.cspace_convert(
                np.squeeze(color), "CAM02-UCS", "sRGB255"
            ).astype(int),
            0,
            255,
        )
        for color in palette
    ]

    if output_format == "hex":
        palette = [rgb_to_hex(color) for color in palette]

    return palette


def extend_palette(
    palette,
    num_colors,
    min_dist=3,
    max_iters=1000,
    seed=None,
    palette_format="rgb",
    output_format="rgb",
    colorblind_safe=False,
    deuteranomaly_safe=None,
    protanomaly_safe=None,
    tritanomaly_safe=None,
):
    if output_format not in ["rgb", "hex"]:
        raise ValueError("output_format must be 'rgb' or 'hex'")

    if palette_format != "CAM02-UCS":
        if palette_format == "hex":
            palette = [hex_to_rgb(color) for color in palette]
            palette_format = "rgb"

        if palette_format == "rgb":
            palette_format = "sRGB255"

        palette = [
            colorspacious.cspace_convert(
                np.squeeze(color), palette_format, "CAM02-UCS"
            )[..., np.newaxis]
            for color in palette
        ]

    palette = find_distant_colors(
        palette,
        num_colors,
        min_dist,
        max_iters,
        seed,
        colorblind_safe,
        deuteranomaly_safe,
        protanomaly_safe,
        tritanomaly_safe,
    )

    # Convert to RGB
    palette = [
        np.clip(
            colorspacious.cspace_convert(
                np.squeeze(color), "CAM02-UCS", "sRGB255"
            ).astype(int),
            0,
            255,
        )
        for color in palette
    ]

    if output_format == "hex":
        palette = [rgb_to_hex(color) for color in palette]

    return palette
