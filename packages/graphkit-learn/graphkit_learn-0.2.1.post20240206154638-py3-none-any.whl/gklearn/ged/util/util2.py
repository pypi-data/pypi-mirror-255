"""
util2

GED computation utilities for the methods that can learn different edit costs
for each pair of (symbolic) labels.

@Author: linlin
@Date: 11.05.23
"""
import networkx as nx
import numpy as np

from gklearn.ged.util.util import ged_options_to_string


def pairwise_ged2(
		g1, g2, options={}, sort=True, repeats=1, parallel=False, verbose=True
):
	"""Compute the graph edit distance between two graphs using the gedlib library
	with repeats. This method is used for the methods that can learn different
	edit costs for each pair of (symbolic) labels.

	Notes
	-----
		- For methods such as BIPARTITE, the repeats may result same results.
		- # of edit operations are not computed in this method.
	"""
	from gklearn.gedlib import librariesImport, gedlibpy2

	ged_env = gedlibpy2.GEDEnv()
	ged_env.set_edit_cost(
		options['edit_cost'],
		edit_cost_constant=options['edit_cost_constants']
	)
	ged_env.add_nx_graph(g1, '')
	ged_env.add_nx_graph(g2, '')
	listID = ged_env.get_all_graph_ids()
	ged_env.init(
		init_option=(options[
			             'init_option'] if 'init_option' in options else 'EAGER_WITHOUT_SHUFFLED_COPIES')
	)
	ged_env.set_method(options['method'], ged_options_to_string(options))
	ged_env.init_method()

	g = listID[0]
	h = listID[1]
	dis_min = np.inf
	# 	print('------------------------------------------')
	for i in range(0, repeats):
		ged_env.run_method(g, h)
		upper = ged_env.get_upper_bound(g, h)
		dis = upper
		# 		print(dis)
		if dis < dis_min:
			dis_min = dis
			pi_forward = ged_env.get_forward_map(g, h)
			pi_backward = ged_env.get_backward_map(g, h)
	# 			lower = ged_env.get_lower_bound(g, h)

	# make the map label correct (label remove map as np.inf)
	nodes1 = [n for n in g1.nodes()]
	nodes2 = [n for n in g2.nodes()]
	nb1 = nx.number_of_nodes(g1)
	nb2 = nx.number_of_nodes(g2)
	pi_forward = [nodes2[pi] if pi < nb2 else np.inf for pi in pi_forward]
	pi_backward = [nodes1[pi] if pi < nb1 else np.inf for pi in pi_backward]
	#		print(pi_forward)

	return dis, pi_forward, pi_backward


# %%


def get_nb_edit_operations2(
		g1, g2, forward_map, backward_map, edit_cost=None, is_cml=False,
		**kwargs
):
	"""Calculate the numbers of the occurence of each edit operation in a given
	edit path.

	Parameters
	----------
	g1 : TYPE
		DESCRIPTION.
	g2 : TYPE
		DESCRIPTION.
	forward_map : TYPE
		DESCRIPTION.
	backward_map : TYPE
		DESCRIPTION.
	edit_cost : TYPE, optional
		DESCRIPTION. The default is None.
	is_cml : TYPE, optional
		DESCRIPTION. The default is False.
	**kwargs : TYPE
		DESCRIPTION.

	Raises
	------
	Exception
		DESCRIPTION.

	Returns
	-------
	TYPE
		DESCRIPTION.

	Notes
	-----
	Attention: when implementing a function to get the numbers of edit
	operations, make sure that:
		- It does not fail if NetworkX node labels are not consecutive integers;
		- It returns correct results if nodes are permutated (e.g., by using
		`gklearn.utis.utils.nx_permute_nodes()`.)
	Generally speaking, it means you need to distinguish the NetworkX label of
	a node from the position (index) of that node in the node list.
	"""
	if is_cml:
		if edit_cost == 'CONSTANT':
			node_labels = kwargs.get('node_labels', [])
			edge_labels = kwargs.get('edge_labels', [])
			return get_nb_edit_operations_symbolic_cml(
				g1, g2, forward_map, backward_map,
				node_labels=node_labels, edge_labels=edge_labels
			)
		else:
			raise Exception('Edit cost "', edit_cost, '" is not supported.')
	else:
		if edit_cost == 'LETTER' or edit_cost == 'LETTER2':
			return get_nb_edit_operations_letter(
				g1, g2, forward_map,
				backward_map
			)
		elif edit_cost == 'NON_SYMBOLIC':
			# Use node_labels and edge_labels if node_attrs and edge_attrs are
			# not specified. Otherwise, set them to [].
			node_attrs = kwargs.get('node_attrs', kwargs.get('node_labels', []))
			edge_attrs = kwargs.get('edge_attrs', kwargs.get('edge_labels', []))
			return get_nb_edit_operations_nonsymbolic(
				g1, g2, forward_map, backward_map,
				node_attrs=node_attrs, edge_attrs=edge_attrs
			)
		elif edit_cost == 'CONSTANT':
			# node_labels = kwargs.get('node_labels', [])
			# edge_labels = kwargs.get('edge_labels', [])
			edit_cost_constants = kwargs.get('edit_cost_constants')
			return_sorted_costs = kwargs.get('return_sorted_costs')
			return get_nb_edit_operations_symbolic2(
				g1, g2, forward_map, backward_map,
				node_labels='l', edge_labels='l',  # TODO: to generalize.
				edit_cost_constants=edit_cost_constants,
				return_sorted_costs=return_sorted_costs
			)
		else:
			raise Exception('Edit cost "', edit_cost, '" is not supported.')
			return get_nb_edit_operations_symbolic2(
				g1, g2, forward_map,
				backward_map
			)


def get_nb_edit_operations_symbolic2(
		g1, g2, forward_map, backward_map, node_labels='l', edge_labels='l',
		edit_cost_constants=None, return_sorted_costs=True
):
	"""Compute the number of each edit operations for symbolic-labeled graphs,
	where the edit costs are different costants for different labels.

	The node labels and edge labels of the whole dataset are first obtained from
	`edit_cost_constants` and then ordered in lexicographical order.
	Then, the numbers of edit operations is computed for each pair of labels.
	The returned numebers of edit operations is a list in the following order:
		- number of node insertion for each pair of labels;
		- number of node deletion for each pair of labels;
		- number of node substitution for each pair of labels;
		- number of edge insertion for each pair of labels;
		- number of edge deletion for each pair of labels;
		- number of edge substitution for each pair of labels.
	if the nodes or edges are not labeled, the corresponding numbers of 3 edit
	operations for unified edit costs are computed, namely, the costs of insertion,
	deletion, and substitution.

	Parameters
	----------
	g1 : networkx.Graph
		The first graph.
	g2 : networkx.Graph
		The second graph.
	forward_map : list
		The forward map.
	backward_map : list
		The backward map.
	node_labels : str, optional
		The node label attribute name. The default is 'l'.
	edge_labels : str, optional
		The edge label attribute name. The default is 'l'.
	edit_cost_constants : tuple(dict, dict), optional
		The edit cost constants. A tuple of two dictionaries, the first one for
		node labels and the second one for edge labels. The default is None.
	return_sorted_costs : bool, optional
		Whether to return the sorted edit costs. The default is True.

	Returns
	-------
	nb_edit_operations : list
		The numbers of edit operations for each pair of labels.
	sorted_label_pairs : tuple(list, list)
		The sorted label pairs for node labels and edge labels, respectively.
	sorted_edit_costs : list, optional
		The sorted edit costs, first for node labels and then for edge labels.
		if `return_sorted_costs` is True.

	Notes
	-----
	`node_labels` and `edge_labels` only support 'l' for now.

	Authors
	-------
	Linlin Jia, GitHub Copilot (2023.05.13)
	"""
	# Get the node labels and edge labels of the whole dataset.
	if edit_cost_constants is None:
		raise Exception('Edit cost constants are not specified.')
	ori_node_labels = _get_labels_from_edit_cost_const_dict(
		edit_cost_constants[0]
	)
	ori_edge_labels = _get_labels_from_edit_cost_const_dict(
		edit_cost_constants[1]
	)
	# Order the labels and get the label pairs, including the special label pairs
	# for insertion and deletion.
	nl_pairs = _get_ordered_label_pairs(ori_node_labels)
	el_pairs = _get_ordered_label_pairs(ori_edge_labels)

	# Iterate over the forward map and backward map to compute the numbers of edit
	# operations.
	# for nodes:
	if len(ori_node_labels) == 0:
		# if nodes are not labeled:
		n_node_ops = _get_n_node_ops_unified(
			forward_map, backward_map, g1, g2, node_labels
		)
	else:
		# if nodes are labeled:
		n_node_ops = _get_n_node_ops_symbolic(
			forward_map, backward_map, g1, g2, node_labels, nl_pairs,
			edit_cost_constants[0], len(ori_node_labels)
		)

	# for edges:
	if len(ori_edge_labels) == 0:
		# if edges are not labeled:
		n_edge_ops = _get_n_edge_ops_unified(
			forward_map, backward_map, g1, g2, edge_labels
		)
	else:
		# if edges are labeled:
		n_edge_ops = _get_n_edge_ops_symbolic(
			forward_map, backward_map, g1, g2, edge_labels, el_pairs,
			edit_cost_constants[1], len(ori_edge_labels)
		)

	if return_sorted_costs:
		sorted_costs_n = sort_edit_costs_by_keys(
			edit_cost_constants[0], nl_pairs, len(ori_node_labels)
		)
		sorted_costs_e = sort_edit_costs_by_keys(
			edit_cost_constants[1], el_pairs, len(ori_edge_labels)
		)
		return n_node_ops + n_edge_ops, (
		nl_pairs, el_pairs), sorted_costs_n + sorted_costs_e
	else:
		return n_node_ops + n_edge_ops, (nl_pairs, el_pairs)


def _get_n_node_ops_unified(
		forward_map, backward_map, g1, g2, node_labels
):
	"""
	Compute the numbers of node insertion, removal, and substitution for unified
	edit costs.

	Parameters
	----------
	forward_map : list
		The forward map.
	backward_map : list
		The backward map.
	g1 : networkx.Graph
		The first graph.
	g2 : networkx.Graph
		The second graph.
	node_labels : str
		The node label attribute name.

	Returns
	-------
	list of int
		The numbers of node insertion, removal, and substitution.

	Notes
	-----
	`node_labels` only supports 'l' for now.
	"""
	n_vi = 0
	n_vr = 0
	n_vs = 0

	nodes1 = [n for n in g1.nodes()]
	for i, map_i in enumerate(forward_map):
		if map_i == np.inf:
			n_vr += 1
		else:
			continue  # @TODO: fo now only support unlabeled edges.
			# The nodes are considered substituted as long as at least one feature
			# is different.
			label1 = g1.nodes[nodes1[i]]['l']
			label2 = g2.nodes[map_i]['l']
			if label1 != label2:
				n_vs += 1
	for map_i in backward_map:
		if map_i == np.inf:
			n_vi += 1
	n_ops = [n_vi, n_vr, n_vs]
	return n_ops


# n_vi = 0
# n_vr = 0
# n_vs = 0
#
# nodes1 = [n for n in g1.nodes()]
# for i, map_i in enumerate(forward_map):
# 	if map_i == np.inf:
# 		n_vr += 1
# 	else:
# 		# The nodes are considered substituted as long as at least one feature
# 		# is different.
# 		for nl in node_labels:
# 			label1 = g1.nodes[nodes1[i]][nl]
# 			label2 = g2.nodes[map_i][nl]
# 			if label1 != label2:
# 				n_vs += 1
# 				break
# for map_i in backward_map:
# 	if map_i == np.inf:
# 		n_vi += 1
# return n_vi, n_vr, n_vs, nodes1


def _get_n_node_ops_symbolic(
		forward_map, backward_map, g1, g2, node_labels, nl_pairs, edit_costs,
		n_ori_node_labels
):
	"""
	Compute the numbers of node insertion, removal, and substitution for symbolic
	edit costs.

	Parameters
	----------
	forward_map : list
		The forward map.
	backward_map : list
		The backward map.
	g1 : networkx.Graph
		The first graph.
	g2 : networkx.Graph
		The second graph.
	node_labels : str
		The node label attribute name.
	nl_pairs : list
		The ordered node label pairs.
	edit_costs : dict
		The edit costs. The keys are the node label pairs. The values are the edit
		costs.

	Returns
	-------
	list of int
		The numbers of node insertion, removal, and substitution.

	Notes
	-----
	`node_labels` only supports 'l' for now.

	Authors
	-------
	Linlin Jia, GitHub Copilot (2023.05.13)
	"""
	# Initialize the numbers of edit operations as 0.
	n_node_ops = [0] * len(nl_pairs)

	nodes1 = [n for n in g1.nodes()]
	# Iterate over the forward map:
	# @TODO: check if map_i the indices of the nodes in g2 or the real nx labels of the nodes.
	for i, map_i in enumerate(forward_map):
		if map_i == np.inf:
			# The node is removed:
			# Get the node label.
			label1 = g1.nodes[nodes1[i]]['l']
			# Find the index of the node label in the ordered node label pairs.
			idx = nl_pairs.index((label1, ''))
			# Increment the number of node removals.
			n_node_ops[idx] += 1
		else:
			# The node is substituted:
			# The nodes are considered substituted as long as at least one feature
			# is different.
			label1 = g1.nodes[nodes1[i]]['l']
			label2 = g2.nodes[map_i]['l']
			if label1 != label2:
				# Find the index of the node label pair in the ordered node label pairs.
				idx = nl_pairs.index((label1, label2))
				# Increment the number of node substitutions.
				n_node_ops[idx] += 1
	# Iterate over the backward map to find node insertions:
	nodes2 = [n for n in g2.nodes()]
	for i, map_i in enumerate(backward_map):
		if map_i == np.inf:
			# The node is inserted:
			# Get the node label.
			label2 = g2.nodes[nodes2[i]]['l']
			# Find the index of the node label in the ordered node label pairs.
			idx = nl_pairs.index(('', label2))
			# Increment the number of node insertions.
			n_node_ops[idx] += 1

	return n_node_ops


def _get_n_edge_ops_unified(
		forward_map, backward_map, g1, g2, edge_labels
):
	"""
	Compute the numbers of edge insertion, removal, and substitution for unified
	edit costs.

	Parameters
	----------
	forward_map : list
		The forward map.
	backward_map : list
		The backward map.
	g1 : networkx.Graph
		The first graph.
	g2 : networkx.Graph
		The second graph.
	edge_labels : str
		The edge label attribute name.

	Returns
	-------
	list of int
		The numbers of edge insertion, removal, and substitution.

	Notes
	-----
	`edge_labels` only supports 'l' for now.

	Authors
	-------
	Linlin Jia, GitHub Copilot (2023.05.13)
	"""
	n_ei = 0
	n_er = 0
	n_es = 0

	nodes1 = [n for n in g1.nodes()]
	edges1 = [e for e in g1.edges()]
	nb_edges2_cnted = 0
	for n1, n2 in edges1:
		idx1 = nodes1.index(n1)
		idx2 = nodes1.index(n2)
		# One of the nodes is removed, thus the edge is removed.
		if forward_map[idx1] == np.inf or forward_map[idx2] == np.inf:
			n_er += 1
		# Corresponding edge is in g2.
		# Notice if the graph is undirected, the two directions of the edge can
		# both be found in the nx.edges() list, so the next elif will not be
		# executed; meanwhile, nx.number_of_edges() will count the two directions
		# only once. nb_edges2_cnted is thus correct.
		elif (forward_map[idx1], forward_map[idx2]) in g2.edges():
			nb_edges2_cnted += 1
			continue  # @TODO: fo now only support unlabeled edges.
			# Edge labels are different as long as any one feature is different.
			el = 'l'
			label1 = g2.edges[((forward_map[idx1], forward_map[idx2]))][el]
			label2 = g1.edges[(n1, n2)][el]
			if label1 != label2:
				n_es += 1
		elif (forward_map[idx2], forward_map[idx1]) in g2.edges():
			nb_edges2_cnted += 1
			continue  # @TODO: fo now only support unlabeled edges.
			# Edge labels are different.
			el = 'l'
			label1 = g2.edges[((forward_map[idx2], forward_map[idx1]))][el]
			label2 = g1.edges[(n1, n2)][el]
			if label1 != label2:
				n_es += 1
		# corresponding nodes are in g2, however the edge is removed.
		else:
			n_er += 1
	n_ei = nx.number_of_edges(g2) - nb_edges2_cnted

	n_ops = [n_ei, n_er, n_es]

	return n_ops


# n_ei = 0
# n_er = 0
# n_es = 0
#
# edges1 = [e for e in g1.edges()]
# nb_edges2_cnted = 0
# for n1, n2 in edges1:
# 	idx1 = nodes1.index(n1)
# 	idx2 = nodes1.index(n2)
# 	# One of the nodes is removed, thus the edge is removed.
# 	if forward_map[idx1] == np.inf or forward_map[idx2] == np.inf:
# 		n_er += 1
# 	# Corresponding edge is in g2.
# 	elif (forward_map[idx1], forward_map[idx2]) in g2.edges():
# 		nb_edges2_cnted += 1
# 		# Edge labels are different as long as any one feature is different.
# 		for el in edge_labels:
# 			label1 = g2.edges[((forward_map[idx1], forward_map[idx2]))][el]
# 			label2 = g1.edges[(n1, n2)][el]
# 			if label1 != label2:
# 				n_es += 1
# 				break
# 	elif (forward_map[idx2], forward_map[idx1]) in g2.edges():
# 		nb_edges2_cnted += 1
# 		# Edge labels are different.
# 		for el in edge_labels:
# 			label1 = g2.edges[((forward_map[idx2], forward_map[idx1]))][el]
# 			label2 = g1.edges[(n1, n2)][el]
# 			if label1 != label2:
# 				n_es += 1
# 				break
# 	# corresponding nodes are in g2, however the edge is removed.
# 	else:
# 		n_er += 1
# n_ei = nx.number_of_edges(g2) - nb_edges2_cnted
#
# return n_vi, n_vr, n_vs, n_ei, n_er, n_es


def _get_n_edge_ops_symbolic(
		forward_map,
		backward_map,
		g1,
		g2,
		edge_labels,
		el_pairs,
		edit_costs,
		n_ori_edges_labels
):
	"""
	Compute the numbers of edge insertion, removal, and substitution for symbolic
	edit costs.

	Parameters
	----------
	forward_map : list
		The forward map.
	backward_map : list
		The backward map.
	g1 : networkx.Graph
		The first graph.
	g2 : networkx.Graph
		The second graph.
	edge_labels : str
		The edge label attribute name.
	el_pairs : list
		The ordered edge label pairs.
	edit_costs : dict
		The edit costs. The keys are the edge label pairs. The values are the edit
		costs.

	Returns
	-------
	list of int
		The numbers of edge insertion, removal, and substitution.

	Notes
	-----
		- `edge_labels` only supports 'l' for now.
		- This function only supports undirected graphs for now.

	Authors
	-------
	Linlin Jia, GitHub Copilot (2023.05.13)
	"""
	# Notice if the graph is undirected, list of nx.edges() only returns one
	# direction of the edges, but the two directions of the edge can
	# both be found in the nx.edges() list; meanwhile, nx.number_of_edges() will
	# count the two directions only once. # @TODO

	# Initialize the numbers of edit operations as 0.
	n_edit_ops = [0] * len(el_pairs)

	nodes1 = [n for n in g1.nodes()]
	edges1 = [e for e in g1.edges()]
	edges2_cnted = []  # Edges in g2 that have been counted.
	# Iterate over the edges in g1.
	for n1, n2 in edges1:
		idx1 = nodes1.index(n1)
		idx2 = nodes1.index(n2)
		# One of the nodes is removed, thus the edge is removed.
		if forward_map[idx1] == np.inf or forward_map[idx2] == np.inf:
			# Get the edge label.
			label1 = g1.edges[(n1, n2)]['l']
			# Get the index of the edge label pair.
			idx = el_pairs.index((label1, ''))
			# Increment the number of edge removals.
			n_edit_ops[idx] += 1
		# Corresponding edge is in g2.
		elif (forward_map[idx1], forward_map[idx2]) in g2.edges():
			# Add the edge to the counted list.
			edges2_cnted.append((forward_map[idx1], forward_map[idx2]))
			# Edge labels are different as long as any one feature is different.
			el = 'l'  #  @TODO
			label2 = g2.edges[((forward_map[idx1], forward_map[idx2]))][el]
			label1 = g1.edges[(n1, n2)][
				el]  # todo: check if the order of label1 and label2 is correct.
			if label1 != label2:
				# Get the index of the edge label pair.
				idx = el_pairs.index((label1, label2))
				# Increment the number of edge substitutions.
				n_edit_ops[idx] += 1
		# This `elif` will never be reached if the edges are undirected.
		elif (forward_map[idx2], forward_map[idx1]) in g2.edges():
			# Add the edge to the counted list.
			edges2_cnted.append((forward_map[idx2], forward_map[idx1]))
			# Edge labels are different.
			el = 'l'
			label2 = g2.edges[((forward_map[idx2], forward_map[idx1]))][el]
			label1 = g1.edges[(n1, n2)][el]
			if label1 != label2:
				# Get the index of the edge label pair.
				idx = el_pairs.index((label1, label2))
				# Increment the number of edge substitutions.
				n_edit_ops[idx] += 1
		# corresponding nodes are in g2, however the edge is removed.
		else:
			# Get the edge label.
			label1 = g1.edges[(n1, n2)]['l']
			# Get the index of the edge label pair.
			idx = el_pairs.index((label1, ''))
			# Increment the number of edge removals.
			n_edit_ops[idx] += 1

	# Iterate over the edges in g2 to find the inserted edges:
	edges2 = [e for e in g2.edges()]
	for n1, n2 in edges2:
		# idx1 = nodes1.index(n1)
		# idx2 = nodes1.index(n2)
		# Check if the edge is already counted:
		if nx.is_directed(g2):
			if (n1, n2) in edges2_cnted:
				continue
		else:
			if (n1, n2) in edges2_cnted or (n2, n1) in edges2_cnted:
				continue

		# Get the edge label.
		label2 = g2.edges[(n1, n2)]['l']
		# Get the index of the edge label pair.
		idx = el_pairs.index(('', label2))
		# Increment the number of edge insertions.
		n_edit_ops[idx] += 1

	return n_edit_ops


# %%


def _retrieve_ordered_label_pairs_from_cost_dict(cost_dict):
	"""Get the ordered label pairs from the keys of edit cost constants.

	Parameters
	----------
	cost_dict : dict
		The edit cost constants, where the keys are the tuples of labels.

	Returns
	-------
	list
		The ordered label pairs.

	Notes
	-----
	The special label '' is included for insertion and deletion; the special label
	' ' is included for unlabeled nodes or edges.

	Authors
	-------
	Linlin Jia, GitHub Copilot (2023.05.13)
	"""
	# Get the node labels and edge labels of the whole dataset.
	ori_labels = _get_labels_from_edit_cost_const_dict(cost_dict)

	# if the nodes or edges are not labeled, the special label for 3 edit operations
	# is returned:
	if len(ori_labels) == 0:
		return [('', ' '), (' ', ''), (' ', ' ')]

	# if the nodes or edges are labeled, the label pairs are returned:
	label_paris = get_label_pairs(ori_labels, sort=True, extended=True)
	return label_paris


def _get_ordered_label_pairs(ori_labels):
	"""Get the ordered label pairs from the original labels.

	Parameters
	----------
	ori_labels : list
		The original labels.

	Returns
	-------
	list
		The ordered label pairs.

	Notes
	-----
	The special label '' is included for insertion and deletion; the special label
	' ' is included for unlabeled nodes or edges.

	Authors
	-------
	Linlin Jia, GitHub Copilot (2023.05.13)
	"""
	# if the nodes or edges are not labeled, the special label for 3 edit operations
	# is returned:
	if len(ori_labels) == 0:
		return [('', ' '), (' ', ''), (' ', ' ')]

	# if the nodes or edges are labeled, the label pairs are returned:
	label_paris = get_label_pairs(ori_labels, sort=True, extended=True)
	return label_paris


def _get_labels_from_edit_cost_const_dict(cost_dict):
	"""Get the node labels or edge labels from the keys of edit cost constants.

	Parameters
	----------
	cost_dict : dict
		The edit cost constants, where the keys are the tuples of labels.

	Returns
	-------
	list
		The node labels or edge labels.

	Authors
	-------
	Linlin Jia, GitHub Copilot (2023.05.13)
	"""
	labels = []
	for k in cost_dict.keys():
		for l in k:
			if l not in labels:
				labels.append(l)
	# Remove special labels: '', ' ':
	if '' in labels:
		labels.remove('')
	if ' ' in labels:
		labels.remove(' ')
	return labels


def sort_edit_costs_by_keys(costs_dict, ordered_label_pairs, n_ori_labels):
	"""
	Sort the edit costs by the keys.

	Parameters
	----------
	costs_dict : dict
		The edit costs, where the keys are the tuples of labels.
	ordered_label_pairs : list
		The ordered label pairs.
	n_ori_labels : int
		The number of original labels.

	Returns
	-------
	list
		The sorted edit costs.

	Authors
	-------
	Linlin Jia, GitHub Copilot (2023.05.14)
	"""
	if n_ori_labels == 0:
		# for unlabeled nodes or edges:
		return [costs_dict[('', ' ')], costs_dict[(' ', '')],
		        costs_dict[(' ', ' ')]]
	else:
		# for labeled nodes or edges:
		costs = []
		for l1, l2 in ordered_label_pairs:
			costs.append(costs_dict[(l1, l2)])
		return costs


def get_label_pairs(labels, sort=True, extended=False):
	"""
	Get all possible pairs of labels from a list of labels.

	Parameters
	----------
	labels : list of hashable
		List of labels.
	sort : bool, optional (default=True)
		Sort labels to ensure that the same pair of labels is always represented.
	extended : bool, optional (default=False)
		Include insertions and deletions pairs.

	Returns
	-------
	label_pairs : list of tuples
		List of all possible pairs of labels.
	"""
	# Sort labels to ensure that the same pair of labels is always represented
	# by the same tuple.
	if sort:
		labels = sorted(labels)

	label_pairs = []

	# Include insertions and deletions pairs.
	if extended:
		for i in range(len(labels)):
			if isinstance(i, str) and i == '':
				raise ValueError(
					'The empty string is not allowed as a label. As it is used '
					'to represent the special label (epsilon) for insertion and deletion.'
				)
			label_pairs.append(('', labels[i]))
		for i in range(len(labels)):
			label_pairs.append((labels[i], ''))

	# Get all possible pairs of labels, two directions.
	for i in range(len(labels)):
		for j in range(i + 1, len(labels)):
			label_pairs.append((labels[i], labels[j]))
			label_pairs.append((labels[j], labels[i]))

	return label_pairs