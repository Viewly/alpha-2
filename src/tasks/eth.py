import web3

from ..config import (
    VIDEO_PUBLISHER_ADDRESS,
    VIDEO_PUBLISHER_ABI,
    ETH_CHAIN,
    INFURA_KEY,
)


def get_web3(http_url: str) -> web3.Web3:
    from web3 import Web3, HTTPProvider
    return Web3(HTTPProvider(http_url))


def get_publishing_contract():
    infura_url = f'https://{ETH_CHAIN}.infura.io/{INFURA_KEY}'
    w3 = get_web3(infura_url)

    return w3.eth.contract(
        address=VIDEO_PUBLISHER_ADDRESS,
        abi=VIDEO_PUBLISHER_ABI,
    )


def is_video_published(video_id: str):
    instance = get_publishing_contract()
    return instance.call().videos(video_id)
