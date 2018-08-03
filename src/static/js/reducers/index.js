import * as actions from '../actions';
import { getWallets } from '../utils';

const initialState = {
  config: { apiUrl: '' },
  wallet: {},
  encryptedWallet: {},
  authToken: '',
  wallets: {},
};

const rootReducer = (state = initialState, action) => {
  let wallet = {};
  let wallets = {};

  switch (action.type) {
    case actions.SET_CONFIG:
      return { ...state, config: action.payload };
    case actions.ADD_WALLET:
      return { ...state, wallet: action.payload };
    case actions.ADD_ENCRYPTED_WALLET:
      return { ...state, encryptedWallet: action.payload };

    case actions.AUTH_TOKEN_FETCH_SUCCESS:
      return { ...state, authToken: action.data };
    case actions.WALLET_LOCK:
      wallet = { ...state.wallets[action.data.address], decrypted: false };
      wallets = { ...state.wallets, [action.data.address]: wallet };

      return { ...state, wallets };
    case actions.WALLET_UNLOCK:
      wallet = { ...state.wallets[action.data.address], decrypted: true, privateKey: action.data.privateKey };
      wallets = { ...state.wallets, [action.data.address]: wallet };

      return { ...state, wallets };
    case actions.WALLETS_FETCH_SUCCESS:
    case actions.WALLET_SAVE_SUCCESS:
      wallets = {};
      const localWallets = getWallets();

      for (const item of [action.data]) {
        const address = `0x${item.address}`;

        // if wallet is unlocked in localstorage - save unlocked data
        if (localWallets[address] && localWallets[address].decrypted) {
          wallets[address] = {
            decrypted: true,
            encryptedWallet: item,
            privateKey: localWallets[address].privateKey
          }
        } else {
          wallets[address] = {
            decrypted: false,
            encryptedWallet: item
          }
        }
      }

      return { ...state, wallets: wallets };
    default:
      return state;
  }
};

export default rootReducer;
