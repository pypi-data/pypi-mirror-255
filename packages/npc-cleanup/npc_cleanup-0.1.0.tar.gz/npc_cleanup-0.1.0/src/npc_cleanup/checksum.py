import zlib

from . import exceptions


def checksum_array(
    arr,
    chunk_size_0: int = 1000,
    chunk_size_1: int = 1000,
    initial: int = 0,
) -> str:
    """Generates a CR32 checksum from a slice of a 2d array.

    Parameters
    ----------
    arr: input array
    chunk_size_0: step size for 1st dimension of array
    chunk_size_1: step size for 2nd dimension of array
    initial: seed value

    Notes
    -----
    - Steps through the array and calculates a rolling checksum
    - Changes to chunk sizes will yield different results due to changes
    in the traversal of the array
    """
    if len(arr.shape) > 2:
        raise exceptions.CleanupException(
            "Unsupported array shape: %s" % arr.shape
        )
    
    checksum = initial
    for chunk in arr[::chunk_size_0]:
        for s_chunk in chunk[::chunk_size_1]:
            checksum = zlib.crc32(s_chunk.tobytes(), checksum)
    
    return f"{checksum:08X}"
