#!/usr/bin/env python3
#
#  export.py
"""
Export and load decision trees to/from JSON-safe dictionaries..

.. versionadded:: 0.6.0
"""
#
#  Copyright © 2023 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Based on https://github.com/mlrequest/sklearn-json
#  Copyright (c) 2019 Mathieu Rodrigue
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from typing import Any, Dict, Tuple

# 3rd party
import numpy
from sklearn.ensemble import RandomForestClassifier  # type: ignore[import]
from sklearn.tree import DecisionTreeClassifier  # type: ignore[import]
from sklearn.tree._tree import Tree  # type: ignore[import]

__all__ = [
		"deserialise_decision_tree",
		"deserialise_random_forest",
		"serialise_decision_tree",
		"serialise_random_forest"
		]


def _serialise_tree(tree: Tree) -> Tuple[Dict[str, Any], numpy.dtype]:
	serialised_tree = tree.__getstate__()

	dtypes = serialised_tree["nodes"].dtype
	serialised_tree["nodes"] = serialised_tree["nodes"].tolist()
	serialised_tree["values"] = serialised_tree["values"].tolist()

	return serialised_tree, dtypes


def _deserialise_tree(tree_dict: Dict[str, Any], n_features: int, n_classes: int, n_outputs: int) -> Tree:
	tree_dict["nodes"] = [tuple(lst) for lst in tree_dict["nodes"]]

	names = [
			"left_child",
			"right_child",
			"feature",
			"threshold",
			"impurity",
			"n_node_samples",
			"weighted_n_node_samples",
			"missing_go_to_left",
			]
	tree_dict["nodes"] = numpy.array(
			tree_dict["nodes"],
			dtype=numpy.dtype({"names": names, "formats": tree_dict["nodes_dtype"]}),
			)
	tree_dict["values"] = numpy.array(tree_dict["values"])

	tree = Tree(n_features, numpy.array([n_classes], dtype=numpy.intp), n_outputs)
	tree.__setstate__(tree_dict)

	return tree


def serialise_decision_tree(model: DecisionTreeClassifier) -> Dict[str, Any]:
	"""
	Serialise a decision tree to a JSON-safe dictionary.

	:param model: Trained decision tree.
	"""

	tree, dtypes = _serialise_tree(model.tree_)
	serialised_model = {
			"classes_": model.classes_.tolist(),
			"feature_importances_": model.feature_importances_.tolist(),
			"max_features_": model.max_features_,
			"n_classes_": int(model.n_classes_),
			"n_features_in_": model.n_features_in_,  # "feature_names_in_": model.feature_names_in_.tolist(),
			"n_outputs_": model.n_outputs_,
			"tree_": tree,
			"params": model.get_params()
			}

	tree_dtypes = []
	for i in range(0, len(dtypes)):  # type: ignore[arg-type]
		tree_dtypes.append(dtypes[i].str)

	serialised_model["tree_"]["nodes_dtype"] = tree_dtypes

	return serialised_model


def deserialise_decision_tree(model_dict: Dict[str, Any]) -> DecisionTreeClassifier:
	"""
	Deserialise a decision tree.

	:param model_dict: JSON-safe representation of the decision tree.
	"""

	deserialised_model = DecisionTreeClassifier(**model_dict["params"])

	deserialised_model.classes_ = numpy.array(model_dict["classes_"])
	deserialised_model.max_features_ = model_dict["max_features_"]
	deserialised_model.n_classes_ = model_dict["n_classes_"]
	deserialised_model.n_features_in_ = model_dict["n_features_in_"]
	deserialised_model.n_outputs_ = model_dict["n_outputs_"]

	tree = _deserialise_tree(
			model_dict["tree_"],
			model_dict["n_features_in_"],
			model_dict["n_classes_"],
			model_dict["n_outputs_"],
			)
	deserialised_model.tree_ = tree

	return deserialised_model


def serialise_random_forest(model: RandomForestClassifier) -> Dict[str, Any]:
	"""
	Serialise a random forest to a JSON-safe dictionary.

	:param model: Trained random forest.
	"""

	serialised_model = {
			"max_depth": model.max_depth,
			"min_samples_split": model.min_samples_split,
			"min_samples_leaf": model.min_samples_leaf,
			"min_weight_fraction_leaf": model.min_weight_fraction_leaf,
			"max_features": model.max_features,
			"max_leaf_nodes": model.max_leaf_nodes,
			"min_impurity_decrease": model.min_impurity_decrease,
			"n_features_in_": model.n_features_in_,
			"n_outputs_": model.n_outputs_,
			"classes_": model.classes_.tolist(),
			"estimators_": [serialise_decision_tree(decision_tree) for decision_tree in model.estimators_],
			"params": model.get_params()
			}

	if "oob_score_" in model.__dict__:
		serialised_model["oob_score_"] = model.oob_score_
	if "oob_decision_function_" in model.__dict__:
		serialised_model["oob_decision_function_"] = model.oob_decision_function_.tolist()

	if isinstance(model.n_classes_, int):
		serialised_model["n_classes_"] = model.n_classes_
	else:
		serialised_model["n_classes_"] = model.n_classes_.tolist()

	return serialised_model


def deserialise_random_forest(model_dict: Dict[str, Any]) -> RandomForestClassifier:
	"""
	Deserialise a random forest.

	:param model_dict: JSON-safe representation of the random forest.
	"""

	model = RandomForestClassifier(**model_dict["params"])
	estimators = [deserialise_decision_tree(decision_tree) for decision_tree in model_dict["estimators_"]]
	model.estimators_ = numpy.array(estimators)

	model.classes_ = numpy.array(model_dict["classes_"])
	model.n_features_in_ = model_dict["n_features_in_"]
	model.n_outputs_ = model_dict["n_outputs_"]
	model.max_depth = model_dict["max_depth"]
	model.min_samples_split = model_dict["min_samples_split"]
	model.min_samples_leaf = model_dict["min_samples_leaf"]
	model.min_weight_fraction_leaf = model_dict["min_weight_fraction_leaf"]
	model.max_features = model_dict["max_features"]
	model.max_leaf_nodes = model_dict["max_leaf_nodes"]
	model.min_impurity_decrease = model_dict["min_impurity_decrease"]

	if "oob_score_" in model_dict:
		model.oob_score_ = model_dict["oob_score_"]
	if "oob_decision_function_" in model_dict:
		model.oob_decision_function_ = model_dict["oob_decision_function_"]

	if isinstance(model_dict["n_classes_"], list):
		model.n_classes_ = numpy.array(model_dict["n_classes_"])
	else:
		model.n_classes_ = model_dict["n_classes_"]

	return model
