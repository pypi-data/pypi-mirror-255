import numpy as np
import colorspacious
import warnings


def gen_random_rgb(seed=None):
    np.random.seed(seed)
    return np.random.randint(0, 255, size=3)


def is_hex_color(color):
    if not isinstance(color, str):
        return False

    if color[0] != "#":
        return False, f"Hex color must start with '#', got {color}"

    if len(color) != 7:
        return False
    try:
        int(color[1:], 16)
    except ValueError:
        return False, f"Could not convert {color} to hex color"

    return True


def is_rgb_color(color):
    if not isinstance(color, tuple):
        return False, f"RGB color must be a tuple, got {color}"

    if len(color) != 3:
        return False, f"RGB color must have three elements, got {color}"

    for c in color:
        if not isinstance(c, int):
            return False, f"RGB color elements must be integers, got {color}"

        if c < 0 or c > 255:
            return False, f"RGB color elements must be between 0 and 255, got {color}"

    return True


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def cielab_to_rgb(cielab):
    # Clip to be in range [0, 255]
    rgb = colorspacious.cspace_convert(cielab, "CIELab", "sRGB255")
    rgb = np.clip(rgb, 0, 255)
    return rgb.astype(int)


def find_distant_colors(
    palette,
    num_colors,
    min_dist=3,
    max_iters=1000,
    seed=None,
    colorblind_safe=False,
    deuteranomaly_safe=None,
    protanomaly_safe=None,
    tritanomaly_safe=None,
):
    if min_dist < 0:
        raise ValueError("min_dist must be >= 0")

    if colorblind_safe:
        # Check if any colorblind variants are not None
        if deuteranomaly_safe is None:
            deuteranomaly_safe = True
        if protanomaly_safe is None:
            protanomaly_safe = True
        if tritanomaly_safe is None:
            tritanomaly_safe = True

        # If any colorblind variants are not True, set all to True and warn user
        if not all([deuteranomaly_safe, protanomaly_safe, tritanomaly_safe]):
            warnings.warn(
                "colorblind_safe is True but not all colorblind variants are True. "
                "Setting all colorblind variants (deuteranomaly_safe, "
                "protanomaly_safe, tritanomaly_safe) to True.  This may result in "
                "undesired behavior."
            )

    # Confirm num_colors and max_iters are positive integers
    if not isinstance(num_colors, int) or num_colors < 1:
        raise ValueError("num_colors must be a positive integer >= 1")

    if not isinstance(max_iters, int) or max_iters < 1:
        raise ValueError("max_iters must be a positive integer >= 1")

    if max_iters < num_colors:
        raise ValueError("max_iters must be >= num_colors")

    for _ in range(max_iters):
        if seed is not None:
            seed += 1
        rgb = gen_random_rgb(seed=seed)
        lab = colorspacious.cspace_convert(rgb, "sRGB255", "CAM02-UCS")[..., np.newaxis]
        compare_colors = lab[..., np.newaxis]

        if any([deuteranomaly_safe, protanomaly_safe, tritanomaly_safe]):
            rgb1 = colorspacious.cspace_convert(rgb, "sRGB255", "sRGB1")

            cvd_space = {
                "name": "sRGB1+CVD",
                "cvd_type": "deuteranomaly",
                "severity": 100,
            }

            # Deuteranomaly colorblindness
            if deuteranomaly_safe:
                cvd_space["cvd_type"] = "deuteranomaly"
                hopper_deuteranomaly_sRGB = colorspacious.cspace_convert(
                    rgb1, cvd_space, "sRGB1"
                )
                hopper_deuteranomaly_color = colorspacious.cspace_convert(
                    hopper_deuteranomaly_sRGB, "sRGB1", "CAM02-UCS"
                )[..., np.newaxis, np.newaxis]

                compare_colors = np.concatenate(
                    (compare_colors, hopper_deuteranomaly_color), axis=2
                )

            # Protanomaly colorblindness
            if protanomaly_safe:
                cvd_space["cvd_type"] = "protanomaly"
                hopper_protanomaly_sRGB = colorspacious.cspace_convert(
                    rgb1, cvd_space, "sRGB1"
                )
                hopper_protanomaly_color = colorspacious.cspace_convert(
                    hopper_protanomaly_sRGB, "sRGB1", "CAM02-UCS"
                )[..., np.newaxis, np.newaxis]
                compare_colors = np.concatenate(
                    (compare_colors, hopper_protanomaly_color), axis=2
                )

            # Tritanomaly colorblindness
            if tritanomaly_safe:
                cvd_space["cvd_type"] = "tritanomaly"
                hopper_tritanomaly_sRGB = colorspacious.cspace_convert(
                    rgb1, cvd_space, "sRGB1"
                )
                hopper_tritanomaly_color = colorspacious.cspace_convert(
                    hopper_tritanomaly_sRGB, "sRGB1", "CAM02-UCS"
                )[..., np.newaxis, np.newaxis]
                compare_colors = np.concatenate(
                    (compare_colors, hopper_tritanomaly_color), axis=2
                )

        # Compute distances between colors
        dists = np.linalg.norm(
            np.concatenate(palette, axis=1)[..., np.newaxis] - compare_colors, axis=0
        )

        # Add color if it is sufficiently far from the others
        if np.min(dists) > min_dist:
            palette.append(lab)

        # Stop if we have enough colors
        if len(palette) == num_colors:
            return palette

    raise ValueError(
        "Could not generate palette with given parameters. "
        "Please try again with a different seed, more iterations, "
        "decrease the minimum distance between colors, or use fewer colors."
    )
