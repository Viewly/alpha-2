export const ADD_ARTICLE = "ADD_ARTICLE";

export const saveWallet = wallet => ({ type: "ADD_WALLET", payload: wallet });
export const saveEncryptedWallet = wallet => ({ type: "ADD_ENCRYPTED_WALLET", payload: wallet });
