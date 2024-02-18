"""Package to analyze wetting front data.

To analyze with command line, specify the parameters in configuration file(s) and run::

    wettingfront analyze <file1> [<file2> ...]
"""

import argparse
import csv
import json
import os
import sys
from typing import Tuple

import numpy as np
import yaml

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
    from importlib_resources import files
else:
    from importlib.metadata import entry_points
    from importlib.resources import files

__all__ = [
    "get_sample_path",
    "analyze_files",
    "fit_washburn",
]


def get_sample_path(*paths: str) -> str:
    """Get path to sample file.

    Arguments:
        paths: Subpaths under ``wettingfront/samples/`` directory.

    Returns:
        Absolute path to the sample file.

    Examples:
        >>> from wettingfront import get_sample_path
        >>> get_sample_path() # doctest: +SKIP
        'path/wettingfront/samples'
        >>> get_sample_path("myfile") # doctest: +SKIP
        'path/wettingfront/samples/myfile'
    """
    return str(files("wettingfront").joinpath("samples", *paths))


def analyze_files(*paths: str):
    """Perform analysis from configuration files.

    Supported formats:
        * YAML
        * JSON

    Each file can have multiple entries. Each entry must have ``type`` field which
    specifies the analyzer. Analyzers are searched from entry point group
    ``"wettingfront.analyzers"``, and must have the following signature:

    * :obj:`str`: entry name
    * :obj:`dict`: entry fields

    For example, the following YAML file contains ``foo`` entry which is analyzed by
    ``Foo`` analyzer. The analyzer is loaded by searching an entry point whose name is
    ``Foo``.

    .. code-block:: yaml

        foo:
            type: Foo
            ...

    Arguments:
        paths: Configuration file paths.
    """
    # load analyzers
    ANALYZERS = {}
    for ep in entry_points(group="wettingfront.analyzers"):
        ANALYZERS[ep.name] = ep.load()

    for path in paths:
        _, ext = os.path.splitext(path)
        ext = ext.lstrip(os.path.extsep).lower()
        try:
            with open(path, "r") as f:
                if ext == "yaml" or ext == "yml":
                    data = yaml.load(f, Loader=yaml.FullLoader)
                elif ext == "json":
                    data = json.load(f)
                else:
                    print(f"Skipping {path} ({ext} not supported)")
        except FileNotFoundError:
            print(f"Skipping {path} (path does not exist)")
            continue
        for k, v in data.items():
            try:
                typename = v["type"]
                analyzer = ANALYZERS.get(typename, None)
                if analyzer is None:
                    raise ValueError("Analysis type '%s' is not registered." % typename)
                analyzer(k, v)
            except Exception as err:
                print(f"Skipping {k} ({type(err).__name__}: {err})")
                continue


def fit_washburn(t, L) -> Tuple[np.float64, np.float64, np.float64]:
    r"""Fit data to Washburn's equation [#f1]_.

    The data are fitted to:

    .. math::

        L = k \sqrt{t - a} + b

    where :math:`k` is penetrativity of the liquid and :math:`a` and :math:`b` are
    correction terms for the starting point.

    Arguments:
        t (array_like, shape (M,)): Time.
        L (array_like, shape (M,)): Penetration length.

    Returns:
        k, a, b
            Washburn equation coefficients.

    .. [#f1] Washburn, E. W. (1921). The dynamics of capillary flow.
             Physical review, 17(3), 273.
    """
    # For polynomial fitting, fit L to t instead of the other way around.
    A, B, C = np.polyfit(L, t, 2)
    k = 1 / np.sqrt(A)
    b = -B / 2 / A
    a = C - B**2 / 4 / A
    return (k, a, b)


def unidirect_analyzer(k, v):
    """Image analysis for unidirectional liquid imbibition in porous medium.

    .. note::

        To evoke this analyzer, you need ``img`` optional dependency::

            pip install wettingfront[img]

    Unidirectional analyzer detects the horizontal wetting front in the image by
    pixel intensities and fits the data using :func:`fit_washburn`.

    The analyzer defines the following fields in configuration entry:

    - **path** (`str`): Path to the input video file.
    - **output-vid** (`str`, optional): Path to the output video file.
    - **output-data** (`str`, optional): Path to the output csv file.

    The output csv file contains three colums; time, wetting height, and fitted
    wetting height. The time unit is seconds and the distance unit is pixels.

    The following is the example for an entry in YAML configuration file:

    .. code-block:: yaml

        foo:
            type: Unidirectional
            path: foo.mp4
            output-vid: output/foo.mp4
            output-data: output/foo.csv
    """
    import imageio.v3 as iio

    # Prepare output
    path = os.path.expandvars(v["path"])
    out_vid = v.get("output-vid")
    out_data = v.get("output-data")
    if out_vid:
        out_vid = os.path.expandvars(v["output-vid"])
        dirname, _ = os.path.split(out_vid)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
    if out_data:
        out_data = os.path.expandvars(v["output-data"])
        dirname, _ = os.path.split(out_data)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

    def yield_result(path):
        for frame in iio.imiter(path, plugin="pyav"):
            gray = np.dot(frame, [0.2989, 0.5870, 0.1140])
            h = np.argmax(np.abs(np.diff(np.mean(gray, axis=1))))
            frame[h, :] = (255, 0, 0)
            yield frame, int(frame.shape[0] - h)

    # Get data (and write video)
    immeta = iio.immeta(path, plugin="pyav")
    fps = immeta["fps"]
    heights = []
    gen = yield_result(path)
    if out_vid:
        codec = immeta["codec"]
        with iio.imopen(out_vid, "w", plugin="pyav") as out:
            out.init_video_stream(codec, fps=fps)
            for frame, h in gen:
                out.write_frame(frame)
                heights.append(h)
    elif out_data:
        for frame, h in gen:
            out.write_frame(frame)
            heights.append(h)

    # write data
    if out_data:
        times = np.arange(len(heights)) / fps
        k, a, b = fit_washburn(times, heights)
        washburn = k * np.sqrt(times - a) + b

        with open(out_data, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time (s)", "height (pixels)", "fitted height (pixels)"])
            for t, h, w in zip(times, heights, washburn):
                writer.writerow([t, h, w])


def main():
    """Entry point function."""
    parser = argparse.ArgumentParser(
        prog="wettingfront",
        description="Wetting front analysis.",
    )
    subparsers = parser.add_subparsers(dest="command")

    parser_samples = subparsers.add_parser(
        "samples",
        description="Print path to sample directory.",
        help="print path to sample directory",
    )
    parser_samples.add_argument(
        "plugin",
        type=str,
        nargs="?",
        help="name of the plugin",
    )

    parser_analyze = subparsers.add_parser(
        "analyze",
        description="Parse configuration files and analyze.",
        help="parse configuration files and analyze",
        epilog=(
            "Supported file formats: YAML, JSON.\n"
            "Refer to the package documentation for configuration file structure."
        ),
    )
    parser_analyze.add_argument("file", type=str, nargs="+", help="configuration files")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help(sys.stderr)
        sys.exit(1)
    elif args.command == "samples":
        if args.plugin is None:
            print(get_sample_path())
        else:
            for ep in entry_points(group="wettingfront.samples"):
                if ep.name == args.plugin:
                    getter = ep.load()
                    print(getter())
                    break
    elif args.command == "analyze":
        analyze_files(*args.file)
