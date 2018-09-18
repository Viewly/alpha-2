import { utils, Wallet } from 'ethers';

import { get, put, patch } from './request';
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

export async function walletUpdate (baseUrl, data) {
  const url = `${baseUrl}/wallet`;
  const { body } = await patch(url, data);

  return body.data;
}

export async function fetchGasPrice(baseUrl) {
  const url = `${baseUrl}/gas_price`;
  const { body } = await get(url);

  return body;
}

export async function fetchBalance(baseUrl, { address }) {
  const etherBN = await provider.getBalance(address);
  const viewBN = await contract.balanceOf(address);
  const allowance = await contract.allowance(address, CONTRACT_VIDEO_PUBLISHER);

  return {
    balanceEth: +utils.formatEther(etherBN),
    balanceView: +utils.formatEther(viewBN),
    allowance: +utils.formatEther(allowance)
  };
}

async function isAddressContract (address) {
  const code = await provider.getCode(address);

  return code !== '0x';
}

export async function sendEthereum(baseUrl, { amount, address, privateKey, gasPrice = false, gasLimit = 21000 }) {
  if (!privateKey) {
    throw new Error('No private key is supplied. Is wallet locked?');
  }
  const wallet = new Wallet(privateKey, provider);
  const etherAmount = utils.parseEther(amount);
  const isContract = await isAddressContract(address);
  const txnGasLimit = (gasLimit === 21000 && isContract) ? 300000 : gasLimit;

  const { hash } = gasPrice
    ? await wallet.send(address, etherAmount, { gasLimit: parseInt(txnGasLimit, 10), gasPrice: utils.parseUnits(gasPrice.toString(), 'gwei') })
    : await wallet.send(address, etherAmount)

  return hash;
}

export async function sendView(baseUrl, { amount, address, privateKey, gasPrice = false, gasLimit = 60000 }) {
  if (!privateKey) {
    throw new Error('No private key is supplied. Is wallet locked?');
  }
  const wallet = new Wallet(privateKey, provider);
  const authorizedContract = contractSigned(wallet);
  const viewAmount = utils.parseEther(amount);

  const { hash } = gasPrice
    ? await authorizedContract.transfer(address, viewAmount, { gasLimit: parseInt(gasLimit, 10), gasPrice: utils.parseUnits(gasPrice.toString(), 'gwei') })
    : await authorizedContract.transfer(address, viewAmount);

  return hash;
}

export async function authorizeAllowance(baseUrl, { amount = 0, address, privateKey, gasPrice, gasLimit = 100000 }) {
  if (!privateKey) {
    throw new Error('No private key is supplied. Is wallet locked?');
  }
  const wallet = new Wallet(privateKey, provider);
  const authorizedContract = contractSigned(wallet);

  const { hash } = await authorizedContract.approve(CONTRACT_VIDEO_PUBLISHER, amount, { gasLimit: parseInt(gasLimit, 10), gasPrice: utils.parseUnits(gasPrice.toString(), 'gwei') });

  return hash;
}
