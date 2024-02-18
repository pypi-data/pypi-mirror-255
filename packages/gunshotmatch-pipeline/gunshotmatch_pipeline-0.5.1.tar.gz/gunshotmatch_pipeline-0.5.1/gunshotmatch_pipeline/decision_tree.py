#!/usr/bin/env python3
#
#  decision_tree.py
"""
Prepare data and train decision trees.

.. autosummary-widths:: 53/100
"""
#
#  Copyright © 2023 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from statistics import mean, stdev
from string import ascii_lowercase
from typing import Collection, List, Tuple

# 3rd party
import graphviz  # type: ignore[import]
import pandas  # type: ignore[import]
import sklearn.tree  # type: ignore[import]
from domdf_python_tools.paths import PathPlus
from libgunshotmatch.project import Project
from libgunshotmatch.utils import get_truncated_normal
from sklearn.base import ClassifierMixin  # type: ignore[import]
from sklearn.ensemble import RandomForestClassifier  # type: ignore[import]

# this package
import gunshotmatch_pipeline.results
from gunshotmatch_pipeline.projects import Projects
from gunshotmatch_pipeline.results import unknown_machine_learning_data
from gunshotmatch_pipeline.unknowns import UnknownSettings
from gunshotmatch_pipeline.utils import friendly_name_mapping

__all__ = (
		"data_from_projects",
		"fit_decision_tree",
		"simulate_data",
		"visualise_decision_tree",
		"get_feature_names",
		"data_from_unknown",
		"dotsafe_name",
		)

# Columns which don't correspond to compounds (features); i.e. metadata columns
_non_feature_columns = {"class", "member_id", "class-id"}


def data_from_projects(
		projects: Projects,
		normalize: bool = False,
		) -> Tuple[pandas.DataFrame, List[str]]:
	"""
	Returns a :class:`~pandas.DataFrame` containing decision tree data for the given projects.

	:param projects:
	:param normalize:
	"""

	# data = pandas.DataFrame.from_dict(_machine_learning_data(projects, normalize))
	data = pandas.DataFrame.from_dict(
			gunshotmatch_pipeline.results.machine_learning_data(
					*projects.iter_loaded_projects(), normalize=normalize
					)
			)

	data = data.rename(friendly_name_mapping, axis=1).fillna(0.0)
	# feature_names = list(data.columns)
	data["class"] = [name[:-2] for name in data.index]
	data["member_id"] = [name[-1] for name in data.index]
	data["class-id"], factorize_map = pandas.factorize(pandas.Categorical(data["class"]), sort=True)

	# feature_names = get_feature_names(data)
	return data, list(factorize_map)


def data_from_unknown(
		unknown: UnknownSettings,
		feature_names: Collection[str],
		normalize: bool = False,  # ) -> Tuple[pandas.DataFrame, List[str]]:
		) -> pandas.DataFrame:
	"""
	Returns a :class:`~pandas.DataFrame` containing decision tree data for the given unknown.

	:param unknown:
	:param feature_names: The compounds the decision tree was trained on. Extra compounds in the unknown will be excluded.
	:param normalize:
	"""

	project = Project.from_file(PathPlus(unknown.output_directory) / f"{unknown.name}.gsmp")
	data = pandas.DataFrame.from_dict(unknown_machine_learning_data(project, normalize))
	data = data.rename(friendly_name_mapping, axis=1).fillna(0.0)

	# data = data[list(existing_compounds & unknowns_compounds)]
	for compound in set(feature_names).difference(data.columns):
		data[compound] = 0.0

	return data[feature_names]


def simulate_data(
		project: Project,
		normalize: bool = False,
		n_simulated: int = 10,
		) -> pandas.DataFrame:
	"""
	Generate simulated peak area data for a project.

	:param project:
	:param normalize:
	:param n_simulated: The number of values to simulate.
	"""

	propellant_data = gunshotmatch_pipeline.results.matches(project)
	df_for_norm = pandas.DataFrame(index=list("abcde"))  # TODO: handle number of repeats not being 5

	compounds_data = propellant_data["compounds"]

	for compound in compounds_data:
		df_for_norm[compound] = compounds_data[compound]["Peak Areas"]

	compounds = list(df_for_norm.columns)

	new_data: List[List[float]] = []

	for sample_idx in range(1, n_simulated + 1):
		new_data.append([])

	for compound in df_for_norm.columns:
		real_values = list(df_for_norm[compound])
		real_mean = mean(real_values)
		real_stdev = stdev(real_values)

		simulated_values = get_truncated_normal(
				real_mean,
				real_stdev,
				min(real_values),
				max(real_values),
				n_simulated,
				random_state=20230703,
				)

		# print(compound, simulated_values)

		for sample_idx, value in enumerate(simulated_values):
			new_data[sample_idx].append(value)

	real_data_size = len(df_for_norm)
	for sample_idx in range(n_simulated):
		# print(sample_idx, real_data_size+sample_idx)
		df_for_norm.loc[ascii_lowercase[real_data_size + sample_idx]] = new_data[sample_idx]

	if normalize:
		df_for_norm = df_for_norm.div(df_for_norm.sum(axis=1), axis=0)
		df_for_norm["total"] = df_for_norm[compounds].sum(axis=1)
		for x in df_for_norm["total"]:
			assert abs(x - 1) < 1e-10, x

	return df_for_norm


def fit_decision_tree(
		data: pandas.DataFrame,
		classifier: ClassifierMixin,
		) -> List[str]:
	"""
	Fit the classifier to the data.

	:param data:
	:param classifier:

	:returns: List of feature names
	"""

	feature_names = get_feature_names(data)
	classifier.fit(data[feature_names], data["class-id"])
	return feature_names


def get_feature_names(data: pandas.DataFrame) -> List[str]:
	"""
	Return the feature names for the given data.

	:param data:
	"""

	return list(data.columns[~data.columns.isin(_non_feature_columns)])


_dotsafe_transmap = str.maketrans({
		'<': "&lt;",
		'>': "&gt;",
		'&': "&amp;",
		"'": "&apos;",
		'"': "&quot;",
		})


def dotsafe_name(name: str) -> str:
	"""
	Return a dot (graphviz) suitable name for a sample, with special characters escaped.

	:param name:

	:rtype:

	.. versionadded:: 0.5.0
	"""

	return name.translate(_dotsafe_transmap)


def visualise_decision_tree(
		data: pandas.DataFrame,
		classifier: ClassifierMixin,
		factorize_map: List[str],
		filename: str = "decision_tree_graphivz",
		filetype: str = "svg",
		) -> None:
	"""
	Visualise a decision tree with graphviz.

	:param data:
	:param classifier:
	:param factorize_map: List of class names in the order they appear as classes in the classifier.
	:param filename: Output filename without extension; for random forest, the base filename (followed by ``-tree-n``).
	:param filetype: Output filetype (e.g. svg, png, pdf).
	"""

	# TODO: handle PathLike for filename

	feature_names = get_feature_names(data)

	def vis_tree(tree: ClassifierMixin, filename: str) -> None:
		# Get text representation of decision tree
		# text_representation = sklearn.tree.export_text(tree, feature_names=feature_names)
		# print(text_representation)

		# DOT data
		dot_data = sklearn.tree.export_graphviz(
				tree,
				out_file=None,
				feature_names=feature_names,
				class_names=list(map(dotsafe_name, factorize_map)),
				filled=True,
				special_characters=True,
				)

		# Draw graph
		graph = graphviz.Source(dot_data)
		graph.render(f"{filename}.dot", outfile=f"{filename}.{filetype}", format=filetype)

	if isinstance(classifier, RandomForestClassifier):
		for idx, tree in enumerate(classifier.estimators_):
			vis_tree(tree, f"{filename}-tree-{idx}")
	else:
		vis_tree(classifier, filename=filename)
