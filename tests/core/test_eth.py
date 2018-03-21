from src.core.eth import *


def test_is_valid_signature():
    signature = "0x997b22c8166703ae5d22d5e182970d9fe95f20755a0989185dac8081031b322d12696e2b705d683ab99f722fc11be4db70b502f7f52a24067e3ea9dbb3d192991b"
    assert is_valid_signature(
        data='foo',
        signature=signature,
        address='0xDD61fA8CEd6F49e70c3b9fD45F2Ed6017128a6Fd'
    )
