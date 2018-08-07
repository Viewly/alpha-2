import { providers, Contract } from 'ethers';
import abi from './abi.json';

// TODO - move to config
const CONTRACT_ADDRESS = '0xfbce7c17608ebd5640313ecf4d2ff09b6726bab9';
const INFURA_KEY = 'eb728907377046c1bc20b92a6fe13e19';
const network = providers.networks.kovan;

const provider = new providers.InfuraProvider(network, INFURA_KEY);

export const contract = new Contract(CONTRACT_ADDRESS, abi, provider);

export function contractSigned (wallet) {
  return new Contract(CONTRACT_ADDRESS, abi, wallet);
}
export default provider;
