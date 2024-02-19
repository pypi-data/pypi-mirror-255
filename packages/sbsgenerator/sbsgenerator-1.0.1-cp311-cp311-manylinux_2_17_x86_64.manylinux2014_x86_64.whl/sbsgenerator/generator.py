#!/usr/bin/env python3
"""
This module provides functionality for generating and analyzing single base substitutions (SBS) mutations
from Variant Call Format (VCF) files. It includes capabilities to generate mutation lists, create sorting
regular expressions, increase mutations based on context, and analyze mutations within a genomic dataset.
Key components include the generation of SBS mutation patterns, parsing of VCF files to identify mutations,
and the construction and analysis of mutation datasets with Dask and Pandas for efficient data handling.

The `SBSGenerator` class serves as the core, facilitating the processing and analysis of VCF files against
a reference genome to identify and count SBS mutations within specified genomic contexts. This involves
downloading reference genomes, parsing VCF files for mutation data, creating sample dataframes for mutation
analysis, and counting mutations with the aid of Dask for distributed computing capabilities. Exception
handling is integrated for scenarios where VCF files do not contain correct SBS mutations.

This module utilizes external libraries such as NumPy, Pandas, Dask, and custom modules for downloading
reference genomes and logging, thereby requiring these dependencies for its operation.

Usage of this module is intended for bioinformatics applications, particularly in the study of genomic
mutations and their implications in various biological contexts.
"""
import itertools
from pathlib import Path
import math
from functools import wraps

import numpy as np
import pandas as pd
import dask.dataframe as dd

from . import download, logging
from .sbsgenerator import parse_vcf_files

import itertools


def generate_mutation_list():
	"""
	Generate a list of mutations in the format 'C>A', 'C>G', etc.

	Returns:
	    list: A list of strings representing mutations.
	"""
	bases = ["A", "C", "G", "T"]
	mutations = ["C>A", "C>G", "C>T", "T>A", "T>C", "T>G"]
	return [f"{y}[{x}]{m}" for x, y, m in itertools.product(mutations, bases, bases)]


def create_sort_regex(context: int) -> str:
	"""
	Create a regular expression pattern for sorting.

	Args:
	    context (int): The context size.

	Returns:
	    str: The regular expression pattern for sorting.
	"""
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


class NotCorrectSBSMutationsFound(Exception):
	"""Exception raised when no correct SBS mutations are found."""

	pass


class NotADirectoryError(Exception):
	"""Exception raised when the argument is not a folder."""

	pass


def validate_input(func):
	@wraps(func)
	def wrapper(context, vcf_files, ref_genome, **kwargs):
		# Check if context is an odd number greater than 1 and an integer
		if not isinstance(context, int) or context < 2 or context % 2 == 0:
			raise ValueError("Context must be an odd number greater than 1.")
		# Ensure vcf_files is a list or tuple
		if not isinstance(vcf_files, (list, tuple)):
			raise TypeError("Input 'vcf_files' must be a list or tuple.")
		# Verify that vcf_files contain existing file paths
		exist_vcf_files = [str(vcf_file) for vcf_file in vcf_files if Path(vcf_file).exists()]
		if len(exist_vcf_files) < len(vcf_files):
			missing_files = set(vcf_files) - set(exist_vcf_files)
			raise FileNotFoundError(f"The following files do not exist: {', '.join(missing_files)}")
		# Normalize ref_genome to a Path object, ensuring it exists
		ref_genome_path = Path(ref_genome)
		if not ref_genome_path.is_dir():
			raise NotADirectoryError("This argument must be a folder.")
		return func(context, vcf_files, ref_genome_path, **kwargs)

	return wrapper


@validate_input
class SBSGenerator:
	def __init__(self, context: int, vcf_files: list[str], ref_genome: Path) -> None:
		"""
		Initialize the Generator object.

		Args:
		    context (int): The context value.
		    vcf_files (list[str]): List of VCF file paths.
		    ref_genome (Path): Path to the reference genome.

		Returns:
		    None
		"""
		download.download_ref_genomes(ref_genome)
		self._logger = logging.SingletonLogger()
		self.context = context
		self.vcf_files = vcf_files
		self.ref_genome = ref_genome
		self.mutation_list: list = increase_mutations(context)
		self.filtered_vcf, self.samples = self.parse_vcf_files(vcf_files)
		self.samples_df = self.create_samples_df()

	@property
	def count_samples(self) -> pd.DataFrame:
		"""
		Returns the count of samples in the generator.

		Returns:
		    pandas.DataFrame: A DataFrame with the count of samples per mutation type.
		"""
		return self.samples_df.reset_index().rename(columns={"index": "MutationType"})

	def parse_vcf_files(self, vcf_files) -> tuple[np.ndarray, np.ndarray]:
		"""
		Parses the given VCF files and returns the filtered VCF data and unique samples.

		Args:
		    vcf_files (list): A list of VCF file paths.

		Returns:
		    tuple: A tuple containing the filtered VCF data and unique samples.
		"""
		self._logger.log_info("Parsing VCF files")
		filtered_vcf = parse_vcf_files(vcf_files, str(self.ref_genome), self.context)
		if filtered_vcf.shape[0] == 0:
			raise NotCorrectSBSMutationsFound("No correct SBS mutations found in VCF files")
		samples = np.unique(filtered_vcf[:, 0])
		self._logger.log_info("Done parsing VCF files")
		return filtered_vcf, samples

	def create_samples_df(self) -> None:
		"""
		Create a DataFrame with zeros, representing the samples and mutations.

		Returns:
		    pd.DataFrame: A DataFrame with zeros, with columns representing the samples and
		                  rows representing the mutations.
		"""
		samples_df = np.zeros((len(self.mutation_list), len(self.samples)))
		return pd.DataFrame(samples_df, columns=self.samples, index=self.mutation_list)

	def _calculate_partition_size(self, df: pd.DataFrame) -> int:
		"""
		Calculates the partition size for a given DataFrame.

		Args:
		    df (pd.DataFrame): The DataFrame to calculate the partition size for.

		Returns:
		    int: The partition size for the given DataFrame.
		"""
		total_data_size_in_bytes = df.memory_usage(deep=True).sum()
		target_partition_size_in_bytes = 100 * 1024**2  # 100MB
		return max(1, math.ceil(total_data_size_in_bytes / target_partition_size_in_bytes))

	def count_mutations(self) -> None:
		"""
		Counts the mutations in the filtered VCF data and updates the samples dataframe.

		Returns:
		    None
		"""
		self._logger.log_info("Counting mutations")
		# Create a DataFrame from filtered VCF data
		df_vcf = pd.DataFrame(self.filtered_vcf, columns=["Sample", "MutationType"])
		npartitions = self._calculate_partition_size(df_vcf)
		# Convert DataFrame to Dask DataFrame
		ddf_vcf = dd.from_pandas(df_vcf, npartitions=npartitions)
		# Group by 'Sample' and 'MutationType' and count the occurrences
		# Convert counts to DataFrame and reset index
		counts_df = (
			ddf_vcf.groupby(["Sample", "MutationType"]).size().to_frame(name="Count").reset_index()
		)
		# Convert 'Sample' and 'MutationType' columns to categorical type
		counts_df["Sample"] = counts_df["Sample"].astype("category").cat.as_known()
		counts_df["MutationType"] = counts_df["MutationType"].astype("category").cat.as_known()
		# Pivot the DataFrame to get mutation counts per sample and mutation type
		pivot_df = counts_df.pivot_table(
			index="MutationType", columns="Sample", values="Count", aggfunc="sum"
		).fillna(0)
		# Compute the pivot DataFrame
		result_df = pivot_df.compute()
		# Update the samples DataFrame with the mutation counts
		self.samples_df.update(result_df)
		self._logger.log_info("Mutation counting done")

	def __repr__(self) -> str:
		"""
		Returns a string representation of the SBSGenerator object.

		Returns:
		    str: A string representation of the SBSGenerator object.
		"""
		return f"SBSGenerator(context={self.context}, vcf_files={self.vcf_files}, ref_genome={self.ref_genome})"
