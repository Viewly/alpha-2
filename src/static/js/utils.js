const LOCALSTORAGE_WALLETS = 'viewly-wallets';

import storageCache, { CACHE_KEYS } from './cache';
import { utils } from 'ethers';
import sigUtil from 'eth-sig-util';
import ethUtil from 'ethereumjs-util';

export function updateWallets(wallet) {
  // const wallets = getWallets();  // uncomment this to support multiple wallets
  const wallets = {};

  if (wallet.privateKey) {
    wallets[wallet.address] = { privateKey: wallet.privateKey, decrypted: true };
  } else {
    wallets[wallet.address] = { decrypted: false };
  }

  localStorage.setItem(LOCALSTORAGE_WALLETS, JSON.stringify(wallets));
}

export function getWallets() {
  return JSON.parse(localStorage.getItem(LOCALSTORAGE_WALLETS)) || {};
}

export function getWalletByAddress(address) {
  const wallets = getWallets();

  return wallets && wallets[address] || {};
}

export function cacheSet (key, value, time = 3600) {
  storageCache.setCache(key, value, time);
}

export function cacheGet (key) {
  return storageCache.getCache(key);
}

export function getVotes() {
  return JSON.parse(cacheGet(CACHE_KEYS.VIDEO_VOTES) || null) || {};
}

export function saveVoteCache(videoId) {
  let votes = getVotes();

  votes[videoId] = true;
  cacheSet(CACHE_KEYS.VIDEO_VOTES, JSON.stringify(votes));
}

export function getPendingTransactions() {
  return JSON.parse(cacheGet(CACHE_KEYS.PENDING_TRANSACTIONS) || null) || [];
}

export function addPendingTransaction(transaction) {
  const transactions = getPendingTransactions();

  transactions.push(transaction);
  cacheSet(CACHE_KEYS.PENDING_TRANSACTIONS, JSON.stringify(transactions));
}

export function removePendingTransaction(txn_id) {
  const transactions = getPendingTransactions();
  const newTransactions = transactions.filter(item => item.txn_id !== txn_id)

  cacheSet(CACHE_KEYS.PENDING_TRANSACTIONS, JSON.stringify(newTransactions));
}

export function isVoted(videoId) {
  let votes = getVotes();

  return !!votes[videoId];
}

export function getFirstWallet(wallets) {
  const keys = Object.keys(wallets);
  if (keys.length === 0) {
    return false;
  }

  const address = keys[0];

  return { ...wallets[address], address };
}

/**
 * @source https://stackoverflow.com/a/2450976
 */
export function arrayShuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex) {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}

export function roundTwoDecimals(number) {
  return Math.round(number * 100)/100;
}

export function checksumAddress(address) {
  return utils.getAddress(address);
}

export function checkAddressValidity(address) {
  if (address.length !== 42) {
    return 'error';
  }

  try {
    const add = utils.getAddress(address);
    return 'valid';
  } catch (e) {
    if (e.message === 'invalid address checksum') {
      if (address === address.toLowerCase()) {
        return 'warning';
      } else {
        return 'error';
      }
    }
    return 'error';
  }
}

export function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

export function signVoteHash (videoId, address, privateKey, weight = 100) {
  const privateBuffer = ethUtil.toBuffer(privateKey);
  const time = Math.round(+new Date()/1000);
  const params = [
    {"type": "string", "name": "Video ID", "value": videoId},
    {"type": "uint8", "name": "Vote Weight (%)", "value": weight},
    {"type": "uint32", "name": "Timestamp", "value": time}
  ];

  const msgParams = { data: params };
  const signedHash = sigUtil.signTypedData(privateBuffer, msgParams);

  return {
    ecc_message: JSON.stringify([ params, address ]),
    ecc_signature: signedHash
  }
}
