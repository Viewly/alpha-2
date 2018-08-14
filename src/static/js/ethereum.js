import { providers, Contract } from 'ethers';

const config = window.walletConfig;

const network = providers.networks[config.ethChain];
const provider = new providers.InfuraProvider(network, config.infuraKey);

export default provider;

const CONTRACT_VIEW_TOKEN = config.viewTokenAddress;
const VIEW_TOKEN_ABI = config.viewTokenAbi;
export const contract = new Contract(CONTRACT_VIEW_TOKEN, VIEW_TOKEN_ABI, provider);
export function contractSigned (wallet) {
  return new Contract(CONTRACT_VIEW_TOKEN, VIEW_TOKEN_ABI, wallet);
}

export const CONTRACT_VIDEO_PUBLISHER = config.videoPublisherAddress;
const VIDEO_PUBLISHER_ABI = config.videoPublisherAbi;
export const videoContract = new Contract(CONTRACT_VIDEO_PUBLISHER, VIDEO_PUBLISHER_ABI, provider);
export function videoContractSigned (wallet) {
  return new Contract(CONTRACT_VIDEO_PUBLISHER, VIDEO_PUBLISHER_ABI, wallet);
}
