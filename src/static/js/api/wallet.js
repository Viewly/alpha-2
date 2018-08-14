import { utils, Wallet } from 'ethers';

import { get, put } from './request';
import provider, { CONTRACT_ADDRESS, CONTRACT_VIDEO_PUBLISHER, contract, contractSigned } from '../ethereum';

export async function walletsFetch (baseUrl) {
  const url = `${baseUrl}/wallet`;
  const { body } = await get(url);

  return body.data;
}

export async function walletSave (baseUrl, data) {
  const url = `${baseUrl}/wallet`;
  const { body } = await put(url, data);

  return body.data;
}

export async function fetchBalance(baseUrl, { address }) {
  const etherBN = await provider.getBalance(address);
  const viewBN = await contract.balanceOf(address);
  const allowance = await contract.allowance(address, CONTRACT_VIDEO_PUBLISHER);

  return {
    balanceEth: utils.formatEther(etherBN),
    balanceView: utils.formatEther(viewBN),
    allowance: utils.formatEther(allowance)
  };
}

export async function sendEthereum(baseUrl, { amount, address, privateKey }) {
  const wallet = new Wallet(privateKey, provider);
  const etherAmount = utils.parseEther(amount);

  const { hash } = await wallet.send(address, etherAmount);

  return hash;
}

export async function sendView(baseUrl, { amount, address, privateKey }) {
  const wallet = new Wallet(privateKey, provider);
  const authorizedContract = contractSigned(wallet);
  const viewAmount = utils.parseEther(amount);

  const { hash } = await authorizedContract.transfer(address, viewAmount);

  return hash;
}

export async function authorizeAllowance(baseUrl, { amount = 0, address, privateKey }) {
  const wallet = new Wallet(privateKey, provider);
  const authorizedContract = contractSigned(wallet);

  const { hash } = await authorizedContract.approve(CONTRACT_VIDEO_PUBLISHER, amount);

  return hash;
}
