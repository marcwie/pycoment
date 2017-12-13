import numpy as np
from sklearn.preprocessing import normalize
#from igraph import Graph
from scipy import sparse

Q_0 = 1. / np.log(2)

class Network():

    def __init__(self, adjacency):

        assert not (adjacency != adjacency.T).nnz
        assert not adjacency.diagonal().sum() 
        assert isinstance(adjacency, sparse.csr_matrix)

        self._cache = {'complexity': [], 'entropy': None, 'linkdensity': None}
        self._adjacency = adjacency
        self._traverse_probabilities = normalize(adjacency, norm='l1', axis=1)
        self._N = adjacency.shape[0] 
        self._triu_indices = np.triu_indices(adjacency.shape[0], k=1)
        self._normalization = np.log(adjacency.shape[0] - 1)

    def entropy(self, normalized=True):

        number_of_nodes = self._N
        adjacency = self._adjacency
        traverse_probs = self._traverse_probabilities

        if self._cache['entropy'] is not None:
            if normalized:
                return self._cache['entropy'] / self._normalization
            else:
                return self._cache['entropy'] 

        entropy = self._shannon_entropy(traverse_probs)
        self._cache['entropy'] = entropy

        if normalized:
            entropy = entropy / self._normalization

        return entropy


    def _shannon_entropy(self, probalities):
        
        number_of_nodes = self._N

        #nonzero_probs = probalities[probalities.nonzero()]
        nonzero_probs = probalities.data.flatten()

        entropy = np.array(np.log(nonzero_probs)) * np.array(nonzero_probs)
        entropy = - entropy.sum() / number_of_nodes 
    
        return entropy


    def reference_probabilities(self):

        linking_probability = self.link_density()
        number_of_nodes = self._N

        ind0, ind1 = self._triu_indices
        
        random_indices = np.random.random(len(ind0)) < linking_probability
        ind0 = ind0[random_indices]
        ind1 = ind1[random_indices]
        reference_edges = (np.concatenate((ind0, ind1)), np.concatenate((ind1,
                                                                        ind0))) 
        #reference_network = Graph.Erdos_Renyi(n=number_of_nodes,
        #                                      p=linking_probability,
        #                                      directed=False,
        #                                      loops=False)

        #reference_edges = np.array(reference_network.get_edgelist())
        #reference_edges = reference_edges.T

        reference_adjacency = sparse.csr_matrix(
            (np.ones(2 * len(ind0)), reference_edges), 
            shape=(number_of_nodes, number_of_nodes))
        #reference_adjacency = reference_adjacency + reference_adjacency.T

        #assert not (reference_adjacency > 1).nnz
        #assert not reference_adjacency.diagonal().sum() 

        reference_traverse_probs = normalize(reference_adjacency, 
                                             norm='l1', 
                                             axis=1)
        return reference_traverse_probs


    def complexity(self):   
        traverse_probs = self._traverse_probabilities

        network_entropy = self.entropy(normalized=False)
        normalized_network_entropy = self.entropy()

        reference_probs = self.reference_probabilities()
        reference_entropy = self._shannon_entropy(reference_probs)

        joint_probabilities = 0.5 * (traverse_probs + reference_probs)
        joint_entropy = self._shannon_entropy(joint_probabilities)

        complexity = normalized_network_entropy * Q_0 
        complexity *= joint_entropy - (network_entropy + reference_entropy) / 2 
        
        self._cache['complexity'].append(complexity)

        return complexity
      

    def previous_complexities(self):
        return self._cache['complexity']

    
    def average_complexity(self, with_std=True, n_samples=None):
        complexities = self._cache['complexity']

        if n_samples is None:
            n_samples = len(complexitie)

        while len(complexities) < n_samples:
            self.complexity()
       
        avg_complexity = np.mean(complexities[:n_samples])
        if with_std:
            return avg_complexity, np.std(complexities[:n_samples])
        else:
            return avg_complexity


    def link_density(self):
       
        if self._cache['linkdensity'] is not None:
            return self._cache['linkdensity']

        adjacency = self._adjacency
        N = self._N
        link_density = adjacency.sum() / (N * (N - 1))
        self._cache['link_density'] = link_density
        
        return link_density


    def number_of_nodes(self):
        return self._N
