import datetime as dt
import random
from typing import Union

import web3
from eth_account import Account
from eth_utils import (
    decode_hex,
    keccak,
    to_checksum_address,
    from_wei,
    is_address,
    is_same_address,
    to_hex,
    to_normalized_address,
)
from funcy import (
    re_find,
    cache,
    partial,
    compose,
    rpartial,
    chunks,
)

from ..config import (
    VIDEO_PUBLISHER_ADDRESS,
    VIDEO_PUBLISHER_ABI,
    ETH_CHAIN,
    INFURA_KEY,
    VIEW_TOKEN_ADDRESS,
    VIEW_TOKEN_ABI,
    GAS_PRICE,
    VOTING_POWER_DELEGATOR_ADDRESS,
    VOTING_POWER_DELEGATOR_ABI,
)

null_address = '0x0000000000000000000000000000000000000000'


def get_web3(http_url: str) -> web3.Web3:
    return web3.Web3(web3.HTTPProvider(http_url))


def get_infura_web3() -> web3.Web3:
    assert ETH_CHAIN, 'Ethereum chain not provided'
    infura_url = f'https://{ETH_CHAIN}.infura.io/v3/{INFURA_KEY}'
    return get_web3(infura_url)


@cache(60)
def gas_price() -> int:
    w3 = get_infura_web3()
    try:
        # 5% + 5 gwei above infura
        price = int(float(from_wei(w3.eth.gasPrice, 'gwei')) * 1.05) + 5
        assert price > 0
    except:
        price = GAS_PRICE

    return price


def view_token():
    w3 = get_infura_web3()

    return w3.eth.contract(
        address=VIEW_TOKEN_ADDRESS,
        abi=VIEW_TOKEN_ABI,
    )


def video_publisher():
    w3 = get_infura_web3()

    return w3.eth.contract(
        address=VIDEO_PUBLISHER_ADDRESS,
        abi=VIDEO_PUBLISHER_ABI,
    )


def voting_power_delegator():
    w3 = get_infura_web3()

    return w3.eth.contract(
        address=VOTING_POWER_DELEGATOR_ADDRESS,
        abi=VOTING_POWER_DELEGATOR_ABI,
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


def get_beneficiary_address(delegator_addr: str, block_num: int = 'latest'):
    instance = voting_power_delegator()
    beneficiary = (instance.functions
                   .delegations(to_checksum_address(delegator_addr))
                   .call(block_identifier=block_num))
    if beneficiary != null_address:
        return to_checksum_address(beneficiary)


def validate_beneficiary(delegator_addr: str, beneficiary_addr: str) -> bool:
    return get_beneficiary_address(delegator_addr) == \
           to_checksum_address(beneficiary_addr)


def is_valid_address(address: str) -> bool:
    return is_address(address)


def normalize_address(address: str) -> str:
    return to_normalized_address(address)


# Distribution game stuff
# -----------------------
def min_balance_for_period(eth_address: str,
                           created_at: dt.datetime,
                           lookback_days: int = 7):
    """
    For a given ETH address, look up their minimum stake for the past lookback_days.
    Returns the lowest balance as determined by a stochastic process.

    The purpose of this method is to prevent abuse caused by
    people who are voting and moving their tokens in an attempt to
    be able to vote again.

    The evaluation will pick random blocks in the average of 1
    block per hour, and acknowledge the minimum balance during
    this period as the voting power.
    """
    w3 = get_infura_web3()
    review_period_end = int(created_at.timestamp())
    review_period_start = int((created_at - dt.timedelta(days=lookback_days)).timestamp())

    find_block = partial(find_block_from_timestamp, w3)
    review_block_range = [find_block(x).number for x in
                          (review_period_start, review_period_end)]

    # get random VIEW balances on the voter's address for the last 7 days
    # split search range into chunks that contain ~ 1 hour worth of blocks
    chunk_size = (review_block_range[1] - review_block_range[0]) // (lookback_days * 24)
    balances = map(
        lambda block_num: view_token_balance(eth_address, block_num=block_num),
        (random.randrange(*chunk_range) for chunk_range in
         chunks(chunk_size, review_block_range))
    )

    to_eth = compose(int, rpartial(from_wei, 'ether'))
    return min(to_eth(x) for x in balances)


def block_timestamp(w3, block_id_or_num: Union[str, int]):
    return w3.eth.getBlock(block_id_or_num)['timestamp']


def block_datetime(w3, block_id_or_num: Union[str, int]):
    timestamp = block_timestamp(w3, block_id_or_num)
    return dt.datetime.utcfromtimestamp(timestamp)


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


# Old signature validation
def sign_recover(message: str, signature: str) -> str:
    from eth_account.messages import defunct_hash_message
    w3 = get_infura_web3()
    message = defunct_hash_message(text=message)
    return w3.eth.account.recoverHash(message, signature=signature)


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

    def is_valid_hex(value: str):
        return all(x in 'x0123456789abcdefABCDEF' for x in value)

    msg = b''
    for arg in args:
        assert arg is not None
        if isinstance(arg, bytes):
            msg += arg
        elif isinstance(arg, str):
            if is_valid_hex(arg):
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
