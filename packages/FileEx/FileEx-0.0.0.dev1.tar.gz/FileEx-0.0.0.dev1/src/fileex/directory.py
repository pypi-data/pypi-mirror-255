from pathlib import Path as _Path
import shutil as _shutil

from fileex import exception as _exception


def delete_contents(
    path: str | _Path, exclude: list[str] | None = None, raise_existence: bool = True
) -> list[str] | None:
    """
    Delete all files and directories within a given directory,
    excluding those specified by `exclude`.

    Parameters
    ----------
    path : str | pathlib.Path
        Path to the directory whose content should be deleted.
    exclude : list[str] | None, default: None
        List of file and directory names to exclude from deletion.
    raise_existence : bool, default: True
        Raise an error when the directory does not exist.

    Returns
    -------
    deleted_names : list[str] | None
        Names of the files and directories that were deleted,
        or None if the directory does not exist and `raise_existence` is set to False.

    Raises
    ------
    fileex.exception.FileExPathNotFoundError
        If the directory does not exist and `raise_existence` is set to True.
    """
    path = _Path(path)
    if not path.is_dir():
        if raise_existence:
            raise _exception.FileExPathNotFoundError(path, is_dir=True)
        return
    if not exclude:
        exclude = []
    deleted_names = []
    for item in path.iterdir():
        if item.name not in exclude:
            deleted_names.append(item.name)
            item.unlink() if item.is_file() else _shutil.rmtree(item)
    return deleted_names
