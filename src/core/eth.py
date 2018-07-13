import web3
from eth_account import Account
from eth_utils import (
    decode_hex,
    keccak,
    is_0x_prefixed,
    to_checksum_address,
    from_wei,
    is_address,
    is_same_address,
    to_hex,
    to_normalized_address,
)
from funcy import re_find, cache

from ..config import (
    VIDEO_PUBLISHER_ADDRESS,
    VIDEO_PUBLISHER_ABI,
    ETH_CHAIN,
    INFURA_KEY,
    VIEW_TOKEN_ADDRESS,
    VIEW_TOKEN_ABI,
    GAS_PRICE,
)

null_address = '0x0000000000000000000000000000000000000000'


def get_web3(http_url: str) -> web3.Web3:
    return web3.Web3(web3.HTTPProvider(http_url))


def get_infura_web3() -> web3.Web3:
    assert ETH_CHAIN, 'Ethereum chain not provided'
    infura_url = f'https://{ETH_CHAIN}.infura.io/{INFURA_KEY}'
    return get_web3(infura_url)


@cache(60)
def gas_price() -> int:
    w3 = get_infura_web3()
    try:
        # 5% above infura
        price = int(float(from_wei(w3.eth.gasPrice, 'gwei')) * 1.05)
        assert price > 0
    except:
        price = GAS_PRICE

    return price


def video_publisher():
    w3 = get_infura_web3()

    return w3.eth.contract(
        address=VIDEO_PUBLISHER_ADDRESS,
        abi=VIDEO_PUBLISHER_ABI,
    )


def view_token():
    w3 = get_infura_web3()

    return w3.eth.contract(
        address=VIEW_TOKEN_ADDRESS,
        abi=VIEW_TOKEN_ABI,
    )


@cache(30)
def confirmed_block_num(confirmations: int = 10):
    w3 = get_infura_web3()
    return w3.eth.blockNumber - confirmations


def view_token_balance(address: str, block_num: int = 'latest'):
    instance = view_token()
    address = to_checksum_address(address)
    return instance.functions.balanceOf(address).call(block_identifier=block_num)


def view_token_supply():
    instance = view_token()
    supply = instance.functions.totalSupply().call()
    return from_wei(supply, 'ether')


def get_publisher_address(video_id: str, block_num: int = 'latest'):
    instance = video_publisher()
    addr = (instance.functions
            .videos(to_hex(text=video_id))
            .call(block_identifier=block_num))
    if addr != null_address:
        addr = to_checksum_address(addr)
    return addr


def is_valid_address(address: str) -> bool:
    return is_address(address)


def normalize_address(address: str) -> str:
    return to_normalized_address(address)


# Metamask Signature Validation
# -----------------------------
def pack(*args) -> bytes:
    """
    Simulates Solidity's keccak256 packing.
    Integers can be passed as tuples where the second tuple
    element specifies the variable's size in bits, e.g.:
    keccak256((5, 32))
    would be equivalent to Solidity's
    keccak256(uint32(5))
    Default size is 256.
    """

    def format_int(value, size):
        assert isinstance(value, int)
        assert isinstance(size, int)
        if value >= 0:
            return decode_hex('{:x}'.format(value).zfill(size // 4))
        else:
            return decode_hex('{:x}'.format((1 << size) + value))

    msg = b''
    for arg in args:
        assert arg is not None
        if isinstance(arg, bytes):
            msg += arg
        elif isinstance(arg, str):
            if is_0x_prefixed(arg):
                msg += decode_hex(arg)
            else:
                msg += arg.encode()
        elif isinstance(arg, bool):
            msg += format_int(int(arg), 8)
        elif isinstance(arg, int):
            msg += format_int(arg, 256)  # note: its a trap - use tuple instead
        elif isinstance(arg, tuple):
            msg += format_int(arg[0], arg[1])
        else:
            raise ValueError('Unsupported type: {}.'.format(type(arg)))

    return msg


def keccak256(*args) -> bytes:
    return keccak(pack(*args))


def infer_int_lengths(message):
    """
    Convert int/uint types to tuple's for `pack` function to work properly.

    original:
     {"type": "uint8", "name": "Vote Weight (%)", "value": 100}
    inferred:
     {"type": "uint8", "name": "Vote Weight (%)", "value": (100, 8)}

    Only works for int and uint values.
    """
    ret = []
    for item in message:
        # todo: add support for fixed and array types.
        if 'int' in item['type']:
            # (value, integer-length)
            item['value'] = (
                item['value'],
                int(re_find(r'\d+', item['type']))
            )
        ret.append(item)

    return ret


def eth_typed_data_message(message) -> bytes:
    types = ['%s %s' % (x['type'], x['name']) for x in message]
    values = [x['value'] for x in message]

    return keccak256(keccak256(*types), keccak256(*values))


def eth_typed_data_message_eip(message) -> bytes:
    types = ['%s %s' % (x['type'], x['name']) for x in message]
    values = [x['value'] for x in message]

    return keccak256(keccak256(*types), *values)


def is_typed_signature_valid(message, signature, address) -> bool:
    msg_hash = eth_typed_data_message(infer_int_lengths(message))
    recovered_address = Account().recoverHash(msg_hash, signature=signature)
    return is_same_address(address, recovered_address)


def find_block_from_timestamp(
    w3,
    timestamp: int,
    low: int = 0,
    high: int = 0,
    search_range: int = 150_000,
    accuracy_range_seconds: int = 180):
    """
    A basic algorithm to find a block number from a timestamp.

    Args:
        w3: web3 instance
        timestamp: Target block timestamp
        low: A lower boundary to include in search.
             If left empty, head block - search_range is used (approx 10 days).
        high: Higher search boundary. If left empty, blockchain head is used.
        search_range: How many blocks to look into the past if `low` is not provided.
                      Defaults to approx 1 month on mainnet.
        accuracy_range_seconds: How many seconds of precision does the resulting block need to fall into.
                        Defaults to 3 minutes on mainnet.

    Returns:
        A block closest to the provided timestamp, or None if not found.
    """
    if not high:
        high = w3.eth.blockNumber
    if not low:
        low = high - search_range

    median = (high + low) // 2
    median_block = w3.eth.getBlock(median)
    # print(median_block.number, median_block.timestamp)

    if abs(median_block.timestamp - timestamp) <= accuracy_range_seconds:
        return median_block

    # block not found in range provided
    if abs(high - low) <= 1:
        return

    # binary search
    if timestamp > median_block.timestamp:
        low = median_block.number
    else:
        high = median_block.number

    return find_block_from_timestamp(
        w3,
        timestamp,
        low=low,
        high=high,
        search_range=search_range,
        accuracy_range_seconds=accuracy_range_seconds
    )
