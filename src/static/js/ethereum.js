import { providers, Contract } from 'ethers';

const config = window.walletConfig;
const CONTRACT_VIEW_TOKEN = config.viewTokenAddress;
const VIEW_TOKEN_ABI = config.viewTokenAbi;

const network = providers.networks[config.ethChain];
const provider = new providers.InfuraProvider(network, config.infuraKey);

export default provider;
export const contract = new Contract(CONTRACT_VIEW_TOKEN, VIEW_TOKEN_ABI, provider);

export function contractSigned (wallet) {
  return new Contract(CONTRACT_VIEW_TOKEN, VIEW_TOKEN_ABI, wallet);
}
