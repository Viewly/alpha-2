const LOCALSTORAGE_WALLETS = 'viewly-wallets';

import storageCache from './cache';

export function updateWallets(wallet) {
  // const wallets = getWallets();  // uncomment this to support multiple wallets
  const wallets = {};

  if (wallet.privateKey) {
    wallets[wallet.address.toLowerCase()] = { privateKey: wallet.privateKey, decrypted: true };
  } else {
    wallets[wallet.address.toLowerCase()] = { decrypted: false };
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
