import os
from typing import Iterator

import matplotlib.pyplot as plt


def safe_save_fig(
    output_path, show_figure: bool = True, output_format: "str | Iterator[str]" = "png"
):
    """Helper method to safe figures in a potentially non-existent directory."""
    dir_name = os.path.dirname(output_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Strips ext from path.
    base_output_path = ".".join(output_path.split(".")[:-1])

    if isinstance(output_format, str):
        output_format = [output_format]
    for element in output_format:
        real_output_path = f"{base_output_path}.{element}"
        plt.savefig(real_output_path, dpi=400, format=element)

    if not show_figure:
        plt.close()
