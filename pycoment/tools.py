import numpy as np
import igraph
from scipy import sparse
from glob import glob
from scipy.io import loadmat
import networkx as nx




#def adjacency_from_igraph(igraph_network):
#    number_of_nodes = igraph_network.vcount()
#    edges = igraph_network.get_edgelist()
#    adjacency = adjacency_from_edges(edges, number_of_nodes)
#    return adjacency


def adjacency_from_edges(edges, number_of_nodes=None):
    edges = np.array(edges).T
    if number_of_nodes is None:
        number_of_nodes = edges.max() + 1
    adjacency = sparse.csr_matrix((np.ones(edges.shape[1]), edges), 
                                  shape=(number_of_nodes, number_of_nodes))
    return adjacency


def load(input_file, verbose=True):

    ending = input_file.split(".")[-1]
    if ending == "txt":
        adjacency = load_txt(input_file)
    elif ending == "gr":
        adjacency = load_gr(input_file)
    elif ending == "mat":
        adjacency = load_mat(input_file)
    elif ending == "gml" or ending == "graphml":
        adjacency = load_gml(input_file)
    elif ending == "tsv":
        adjacency = load_tsv(input_file)

    if (adjacency.diagonal().sum()) > 0:
        adjacency = adjacency.tolil()
        for _ in range(adjacency.shape[0]):
            adjacency[_, _] = 0
        adjacency = adjacency.tocsr()

    if (adjacency != adjacency.T).sum() > 0:
        if verbose:
            print("Making adjacency symmetric")
        adjacency = adjacency + adjacency.T
        adjacency[adjacency > 0] = 1
    
    if (adjacency.sum(axis=0) == 0).any():
        if verbose:
            print("Removing isolated nodes")
        nz_row, nz_col = adjacency.nonzero()
        nz_row = np.unique(nz_row)
        nz_col = np.unique(nz_col)
        adjacency = adjacency[nz_row, :][:, nz_col]

    adjacency = sparse.csr_matrix(adjacency)
    return adjacency


def load_tsv(file_name):
    edges = []
    with open(file_name) as input_file:
        for row in input_file:
            if row[0] != "%":
                if "\t" in row:
                    separator = "\t"
                else:
                    separator = " "
                row = row[:-1].split(separator)
                node_i = row[0]
                node_j = row[1]
                edges.append([int(node_i), int(node_j)])

    adjacency = adjacency_from_edges(edges)

    return adjacency


def load_txt(file_name):
    edges = []
    with open(file_name) as input_file:
        for row in input_file:
            node_i, node_j, _ = row.split(" ")
            edges.append([int(node_i), int(node_j)])

    adjacency = adjacency_from_edges(edges)

    return adjacency


def load_gr(file_name):
    edges = []
    with open(file_name) as input_file:
        for row in input_file:
            if row[0] == "a":
                prefix, node_i, node_j, _ = row.split(" ")
                if prefix == "a":
                    edges.append([int(node_i), int(node_j)])

    adjacency = adjacency_from_edges(edges)

    return adjacency


def load_mat(file_name):
    input_data = loadmat(file_name)
    for (key, value) in input_data.items():
        if key[:2] != "__" and value.ndim == 2:
            if value.shape[0] == value.shape[1]:
                print("Found possible adjacency matrix with key "+key)
                edges = np.array(np.nonzero(value)).T
                number_of_nodes = value.shape[0]

    adjacency = adjacency_from_edges(edges, number_of_nodes)

    return adjacency


def load_gml(input_file):
    net = igraph.load(input_file)
    edges = net.get_edgelist()
    adjacency = adjacency_from_edges(edges)

    return adjacency


#def load_networks(inputfolder, networks=[]):
#    for _, folder in enumerate(inputfolder):
#        network_folder = load_folder("networks/"+folder)
#        for __, (name, adjacency) in enumerate(network_folder.items()):
#            if (adjacency != adjacency.T).sum() > 0:
#                print name, "Making adjacency symmetric"
#                adjacency = adjacency + adjacency.T
#                adjacency[adjacency > 0] = 1
#            if (adjacency.sum(axis=0) == 0).any():
#                print name, "Removing empty rows"
#                nz_row, nz_col = adjacency.nonzero()
#                nz_row = np.unique(nz_row)
#                nz_col = np.unique(nz_col)
#                adjacency = adjacency[nz_row, :][:, nz_col]
#
#            networks.append((name, folder, adjacency))
#
#    return networks
