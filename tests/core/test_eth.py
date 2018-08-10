from src.core.eth import *
from eth_utils import to_wei


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


def test_is_video_published():
    assert ETH_CHAIN == 'kovan', 'This test was designed for Kovan chain.'

    assert get_publisher_address('gibberish') == null_address
    assert get_publisher_address('abc') == '0xaAF3FFEE9d4C976aA8d0CB1bb84c3C90ee6E9118'


def test_historic_view_token_balance():
    assert ETH_CHAIN == 'kovan', 'This test was designed for Kovan chain.'

    address = '0xaAF3FFEE9d4C976aA8d0CB1bb84c3C90ee6E9118'
    assert view_token_balance(address, block_num=7763177) == 0
    assert view_token_balance(address, block_num=8319319) == to_wei(99_979.99, 'ether')


def test_find_block_from_timestamp():
    assert ETH_CHAIN == 'kovan', 'This test was designed for Kovan chain.'

    w3 = get_infura_web3()

    # block out of search range
    assert not find_block_from_timestamp(w3, 1_000_000_000)

    # block in search range
    # fix the high so that the test works in the future as well
    match = find_block_from_timestamp(w3, 1_523_500_232, high=6877888)
    assert match and abs(match.number - 6833449) < 30,\
        'Block should have been found'

    # very accurate match
    match = find_block_from_timestamp(
        w3,
        timestamp=1_523_500_232,
        high=6877888,
        accuracy_range_seconds=1)
    assert match and match.number == 6833449,\
        'Accurate block should have been found'
