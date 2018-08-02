const initialState = {
  config: { apiUrl: '' },
  wallet: {},
  encryptedWallet: {},
  auth_token: '',
};

const rootReducer = (state = initialState, action) => {
  switch (action.type) {
    case "SET_CONFIG":
      return { ...state, config: action.payload };
    case "ADD_WALLET":
      return { ...state, wallet: action.payload };
    case "AUTH/AUTH_TOKEN_FETCH_SUCCESS":
      return { ...state, auth_token: action.data };
    case "ADD_ENCRYPTED_WALLET":
      return { ...state, encryptedWallet: action.payload };
    default:
      return state;
  }
};

export default rootReducer;
