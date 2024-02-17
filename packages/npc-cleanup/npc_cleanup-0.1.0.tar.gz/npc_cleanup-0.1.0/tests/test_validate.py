import pytest
import npc_lims
import npc_sessions

from npc_cleanup import validation, npc


@pytest.mark.slow
@pytest.mark.onprem
@pytest.mark.parametrize("session_id", [
    '686176_2023-12-07',
])
def test_validate_upload_integrity_success(session_id):
    timing_data = next(npc.generate_timing_data(session_id))

    result = validation._validate_upload_integrity(
        *timing_data,
        session_id,
        10000,
    )

    assert result.s3_checksum == result.isilon_checksum


@pytest.mark.slow
@pytest.mark.onprem
@pytest.mark.parametrize("session_id", [
    '686176_2023-12-07',
])
def test_validate_upload_integrity_failure(session_id):
    info = npc_lims.get_session_info(
        session=session_id,
    )
    
    s3 = npc_sessions.Session(info)
    isilon = npc_sessions.Session(info.allen_path)
    timing_data = next(isilon.ephys_timing_data)
    isilon_timing_data = npc._get_timing_data(timing_data.device)
    s3_timing_data = npc._get_timing_data(
        next(
            d.device for d in s3.ephys_timing_data 
            if d.device.name.lower() != timing_data.device.name.lower()
        )
    )

    result = validation._validate_upload_integrity(
        isilon_timing_data,
        s3_timing_data,
        session_id,
        10000,
    )

    assert result.s3_checksum == result.isilon_checksum
