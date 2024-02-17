# rdadccvt

Balzer's algorithm (DCCVT) to find a maximally population compact map

## Installation

To clone the repository:

```bash
$ git clone https://github.com/alecramsay/rdadccvt
$ cd rdadccvt
```

To install the package:

```bash
$ pip install rdadccvt
```

Then copy the `dccvt` executable from the `bin` directory to the `bin` directory where you installed the package.

## Usage

See the [rdatools/rdaroot](https://github.com/rdatools/rdaroot) and
[rdatools/rdaensemble](https://github.com/rdatools/rdaensemble)
repositories for examples of how to use this package.
The former takes contiguous and 'roughly equal' population maps, and
minimizes the energy (maximizes the population compactness).
The latter uses Balzer's algorithm as part of a multi-step process to
create a contiguous and 'roughly equal' population map from a random
set of starting district centroids.