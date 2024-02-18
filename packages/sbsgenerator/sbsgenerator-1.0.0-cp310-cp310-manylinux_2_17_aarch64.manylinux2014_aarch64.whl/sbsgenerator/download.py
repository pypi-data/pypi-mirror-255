#!/usr/bin/env python3
"""
This module provides functions to download reference genomes.
And skip the download if the reference genome already exists.
If some of the files are missing, it will delete the folder and download the reference genome again.

* download_ref_genomes(folder: Path) -> callable: Download reference genomes (GRCh37, GRCh38).
"""
import os
import requests
import tarfile
from pathlib import Path

from . import logging

# Dictionary of reference genomes and their chromosomes *.txt files
CHECK_REF_GENOMES = {
	"GRCh37": list(range(1, 23)) + ["Y", "X", "MT"],
	"GRCh38": list(range(1, 23)) + ["Y", "X", "MT"],
}


def download_ref_genomes(folder: Path) -> None:
	"""
	Download reference genomes.

	Args:
	    folder (Path): The folder where the reference genomes will be downloaded.

	Returns:
	    None
	"""
	ref_genomes = ["GRCh37", "GRCh38"]
	for _ref_genome in ref_genomes:
		download_ref_genome(folder, _ref_genome)


def download_ref_genome(folder: Path, ref_genome: str) -> None:
	"""
	Downloads a reference genome if it doesn't already exist in the specified folder.

	Args:
	    folder (Path): The folder where the reference genome will be downloaded.
	    ref_genome (str): The name of the reference genome.

	Returns:
	    None
	"""
	# Log to the console
	logger: logging.SingletonLogger = logging.SingletonLogger()
	if check_ref_genome(folder, ref_genome):
		logger.log_info(f"{ref_genome} already exists in '{folder / ref_genome}'")
		return
	# Delete children if the folder exists but not complete
	if (folder / ref_genome).exists():
		delete_children(folder / ref_genome)
	download_path = folder / f"{ref_genome}.tar.gz"
	logger.log_info(
		f"Beginning downloading of reference {ref_genome}. "
		"This may take up to 40 minutes to complete."
	)
	# Download the tar.gz file
	url = f"https://ngs.sanger.ac.uk/scratch/project/mutographs/SigProf/{ref_genome}.tar.gz"
	download_tar_url(url, download_path, folder, ref_genome)


def delete_children(folder: Path) -> None:
	"""
	Deletes all the files in the given folder.

	Args:
	    folder (Path): The folder to delete the files from.

	Returns:
	    None
	"""
	for child in folder.iterdir():
		if child.is_file():
			child.unlink()


def check_ref_genome(folder: Path, ref_genome: str) -> bool:
	"""
	Check if all the required reference genome files exist in the specified folder.

	Args:
	    folder (Path): The folder where the reference genome files are located.
	    ref_genome (str): The name of the reference genome.

	Returns:
	    bool: True if all the required files exist, False otherwise.
	"""
	t_path = folder / ref_genome
	for chr in CHECK_REF_GENOMES[ref_genome]:
		if not (t_path / f"{chr}.txt").exists():
			return False
	return True


def download_tar_url(url: str, download_path: Path, extracted_path: Path, genome: str) -> None:
	"""
	    Download a tar.gz file from the provided URL, extract its contents, and clean up.

	    Args:
	        url (str): URL of the tar.gz file.
	        download_path (Path): Path to save the downloaded tar.gz file.
	        extracted_path (Path): Path to extract the contents of the tar.gz file.
	        genome (str): Name of the reference genome.

	Returns:
	    None
	"""
	logger: logging.SingletonLogger = logging.SingletonLogger()
	# Download the tar.gz file
	response = requests.get(url)
	# Check if the request was successful
	if response.status_code == 200:
		logger.log_info("Finished downloading the file")
		# Save the downloaded tar.gz file
		with open(download_path, "wb") as file:
			file.write(response.content)
		# Extract the contents of the tar.gz file
		with tarfile.open(download_path, "r:gz") as tar:
			tar.extractall(extracted_path)
		logger.log_info(f"Finished extracting {genome} to '{extracted_path}'!")
		# Clean up by removing the downloaded tar.gz file
		os.remove(download_path)
	else:
		logger.log_warning(
			(
				"The Sanger ftp site is not responding. "
				"Please check your internet connection/try again later."
			)
		)
