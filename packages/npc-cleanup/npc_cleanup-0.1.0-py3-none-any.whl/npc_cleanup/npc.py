import typing
import npc_lims
import npc_sessions
import zarr
import numpy as np

from . import models, exceptions


def _get_timing_data(
    ephys_device_info: npc_sessions.EphysDeviceInfo,
) -> models.TimingData:
    """Gets timing data and path (isilon or s3).
    """
    if ephys_device_info.compressed:
        path = ephys_device_info.compressed
        return models.TimingData(
            data=zarr.open(path, mode="r")["traces_seg0"],
            path=path.path,
        )
    else:
        path = ephys_device_info.continuous / "continuous.dat"
        return models.TimingData(
            data=np.memmap(path, dtype=np.int16, mode="r", ).reshape(-1, 384),
            path=path.path,
        )


def generate_timing_data(
    session_id: str,
) -> typing.Generator[tuple[models.TimingData, models.TimingData], None, None]:
    """Generates associated isilon and s3 data.
    """
    info = npc_lims.get_session_info(
        session=session_id,
    )
    if not info.is_uploaded:
        raise exceptions.CleanupException("Data not yet uploaded.")
    
    s3 = npc_sessions.Session(info)
    isilon = npc_sessions.Session(info.allen_path)
    for timing_data in isilon.ephys_timing_data:
        isilon_timing_data = _get_timing_data(timing_data.device)
        s3_timing_data = _get_timing_data(
            next(
                d.device for d in s3.ephys_timing_data 
                if d.device.name.lower() == timing_data.device.name.lower()
            )
        )
        yield (
            isilon_timing_data,
            s3_timing_data,
        )
