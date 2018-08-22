import { get, put } from './request';
import { utils, Wallet } from 'ethers';

import provider, { CONTRACT_VIDEO_PUBLISHER, videoContract, videoContractSigned } from '../ethereum';

export async function fetchVideoPublisherData(baseUrl, { videoHex = false }) {
  const priceView = await videoContract.priceView();
  const priceEth = await videoContract.priceEth();
  const isPublished = videoHex
    ? await videoContract.videos(videoHex) !== '0x0000000000000000000000000000000000000000'
    : false;

  return {
    priceView: +utils.formatEther(priceView),
    priceViewBn: priceView,
    priceEth: +utils.formatEther(priceEth),
    priceEthBn: priceEth,
    isPublished
  };
}

export async function publishVideo(baseUrl, { videoHex, address, privateKey, value = 0, gasPrice = false, gasLimit = 60000 }) {
  const wallet = new Wallet(privateKey, provider);
  const authorizedContract = videoContractSigned(wallet);

  const { hash } = await authorizedContract.publish(videoHex, { value, gasLimit: parseInt(gasLimit, 10), gasPrice: utils.parseUnits(gasPrice.toString(), 'gwei') });

  return hash;
}
