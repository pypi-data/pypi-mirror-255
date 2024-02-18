# Color-Craftsman

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
![Development Status](https://img.shields.io/badge/development-active-brightgreen.svg)
![PyPI Downloads](https://img.shields.io/pypi/dm/color-craftsman.svg)

## Description

Color-Craftsman creates perceptually-distinct color palettes for data visualization in Python. While many great plotting libaries exist, they often rely on fixed color palettes and generally have few colors. These colors often conflict with one another. Color-Craftsman allows users to create a palette of colors that are perceptually distinct from one another. This allows for more colors to be used in a plot without sacrificing readability.

## Installation

```bash
pip install color-craftsman
```

## Usage

Simple examples are shown below. For more examples, see the [examples](./examples) directory.

### Creating a Random Palette

```python
import color_craftsman as cc

# Create a palette with 5 colors
palette = cc.generate_palette(
    5,
    min_dist=30,
    seed=11,
    output_format="rgb",
)
cc.visualize_palette(palette, show=True)
```

![base_palette](./images/base_palette.png)

`Note:` a random seed can be provided to ensure reproducibility. Distance is the distance between colors in the palette. A larger distance will result in more distinct colors. If the distance is too large, a warning message will be displayed. Too large of distances can result in colors that are too similar to each other due to clipping in the RGB color space. Distance is defined as the Delta-E color difference between colors in the palette.

### Creating a Palette from a Base Palette

```python
import color_craftsman as cc

# Create a palette with 10 total colors
extended_palette = cc.extend_palette(
    [
        np.array([153, 191, 80]),
        np.array([107, 88, 11]),
        np.array([42, 19, 119]),
        np.array([93, 110, 244]),
        np.array([213, 114, 236]),
    ],
    10,
    min_dist=10,
    seed=18,
    palette_format="rgb",
    output_format="rgb",
)
cc.visualize_palette(extended_palette, show=True)
```

![extended_palette](./images/extended_palette.png)

### Visualizing a Palette

```python
import color_craftsman as cc

cc.visualize_palette(palette, show=True)
```

### Colorblind-Safe Palettes

To guard against deutranopia, protanopia, and tritanopia, use the `colorblind_safe` parameter.

```python
palette = cc.generate_palette(
    5,
    min_dist=30,
    seed=22,
    output_format="rgb",
    colorblind_safe=True,
)
cc.visualize_palette(extended_palette, show=True)
```

![colorblind_palette](./images/colorblind_safe_palette.png)

#### Specific Colorblindness-Safe Palettes

If you want to guard against specific-forms of colorblindness, you can specify the type of colorblindness using the following arguments: `deuteranomaly_safe`, `protanomaly_safe`, and `tritanomaly_safe`.

##### Deuteranopia-Safe Palette

```python
palette = cc.generate_palette(
    5,
    min_dist=30,
    seed=33,
    output_format="rgb",
    deuteranomaly_safe=True,
)
cc.visualize_palette(palette, show=True)
```

![deuteranomaly_palette](./images/deuteranopia_safe_palette.png)

##### Protanopia-Safe Palette

```python
palette = cc.generate_palette(
    5,
    min_dist=30,
    seed=44,
    output_format="rgb",
    protanomaly_safe=True,
)
cc.visualize_palette(palette, show=True)
```

![protanopia_palette](./images/protanopia_safe_palette.png)

##### Tritanopia-Safe Palette

```python
palette = cc.generate_palette(
    5,
    min_dist=30,
    seed=55,
    output_format="rgb",
    tritanomaly_safe=True,
)
cc.visualize_palette(palette, show=True)
```

![tritanopia_palette](./images/tritanopia_safe_palette.png)

## Contributing

Contributions are welcome! If you'd like to contribute to the project, please follow these guidelines:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Test your changes thoroughly.
5. Submit a pull request.
6. Add caharper as a reviewer.

Please ensure your code adheres to the project's coding style and conventions.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

If you have any questions, suggestions, or feedback, feel free to reach out:

- Email: [caharper@smu.edu](mailto:caharper@smu.edu)
- GitHub: [caharper](https://github.com/caharper)
