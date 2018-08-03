const LOCALSTORAGE_WALLETS = 'viewly-wallets';

export function updateWallets(wallet) {
  // const wallets = getWallets();  // uncomment this to support multiple wallets
  const wallets = {};

  wallets[wallet.address.toLowerCase()] = { privateKey: wallet.privateKey, decrypted: true };

  localStorage.setItem(LOCALSTORAGE_WALLETS, JSON.stringify(wallets));
}

export function getWallets() {
  return JSON.parse(localStorage.getItem(LOCALSTORAGE_WALLETS)) || {};
}

export function getWalletByAddress(address) {
  const wallets = getWallets();

  return wallets && wallets[address] || {};
}

// export function walletsToStorage(wallets) {
//   let newData = {};
//
//   for (const item of wallets) {
//     const address = `0x${item.address}`;
//
//     newData[address] = {
//       decrypted: false,
//       encryptedWallet: item
//     };
//   }
//
//   localStorage.setItem(LOCALSTORAGE_WALLETS, JSON.stringify(newData));
// }
