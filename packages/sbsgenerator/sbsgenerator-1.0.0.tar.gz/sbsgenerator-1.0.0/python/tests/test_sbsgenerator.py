#!/usr/bin/env python3
"""
Tests the SBSGenerator class.
This tests good and bad cases for the SBSGenerator class.
"""
from pathlib import Path

import pytest

from sbsgenerator import generator


@pytest.mark.parametrize(
	"context_size,expected_shape",
	[
		(7, (24576, 325)),  # For context size 7
		(5, (1536, 325)),  # For context size 5
		(3, (96, 325)),  # For context size 3
	],
)
def test_sbsgenerator_with_context(context_size: int, expected_shape: tuple[int, int]) -> None:
	"""
	Test the SBSGenerator class with different context sizes.

	Args:
	    context_size (int): The size of the context.
	    expected_shape (tuple): The expected shape of the count_samples DataFrame.

	Returns:
	    None
	"""
	sbsgen = generator.SBSGenerator(
		context=context_size,
		vcf_files=[str(Path(__file__).parent / "files" / "test.vcf")],
		ref_genome=Path(__file__).parent / "files",
	)
	sbsgen.count_mutations()
	assert not sbsgen.count_samples.empty
	assert sbsgen.count_samples.shape == expected_shape
	assert sbsgen.count_samples["Adrenal-neoplasm::2293776"].sum() == 503
	assert sbsgen.count_samples["ALL::TARGET-10-PARBRK-04A-01D"].sum() == 179


@pytest.mark.parametrize(
	"context_size",
	[
		7,  # For context size 7
		5,  # For context size 5
		3,  # For context size 3
	],
)
def test_bad_sbsgenerator(context_size: int) -> None:
	"""
	Test case for the SBSGenerator class when no correct SBS mutations are found in VCF files.

	Args:
	    context_size (int): The size of the context to consider for SBS mutations.

	Raises:
	    generator.NoCorrectSBSMutationsFound: If no correct SBS mutations are found in the VCF files.

	Returns:
	    None
	"""
	with pytest.raises(
		generator.NoCorrectSBSMutationsFound,
		match="No correct SBS mutations found in VCF files",
	) as _:
		sbsgen = generator.SBSGenerator(
			context=context_size,
			vcf_files=[str(Path(__file__).parent / "files" / "bad_test.vcf")],
			ref_genome=Path(__file__).parent / "files",
		)
		sbsgen.count_mutations()
