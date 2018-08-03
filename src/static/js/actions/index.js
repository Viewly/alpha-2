import { makeApiCall, makeAuthCall } from '../api/request';
import * as authApi from '../api/auth_token';
import * as walletApi from '../api/wallet';

export const AUTH_TOKEN_FETCH_START = 'AUTH/AUTH_TOKEN_FETCH_START';
export const AUTH_TOKEN_FETCH_SUCCESS = 'AUTH/AUTH_TOKEN_FETCH_SUCCESS';
export const AUTH_TOKEN_FETCH_ERROR = 'AUTH/AUTH_TOKEN_FETCH_ERROR';
export const fetchAuthToken = makeAuthCall(authApi.fetchAuthToken, AUTH_TOKEN_FETCH_START, AUTH_TOKEN_FETCH_SUCCESS, AUTH_TOKEN_FETCH_ERROR);

export const WALLETS_FETCH_START = 'WALLET/WALLETS_FETCH_START';
export const WALLETS_FETCH_SUCCESS = 'WALLET/WALLETS_FETCH_SUCCESS';
export const WALLETS_FETCH_ERROR = 'WALLET/WALLETS_FETCH_ERROR';
export const walletsFetch = makeApiCall(walletApi.walletsFetch, WALLETS_FETCH_START, WALLETS_FETCH_SUCCESS, WALLETS_FETCH_ERROR);

export const WALLET_SAVE_START = 'WALLET/WALLET_SAVE_START';
export const WALLET_SAVE_SUCCESS = 'WALLET/WALLET_SAVE_SUCCESS';
export const WALLET_SAVE_ERROR = 'WALLET/WALLET_SAVE_ERROR';
export const walletSave = makeApiCall(walletApi.walletSave, WALLET_SAVE_START, WALLET_SAVE_SUCCESS, WALLET_SAVE_ERROR);

export const WALLET_LOCK = 'WALLET/WALLET_LOCK';
export const WALLET_UNLOCK = 'WALLET/WALLET_UNLOCK';
export const lockWallet = (address) => ({ type: WALLET_LOCK, data: { address } });
export const unlockWallet = (address, privateKey) => ({ type: WALLET_UNLOCK, data: { address, privateKey } });

export const SET_CONFIG = 'SYSTEM/SET_CONFIG'
export const ADD_WALLET = 'USER/ADD_WALLET';
export const ADD_ENCRYPTED_WALLET = 'USER/ADD_ENCRYPTED_WALLET';
export const saveConfig = config => ({ type: SET_CONFIG, payload: config });
export const saveWallet = wallet => ({ type: ADD_WALLET, payload: wallet });
export const saveEncryptedWallet = wallet => ({ type: ADD_ENCRYPTED_WALLET, payload: wallet });
