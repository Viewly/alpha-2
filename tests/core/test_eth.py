from src.core.eth import *
from eth_utils import to_wei


def test_is_video_published():
    assert is_video_published('20ltwfLhmxDa')


def test_address_utils():
    assert is_valid_address('0xF03f8D65BaFA598611C3495124093c56e8F638f0')
    assert normalize_address('0xF03f8D65BaFA598611C3495124093c56e8F638f0') \
           == '0xf03f8d65bafa598611c3495124093c56e8f638f0'


def test_is_signature_valid():
    address = '0xaaf3ffee9d4c976aa8d0cb1bb84c3c90ee6e9118'
    signature = '0x965439c02ec9399b9fce8f9eac57bfa7f93385c885c96c536dc28070bcdf0ccc6cc45c9eaf4f43b0a40c32e8f8d7e97320a92ea675fa5d826ae67521d3e669af1c'
    msg = [
        {"type": "string", "name": "Video ID", "value": "v3jMYxUpBzZ2"},
        {"type": "uint8", "name": "Vote Weight (%)", "value": 100}
    ]
    assert is_typed_signature_valid(
        message=msg,
        signature=signature,
        address=address,
    )


def test_historic_view_token_balance():
    address = '0xaAF3FFEE9d4C976aA8d0CB1bb84c3C90ee6E9118'
    assert view_token_balance(address, block_num=5876634) == 0
    assert view_token_balance(address, block_num=5876635) == to_wei(1000, 'ether')
    assert view_token_balance(address, block_num=6855595) == to_wei(740, 'ether')
