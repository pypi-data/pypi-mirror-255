# IDPettis Intrinsic Dimensionality Estimation by Alberto Biscalchin

This repository contains a Python implementation of the IDPettis algorithm, which is designed to estimate the intrinsic dimensionality of a dataset. The intrinsic dimensionality represents the minimum number of variables required to approximate the structure of the dataset. This implementation is based on the algorithm outlined in [reference to the original paper or source if available].

## Features

- Implementation of the IDPettis algorithm to estimate intrinsic dimensionality.
- Example script to generate a helix dataset and estimate its intrinsic dimensionality.
- Visualization of the helix dataset.

## Requirements

- Python 3.6+
- NumPy
- SciPy
- Matplotlib (for dataset visualization)

## Installation


## Usage

To use the IDPettis algorithm to estimate the intrinsic dimensionality of a dataset, follow these steps:

1. Prepare your dataset as a NumPy array where each row represents a data point and each column represents a dimension.
2. Use the `pdist` function from `scipy.spatial.distance` to compute the pairwise distances between data points.
3. Call the `idpettis` function with the computed distances and the number of data points.

Example:

```python
from your_module import generate_helix_data, idpettis
from scipy.spatial.distance import pdist, squareform
import numpy as np

# Generate a helix dataset
data = generate_helix_data(num_points=1000)

# Compute the pairwise distances
ydist = squareform(pdist(data))

# Sort distances for each point to get nearest neighbors, excluding the distance to itself
ydist_sorted = np.sort(ydist, axis=1)[:, 1:]

# Estimate the intrinsic dimensionality
idhat = idpettis(ydist_sorted, n=data.shape[0], K=10)

print(f'Estimated intrinsic dimensionality: {idhat}')
```

## Contributing

Contributions to improve the IDPettis implementation or to add new features are welcome. Please submit a pull request or open an issue to discuss your ideas.
