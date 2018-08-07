import * as actions from '../actions';
import { getWallets, getVotes } from '../utils';
import { STATUS_TYPE } from '../constants';

const initialState = {
  config: { apiUrl: '' },
  authToken: '',
  wallet: {},
  votes: getVotes(),
};

const rootReducer = (state = initialState, action) => {
  let wallet = {};
  let address;

  switch (action.type) {
    case actions.SET_CONFIG:
      return { ...state, config: action.payload };
    case actions.AUTH_TOKEN_FETCH_SUCCESS:
      return { ...state, authToken: action.data };

    case actions.VIDEO_VOTE_START:
      return { ...state, votes: { ...state.votes, [action.videoId]: STATUS_TYPE.LOADING }};
    case actions.VIDEO_VOTE_SUCCESS:
      return { ...state, votes: { ...state.votes, [action.data.videoId]: true }};
    case actions.VIDEO_VOTE_ERROR:
      return { ...state, votes: { ...state.votes, [action.videoId]: STATUS_TYPE.ERROR }};

    case actions.WALLET_LOCK:
      return { ...state, wallet: { ...state.wallet, decrypted: false, privateKey: null } };
    case actions.WALLET_UNLOCK:
      return { ...state, wallet: { ...state.wallet, decrypted: true, privateKey: action.data.privateKey } };

    case actions.WALLET_FETCH_SUCCESS:
    case actions.WALLET_SAVE_SUCCESS:
      const localWallets = getWallets();

      address = `0x${action.data.address}`;

      if (localWallets[address] && localWallets[address].decrypted) {
        wallet = { address, decrypted: true, encryptedWallet: action.data, privateKey: localWallets[address].privateKey };
      } else {
        wallet = { address, decrypted: false, encryptedWallet: action.data };
      }

      return { ...state, wallet };
    default:
      return state;
  }
};

export default rootReducer;
