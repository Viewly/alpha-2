import web3
from eth_account import Account
from eth_utils import (
    decode_hex,
    keccak,
    is_0x_prefixed,
)
from eth_utils import (
    is_address,
    is_same_address,
    to_hex,
    to_normalized_address,
)
from funcy import re_find

from ..config import (
    VIDEO_PUBLISHER_ADDRESS,
    VIDEO_PUBLISHER_ABI,
    ETH_CHAIN,
    INFURA_KEY,
    VIEW_TOKEN_ADDRESS,
    VIEW_TOKEN_ABI,
)


def get_web3(http_url: str) -> web3.Web3:
    return web3.Web3(web3.HTTPProvider(http_url))


def get_infura_web3() -> web3.Web3:
    infura_url = f'https://{ETH_CHAIN}.infura.io/{INFURA_KEY}'
    return get_web3(infura_url)


def video_publisher_contract():
    w3 = get_infura_web3()

    return w3.eth.contract(
        address=VIDEO_PUBLISHER_ADDRESS,
        abi=VIDEO_PUBLISHER_ABI,
    )


def view_token_contract():
    w3 = get_infura_web3()

    return w3.eth.contract(
        address=VIEW_TOKEN_ADDRESS,
        abi=VIEW_TOKEN_ABI,
    )


def view_token_balance(address: str, block_num: int = 'latest'):
    instance = view_token_contract()
    return instance.functions.balanceOf(address).call(block_identifier=block_num)


def is_video_published(video_id: str):
    instance = video_publisher_contract()
    return instance.functions.videos(to_hex(video_id)).call()


def is_valid_address(address: str) -> bool:
    return is_address(address)


def normalize_address(address: str) -> str:
    return to_normalized_address(address)


# Metamask Signature Validation
# -----------------------------
def pack(*args) -> bytes:
    """
    Simulates Solidity's keccak256 packing. Integers can be passed as tuples where the second tuple
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
