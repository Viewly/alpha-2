import binascii

import web3
from eth_utils import (
    is_address,
    is_same_address,
    keccak,
    remove_0x_prefix,
    big_endian_to_int,
    to_hex,
    to_normalized_address,
)

from ..config import (
    VIDEO_PUBLISHER_ADDRESS,
    VIDEO_PUBLISHER_ABI,
    ETH_CHAIN,
    INFURA_KEY,
)


def get_web3(http_url: str) -> web3.Web3:
    return web3.Web3(web3.HTTPProvider(http_url))


def video_publisher_contract():
    infura_url = f'https://{ETH_CHAIN}.infura.io/{INFURA_KEY}'
    w3 = get_web3(infura_url)

    return w3.eth.contract(
        address=VIDEO_PUBLISHER_ADDRESS,
        abi=VIDEO_PUBLISHER_ABI,
    )


def is_video_published(video_id: str):
    instance = video_publisher_contract()
    return instance.functions.videos(to_hex(video_id)).call()


def recover_address(data: str, signature: str) -> str:
    from eth_keys import KeyAPI
    signature = binascii.unhexlify(remove_0x_prefix(signature))
    data = keccak(text=data)
    data = f"\\x19Ethereum Signed Message:\n{len(data)}{data}"
    data = bytes(data, 'utf-8')

    # web3js outputs in rsv order
    vrs = (
        ord(signature[64:65]) - 27,
        big_endian_to_int(signature[0:32]),
        big_endian_to_int(signature[32:64]),
    )
    sig = KeyAPI.Signature(vrs=vrs)
    return sig.recover_public_key_from_msg(data).to_address()


def is_valid_signature(data, signature, address) -> bool:
    return is_same_address(
        address,
        recover_address(data, signature)
    )


def is_valid_address(address: str) -> bool:
    return is_address(address)


def normalize_address(address: str) -> str:
    return to_normalized_address(address)
