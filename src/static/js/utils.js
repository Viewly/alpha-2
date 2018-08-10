const LOCALSTORAGE_WALLETS = 'viewly-wallets';

import storageCache, { CACHE_KEYS } from './cache';
import { utils } from 'ethers';

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

export function roundTwoDecimals(number) {
  return Math.round(number * 100)/100;
}

export function checksumAddress(address) {
  return utils.getAddress(address);
}
