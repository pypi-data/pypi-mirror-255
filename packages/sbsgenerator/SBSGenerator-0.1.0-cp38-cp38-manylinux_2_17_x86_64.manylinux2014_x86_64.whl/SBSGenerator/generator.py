import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from . import logging
from .SBSGenerator import parse_vcf_files


def generate_mutation_list():
	bases = ["A", "C", "G", "T"]
	mutations = ["C>A", "C>G", "C>T", "T>A", "T>C", "T>G"]
	return [f"{y}[{x}]{m}" for x, y, m in itertools.product(mutations, bases, bases)]


def create_sort_regex(context):
	n = context // 2
	r_string = r"\w" * n + r"\[.*\]" + r"\w" * n
	return rf"({r_string})"


def increase_mutations(context: int) -> list[str]:
	"""
	Increases mutations in a given column based on a specified context.

	Args:
	    context (int): The context for increasing mutations.

	Returns:
	    list: A list of increased mutations based on the specified context.
	"""
	if context < 3:
		raise ValueError("Context must be aleast 3")
	nucleotides = ["A", "C", "G", "T"]
	combinations = list(itertools.product(nucleotides, repeat=context - 3))
	# Generate new mutations based on the context and combinations
	new_mutations = [
		f"{''.join(combo[:len(combo)//2])}{mut}{''.join(combo[len(combo)//2:])}"
		for mut in generate_mutation_list()
		for combo in combinations
	]
	return new_mutations


def compress_matrix_stepwise(sbs_folder, df, context):
	logger = logging.SingletonLogger()
	sampled_one_down = None
	if not sbs_folder.is_dir():
		sbs_folder.mkdir(parents=True, exist_ok=True)
	for c in list(range(context, 2, -2)):
		logger.log_info(f"Creating a SBS matrix with context: {c}")
		if c == context:
			sampled_one_down = df
		else:
			sampled_one_down = compress(
				sampled_one_down,
				create_sort_regex(c),
			)
		filename = sbs_folder / f"sbs.{sampled_one_down.shape[0]}.parquet"
		sampled_one_down.to_parquet(filename)
		logger.log_info(f"Stepwise compression {c} done")


def compress(df: pd.DataFrame, regex_str: str) -> pd.DataFrame:
	"""
	Compress the dataframe down by grouping rows based on the regular pattern.

	Args:
	    df (pd.DataFrame): The dataframe to be compressed.
	    regex_str (str): Regular expression pattern for extracting sorting key.

	Returns:
	    pd.DataFrame: The compressed DataFrame.
	"""
	# Define columns for sorting
	col = "MutationType"
	sort_col = "sort_key"
	# Extract sorting key based on the provided regular expressio
	df[sort_col] = df[col].str.extract(regex_str)
	# Sort the DataFrame based on the sorting key
	df = df.sort_values(sort_col)
	# Group rows based on the sorting key and sum values
	compressed_df = df.groupby(sort_col).sum(numeric_only=True).reset_index()
	# Rename columns
	compressed_df.columns = [col] + list(compressed_df.columns[1:])
	return compressed_df


class SBSGenerator:
	def __init__(self, context: int, vcf_files: list[str], ref_genome: str):
		self._logger = logging.SingletonLogger()
		self.context: int = context
		self.ref_genome: str = ref_genome
		self.mutation_list: list = increase_mutations(context)
		self.filtered_vcf, self.samples = self.parse_vcf_files(vcf_files)
		self.samples_df = self.create_samples_df()

	@property
	def count_samples(self):
		return self.samples_df.reset_index().rename(columns={"index": "MutationType"})

	def parse_vcf_files(self, vcf_files):
		self._logger.log_info("Parsing VCF files")
		filtered_vcf = parse_vcf_files(vcf_files, self.ref_genome, self.context)
		samples = np.unique(filtered_vcf[:, 0])
		return filtered_vcf, samples

	def create_samples_df(self):
		samples_df = np.zeros((len(self.mutation_list), len(self.samples)))
		return pd.DataFrame(samples_df, columns=self.samples, index=self.mutation_list)

	def count_mutations(self):
		self._logger.log_info("Counting mutations")
		df_vcf = pd.DataFrame(self.filtered_vcf, columns=["Sample", "MutationType"])
		grouped = (
			df_vcf.groupby(["Sample", "MutationType"]).size().reset_index(name="Count")
		)
		pivot_df = grouped.pivot(
			index="MutationType", columns="Sample", values="Count"
		).fillna(0)
		self.samples_df.update(pivot_df)
		# for sample in self.samples:
		# 	sample_df = self.filtered_vcf[self.filtered_vcf[:, 0] == sample]
		# 	for mutation in self.mutation_list:
		# 		count = np.sum(sample_df[:, 1] == mutation)
		# 		self.samples_df.at[mutation, sample] = count
		self._logger.log_info("Mutation counting done")
