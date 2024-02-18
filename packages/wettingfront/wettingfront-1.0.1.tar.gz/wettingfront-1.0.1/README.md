# WettingFront

[![License](https://img.shields.io/github/license/JSS95/wettingfront)](https://github.com/JSS95/wettingfront/blob/master/LICENSE)
[![CI](https://github.com/JSS95/wettingfront/actions/workflows/ci.yml/badge.svg)](https://github.com/JSS95/wettingfront/actions/workflows/ci.yml)
[![CD](https://github.com/JSS95/wettingfront/actions/workflows/cd.yml/badge.svg)](https://github.com/JSS95/wettingfront/actions/workflows/cd.yml)
[![Docs](https://readthedocs.org/projects/wettingfront/badge/?version=latest)](https://wettingfront.readthedocs.io/en/latest/?badge=latest)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/wettingfront.svg)](https://pypi.python.org/pypi/wettingfront/)
[![PyPI Version](https://img.shields.io/pypi/v/wettingfront.svg)](https://pypi.python.org/pypi/wettingfront/)

![title](https://wettingfront.readthedocs.io/en/latest/_images/index-1.png)

WettingFront is a simple and extensible Python package for wetting front analysis.

## Usage

Store analysis parameters in configuration file (YAML or JSON).

```
data1:
    type: Unidirectional
    path: your-video.mp4
    output-vid: result.mp4
    output-data: result.csv
data2:
    type: MyType
    my-parameters: ...
data3:
    ...
```

Pass the file to the command:

```
$ wettingfront analyze config.yml
```

You can also define your own analysis type by [writing a plugin](https://wettingfront.readthedocs.io/en/latest/plugin.html).

## Installation

WettingFront can be installed using `pip`.

```
$ pip install wettingfront
```

To access image processing feature, install with optional dependency `[img]`.

```
$ pip install wettingfront[img]
```

Other optional dependencies are listed in [manual](https://wettingfront.readthedocs.io/en/latest/intro.html#installation).

## Documentation

Wettingfront is documented with [Sphinx](https://pypi.org/project/Sphinx/).
The manual can be found on Read the Docs:

> https://wettingfront.readthedocs.io

If you want to build the document yourself, get the source code and install with `[doc]` dependency.
Then, go to `doc` directory and build the document:

```
$ pip install .[doc]
$ cd doc
$ make html
```

Document will be generated in `build/html` directory. Open `index.html` to see the central page.
