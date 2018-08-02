const LOCALSTORAGE_WALLETS = 'viewly-wallets';

export function updateWallets(wallet) {
  // const wallets = getWallets();  // uncomment this to support multiple wallets
  const wallets = {};

  wallets[wallet.address] = { privateKey: wallet.privateKey, decrypted: true };

  localStorage.setItem(LOCALSTORAGE_WALLETS, JSON.stringify(wallets));
}

export function getWallets() {
  return JSON.parse(localStorage.getItem(LOCALSTORAGE_WALLETS)) || {};
}
