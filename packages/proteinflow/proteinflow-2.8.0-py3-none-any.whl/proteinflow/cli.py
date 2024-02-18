"""Command line interface for proteinflow."""

import os

import click

from proteinflow import (
    check_download_tags,
    check_pdb_snapshots,
    download_data,
    generate_data,
    split_data,
    unsplit_data,
)
from proteinflow.logging import get_error_summary


@click.group(help="A data processing pipeline for protein design ML tasks")
def cli():
    """Use a data processing pipeline for protein design ML tasks."""
    pass


@cli.command("check_tags", help="Print the available options for download tags")
def check_tags():
    """Print the available options for download tags."""
    print("Available tags:")
    for x in check_download_tags():
        print(f"    {x}")


@cli.command("check_snapshots", help="Print the available options for PDB snapshots")
def check_snapshots():
    """Print the available options for PDB snapshots."""
    print("Available snapshots:")
    for x in check_pdb_snapshots():
        print(f"    {x}")


@click.option(
    "--tag",
    default="20230102_stable",
    help="The name of the dataset",
)
@click.option(
    "--local_datasets_folder",
    default="./data",
    help="The folder where proteinflow datasets, temporary files and logs will be stored",
)
@click.option(
    "--skip_splitting", is_flag=True, help="Use this flag to skip splitting the data"
)
@cli.command("download", help="Download an existing ProteinFlow dataset")
def download(**kwargs):
    """Download an existing ProteinFlow dataset."""
    download_data(**kwargs)


@click.option(
    "--tag",
    help="The name of the dataset",
)
@click.option(
    "--pdb_id_list_path",
    help="List of pdb ids to download and process",
)
@click.option(
    "--local_datasets_folder",
    default="./data",
    help="The folder where proteinflow datasets, temporary files and logs will be stored",
)
@click.option(
    "--min_length",
    default=30,
    help="The minimum number of non-missing residues per chain",
)
@click.option(
    "--max_length",
    default=10000,
    help="The maximum number of residues per chain (set None for no threshold)",
)
@click.option("--resolution_thr", default=3.5, help="The maximum resolution")
@click.option(
    "--missing_ends_thr",
    default=0.3,
    help="The maximum fraction of missing residues at the ends",
)
@click.option(
    "--missing_middle_thr",
    default=0.1,
    help="The maximum fraction of missing residues in the middle (after missing ends are disregarded)",
)
@click.option(
    "--not_filter_methods",
    is_flag=True,
    help="Unless this flag is used, only files obtained with X-ray or EM will be processed",
)
@click.option(
    "--not_remove_redundancies",
    is_flag=True,
    help="Unless this flag is used, removes biounits that are doubles of others sequence wise",
)
@click.option(
    "--redundancy_thr",
    default=0.9,
    type=float,
    help="The threshold upon which sequences are considered as one and the same (default: 90%)",
)
@click.option(
    "--skip_splitting", is_flag=True, help="Use this flag to skip splitting the data"
)
@click.option(
    "--n",
    default=None,
    type=int,
    help="The number of files to process (for debugging purposes)",
)
@click.option(
    "--force", is_flag=True, help="When `True`, rewrite the files if they already exist"
)
@click.option(
    "--split_tolerance",
    default=0.2,
    type=float,
    help="The tolerance on the split ratio (default 20%)",
)
@click.option(
    "--test_split",
    default=0.05,
    type=float,
    help="The fraction of chains to put in the test set (default 5%)",
)
@click.option(
    "--valid_split",
    default=0.05,
    type=float,
    help="The fraction of chains to put in the validation set (default 5%)",
)
@click.option(
    "--pdb_snapshot",
    type=str,
    help="The pdb snapshot folder to load",
)
@click.option(
    "--load_live",
    is_flag=True,
    help="Load the files that are not in the latest PDB snapshot from the PDB FTP server (disregarded if pdb_snapshot is not none)",
)
@click.option(
    "--min_seq_id",
    default=0.3,
    type=float,
    help="Minimum sequence identity for mmseqs clustering",
)
@click.option(
    "--sabdab",
    is_flag=True,
    help="Use this flag to generate a dataset from SAbDab files instead of PDB",
)
@click.option(
    "--sabdab_data_path",
    type=str,
    help="Path to a zip file or a directory containing SAbDab files (only used if `sabdab` is `True`)",
)
@click.option(
    "--require_antigen",
    is_flag=True,
    help="Use this flag to require that the SAbDab files contain an antigen",
)
@click.option(
    "--exclude_chains",
    "-e",
    multiple=True,
    type=str,
    help="Exclude specific chains from the dataset ({pdb_id}-{chain_id}, e.g. -e 1a2b-A)",
)
@click.option(
    "--exclude_chains_file",
    type=str,
    help="Exclude specific chains from the dataset (path to a file containing the sequences to exclude, one sequence per line)",
)
@click.option(
    "--exclude_threshold",
    default=0.7,
    type=float,
    help="Exclude chains with sequence identity to exclude_chains above this threshold",
)
@click.option(
    "--exclude_clusters",
    is_flag=True,
    help="Exclude clusters that contain chains similar to chains to exclude",
)
@click.option(
    "--exclude_based_on_cdr",
    type=click.Choice(["L1", "L2", "L3", "H1", "H2", "H3"]),
    multiple=True,
    help="if given and exclude_clusters is true + the dataset is SAbDab, exclude files based on only the given CDR clusters",
)
@click.option(
    "--load_ligands",
    is_flag=True,
    help="Whether or not to load ligands found in the pdbs example: data['A']['ligand'][0]['X']",
)
@click.option(
    "--exclude_chains_without_ligands",
    is_flag=True,
    help="Exclude chains without ligands from the generated dataset",
)
@click.option(
    "--tanimoto_clustering",
    is_flag=True,
    help="Whether to use Tanimoto Clustering instead of MMSeqs2. Only works if load_ligands is set to True",
)
@click.option(
    "--foldseek",
    is_flag=True,
    help="Whether to use FoldSeek to cluster the dataset",
)
@click.option(
    "--require_ligand",
    is_flag=True,
    help="Use this flag to require that the PDB files contain a ligand",
)
@click.option(
    "--random_seed",
    default=42,
    type=int,
    help="The random seed to use for splitting",
)
@click.option(
    "--max_chains",
    default=10,
    type=int,
    help="The maximum number of chains per biounit",
)
@cli.command("generate", help="Generate a new ProteinFlow dataset")
def generate(**kwargs):
    """Generate a new ProteinFlow dataset."""
    generate_data(**kwargs)


@click.option(
    "--tag",
    help="The name of the dataset",
)
@click.option(
    "--local_datasets_folder",
    default="./data",
    help="The folder where proteinflow datasets, temporary files and logs will be stored",
)
@click.option(
    "--split_tolerance",
    default=0.2,
    type=float,
    help="The tolerance on the split ratio (default 20%)",
)
@click.option(
    "--valid_split",
    default=0.05,
    type=float,
    help="The percentage of chains to put in the validation set (default 5%)",
)
@click.option(
    "--test_split",
    default=0.05,
    type=float,
    help="The percentage of chains to put in the test set (default 5%)",
)
@click.option(
    "--ignore_existing",
    is_flag=True,
    help="Unless this flag is used, proteinflow will not overwrite existing split dictionaries for this tag and will load them instead",
)
@click.option(
    "--min_seq_id",
    default=0.3,
    type=float,
    help="Minimum sequence identity for mmseqs clustering",
)
@click.option(
    "--exclude_chains",
    "-e",
    multiple=True,
    type=str,
    help="Exclude specific chains from the dataset ({pdb_id}-{chain_id}, e.g. -e 1a2b-A)",
)
@click.option(
    "--exclude_chains_file",
    type=str,
    help="Exclude specific chains from the dataset (path to a file containing the sequences to exclude, one sequence per line)",
)
@click.option(
    "--exclude_threshold",
    default=0.7,
    type=float,
    help="Exclude chains with sequence identity to exclude_chains above this threshold",
)
@click.option(
    "--exclude_clusters",
    is_flag=True,
    help="Exclude clusters that contain chains similar to chains to exclude",
)
@click.option(
    "--exclude_based_on_cdr",
    type=click.Choice(["L1", "L2", "L3", "H1", "H2", "H3"]),
    multiple=True,
    help="if given and exclude_clusters is true + the dataset is SAbDab, exclude files based on only the given CDR clusters",
)
@click.option(
    "--random_seed",
    default=42,
    type=int,
    help="The random seed to use for splitting",
)
@click.option(
    "--exclude_chains_without_ligands",
    is_flag=True,
    help="Exclude chains without ligands from the generated dataset",
)
@click.option(
    "--tanimoto_clustering",
    is_flag=True,
    help="Whether to use Tanimoto Clustering instead of MMSeqs2. Only works if the dataset contains ligands",
)
@click.option(
    "--foldseek",
    is_flag=True,
    help="Whether to use FoldSeek to cluster the dataset",
)
@cli.command(
    "split",
    help="Split an existing ProteinFlow dataset into training, validation and test subset according to MMseqs clustering and homomer/heteromer/single chain proportions",
)
def split(**kwargs):
    """Split an existing ProteinFlow dataset into training, validation and test subset according to MMseqs clustering and homomer/heteromer/single chain proportions."""
    split_data(**kwargs)


@click.option(
    "--tag",
    help="The name of the dataset",
)
@click.option(
    "--local_datasets_folder",
    default="./data",
    help="The folder where proteinflow datasets are stored",
)
@cli.command(
    "unsplit",
    help="Move files from train, test, validation and excluded folders back into the main folder",
)
def unsplit(**kwargs):
    """Move files from train, test, validation and excluded folders back into the main folder."""
    unsplit_data(**kwargs)


@click.option(
    "--tag",
    help="The name of the dataset",
)
@click.option(
    "--local_datasets_folder",
    default="./data",
    help="The folder where proteinflow datasets are stored",
)
@cli.command("get_summary", help="Get a summary of filtering reasons from a log file")
def get_summary(tag, local_datasets_folder):
    """Get a summary of filtering reasons from a log file."""
    log_path = os.path.join(local_datasets_folder, f"proteinflow_{tag}", "log.txt")
    if not os.path.exists(log_path):
        raise ValueError(f"Log file does not exist at {log_path}")
    get_error_summary(log_path)


if __name__ == "__main__":
    cli()
