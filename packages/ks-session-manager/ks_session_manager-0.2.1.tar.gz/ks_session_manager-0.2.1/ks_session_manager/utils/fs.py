import logging
import tarfile
import zipfile

from pathlib import Path
from typing import Sequence

logger = logging.getLogger(__name__)


def recursive_remove_empty_dirs(directory: str | Path):
    """
    Removes all empty directories recursively within the specified directory.

    :param directory: The directory path to start removing empty directories from.
    :type directory: str or Path
    """
    directory = Path(directory)

    for file in directory.iterdir():
        if file.is_dir():
            recursive_remove_empty_dirs(file)
            if not any(file.iterdir()):
                file.rmdir()


def tar_filter(tarinfo: tarfile.TarInfo, _) -> tarfile.TarInfo | None:
    path = Path(tarinfo.name)

    # Skip hidden files
    if path.stem.startswith('.'):
        return None

    return tarinfo


def extract_archive(archive: str | Path, output_dir: str | Path):
    """
    Extracts the contents of an archive to a specified output directory.

    Parameters:
        archive (str | Path): Path to the archive file.
        output_dir (str | Path): Path to the output directory.

    Raises:
        ValueError: If the archive type is unsupported.

    """
    archive = Path(archive)
    output_dir = Path(output_dir)

    if tarfile.is_tarfile(archive):
        with tarfile.open(archive) as tar:
            tar.extractall(output_dir, filter=tar_filter)
    elif zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as file:
            file.extractall(output_dir)
    else:
        raise ValueError(f'{archive} has unsupported archive type')


def flatten_dir_files(
        directory: str | Path,
        *,
        include_suffixes: Sequence[str] | None = None,
        remove_unmatched: bool = False
):
    """
    Flatten Dir Files

    Flattens files in a given directory and its subdirectories, optionally matching only certain file suffixes and removing unmatched files.

    Parameters
    ----------
    directory : str or Path
        The directory to flatten files in.

    include_suffixes : Sequence[str]
        A sequence of file suffixes to include. Only files with these suffixes will be flattened.
        If an empty sequence is provided, all files will be included.

    remove_unmatched : bool, optional
        If True, unmatched files (files whose suffixes do not match the provided include_suffixes) will be removed.
        Default is False.

    Returns
    -------
    None

    Notes
    -----
    - Existing files with the same name as the flattened files will be skipped.
    - Empty directories will be cleaned after file flattening.

    Examples
    --------
    >>> flatten_dir_files('path/to/directory', include_suffixes=['.txt', '.csv'], remove_unmatched=True)
    """
    target_dir = Path(directory)

    for file in target_dir.glob('**/*'):
        if file.is_file():
            if bool(include_suffixes) and file.suffix not in include_suffixes:
                if remove_unmatched:
                    file.unlink()
                continue

            target_path = Path(target_dir / file.name)

            if target_path.exists():
                logger.warning(f'File {target_path} already exists, skipping')
                continue

            file.rename(target_path)

    # Clean empty directories
    logger.info(f"Cleaning empty directories in {target_dir}")
    recursive_remove_empty_dirs(target_dir)
