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
  switch (action.type) {
    case actions.SET_CONFIG:
      return { ...state, config: action.payload };
    case actions.ADD_WALLET:
      return { ...state, wallet: action.payload };
    case actions.ADD_ENCRYPTED_WALLET:
      return { ...state, encryptedWallet: action.payload };

    case actions.AUTH_TOKEN_FETCH_SUCCESS:
      return { ...state, authToken: action.data };
    case actions.WALLETS_FETCH_SUCCESS:
      let newWallets = {};
      const localWallets = getWallets();

      for (const item of [action.data]) {
        const address = `0x${item.address}`;

        // if wallet is unlocked in localstorage - save unlocked data
        if (localWallets[address] && localWallets[address].decrypted) {
          newWallets[address] = {
            decrypted: true,
            privateKey: localWallets[address].privateKey
          }
        } else {
          newWallets[address] = {
            decrypted: false,
            encryptedWallet: item
          }
        }
      }

      return { ...state, wallets: newWallets };
    default:
      return state;
  }
};

export default rootReducer;
