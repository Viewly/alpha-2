const initialState = {
  wallet: {},
  encryptedWallet: {}
};

// const rootReducer = (state = initialState, action) => state;
const rootReducer = (state = initialState, action) => {
  switch (action.type) {
    case "ADD_WALLET":
      return { ...state, wallet: action.payload };
    case "ADD_ENCRYPTED_WALLET":
      return { ...state, encryptedWallet: action.payload };
    default:
      return state;
  }
};

export default rootReducer;
