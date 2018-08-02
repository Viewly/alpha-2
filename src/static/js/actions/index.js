import { makeApi, makeAuthCall } from '../api/request';
import * as api from '../api/auth_token';

export const AUTH_TOKEN_FETCH_START = 'AUTH/AUTH_TOKEN_FETCH_START';
export const AUTH_TOKEN_FETCH_SUCCESS = 'AUTH/AUTH_TOKEN_FETCH_SUCCESS';
export const AUTH_TOKEN_FETCH_ERROR = 'AUTH/AUTH_TOKEN_FETCH_ERROR';
export const fetchAuthToken = makeAuthCall(api.fetchAuthToken, AUTH_TOKEN_FETCH_START, AUTH_TOKEN_FETCH_SUCCESS, AUTH_TOKEN_FETCH_ERROR);

export const saveConfig = config => ({ type: "SET_CONFIG", payload: config });
export const saveWallet = wallet => ({ type: "ADD_WALLET", payload: wallet });
export const saveEncryptedWallet = wallet => ({ type: "ADD_ENCRYPTED_WALLET", payload: wallet });
