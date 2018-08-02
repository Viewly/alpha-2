import { makeApi, makeAuthCall } from '../api/request';
import * as authApi from '../api/auth_token';
import * as walletApi from '../api/wallet';

export const AUTH_TOKEN_FETCH_START = 'AUTH/AUTH_TOKEN_FETCH_START';
export const AUTH_TOKEN_FETCH_SUCCESS = 'AUTH/AUTH_TOKEN_FETCH_SUCCESS';
export const AUTH_TOKEN_FETCH_ERROR = 'AUTH/AUTH_TOKEN_FETCH_ERROR';
export const fetchAuthToken = makeAuthCall(authApi.fetchAuthToken, AUTH_TOKEN_FETCH_START, AUTH_TOKEN_FETCH_SUCCESS, AUTH_TOKEN_FETCH_ERROR);

export const WALLET_SAVE_START = 'WALLET/WALLET_SAVE_START';
export const WALLET_SAVE_SUCCESS = 'WALLET/WALLET_SAVE_SUCCESS';
export const WALLET_SAVE_ERROR = 'WALLET/WALLET_SAVE_ERROR';
export const walletSave = makeApi(walletApi.walletSave, WALLET_SAVE_START, WALLET_SAVE_SUCCESS, WALLET_SAVE_ERROR);

export const SET_CONFIG = 'SYSTEM/SET_CONFIG'
export const ADD_WALLET = 'USER/ADD_WALLET';
export const ADD_ENCRYPTED_WALLET = 'USER/ADD_ENCRYPTED_WALLET';
export const saveConfig = config => ({ type: SET_CONFIG, payload: config });
export const saveWallet = wallet => ({ type: ADD_WALLET, payload: wallet });
export const saveEncryptedWallet = wallet => ({ type: ADD_ENCRYPTED_WALLET, payload: wallet });
