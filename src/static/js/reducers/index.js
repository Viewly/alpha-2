import * as actions from '../actions';

const initialState = {
  config: { apiUrl: '' },
  wallet: {},
  encryptedWallet: {},
  authToken: '',
  wallets: [],
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
      return { ...state, wallets: action.data };
    default:
      return state;
  }
};

export default rootReducer;
