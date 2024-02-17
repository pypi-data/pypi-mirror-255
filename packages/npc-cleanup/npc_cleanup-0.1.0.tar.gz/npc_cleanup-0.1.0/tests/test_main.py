import pytest
from click.testing import CliRunner

from npc_cleanup import __main__, validation


@pytest.mark.onprem
@pytest.mark.parametrize("session_id", [
    (
        '686176_2023-12-07',
    )
])
def test_validate_npc_session(session_id, tmp_path, monkeypatch):
    monkeypatch.setattr(
        validation.checksum,
        'checksum_array',
        lambda *args, **kwargs: "bur",
    )
    runner = CliRunner()
    output_path = tmp_path / "validation.json"
    result = runner.invoke(
        __main__.validate_npc_session,
        [
            session_id,
            f"--output_path={output_path}",
        ],
    )
    assert result.exit_code == 0
    assert output_path.is_file()