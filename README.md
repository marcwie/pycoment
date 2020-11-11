[![DOI](https://zenodo.org/badge/114005339.svg)](https://zenodo.org/badge/latestdoi/114005339)

This is a small package for computing the entropy and the complexity of a given (set of) network(s). It implements the metrics that are proposed in the paper [Mapping and discrimination of networks in the complexity-entropy plane](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.96.042304). You can also find an open-access pre-print [here](https://arxiv.org/abs/1704.07599).

# Structure of the package

The package contains a module ```tools``` that can be imported via ```from pycoment import tools```. It contains functions for parsing input files of different formats, e.g., ```graphml``` and generating adjancency matrices from random network models.

The class ```Network``` can be imported via ```from pycoment import tools``` and allows to compute the corresponding network's (average) complexity and entropy. It can be instantiated with any **symmetric adjacency matrix without self-loops** provided as a ```sparse.csr_matrix```. See the below example for details on further usage. 

If your adjacency matrix does not fulfill the aforementioned requirements you can use ```pycoment.tools.clean_adjacency``` to make it symmetric, remove self-loops and remove isolated nodes. 

# Installation

A simple ```python setup.py develop``` should do. 

# Minimal working example

Create a network adjacency matrix for a Watts-Strogatz network and compute its entropy and complexity

```python
from pycoment import tools, Network

adjacency = tools.watts_strogatz_network(number_of_nodes=1000, number_neighbors=10, rewiring_probability=0.1)
net = Network(adjacency=adjacency)

entropy = net.entropy()
complexity = net.complexity()

# The value of complexity depends on the random reference network. Therefore it is advised to draw multiple samples and compute an average
avg_complexity, std_complexity = net.average_complexity(n_samples=100)

print("Entropy:", entropy)
print("Complexity:", complexity)
print("Average Complexity:", avg_complexity, "+/-", std_complexity)
```

