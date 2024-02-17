import pytest
import logging
import dotenv
import numpy as np
from npc_cleanup import checksum


dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "args, expected",
    [
        (
            (np.zeros((1000, 200)), 20, 1000,),
            "46220D0C",
        ),
        (
            (np.zeros((1000, 200)), 1000, 1000,),
            "6522DF69",
        ),
        (
            (np.ones((1000, 200)), 1000, 1000,),
            "C7F813E9",
        )
    ]
)
def test_generate_checksum(args, expected):
    result = checksum.checksum_array(*args)
    assert result == expected

