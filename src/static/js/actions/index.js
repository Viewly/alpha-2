import { makeApiCall, makeAuthCall } from '../api/request';
import * as authApi from '../api/auth_token';
import * as walletApi from '../api/wallet';
import * as videoApi from '../api/video';

export const AUTH_TOKEN_FETCH_START = 'AUTH/AUTH_TOKEN_FETCH_START';
export const AUTH_TOKEN_FETCH_SUCCESS = 'AUTH/AUTH_TOKEN_FETCH_SUCCESS';
export const AUTH_TOKEN_FETCH_ERROR = 'AUTH/AUTH_TOKEN_FETCH_ERROR';
export const fetchAuthToken = makeAuthCall(authApi.fetchAuthToken, AUTH_TOKEN_FETCH_START, AUTH_TOKEN_FETCH_SUCCESS, AUTH_TOKEN_FETCH_ERROR);

export const WALLET_FETCH_START = 'WALLET/WALLET_FETCH_START';
export const WALLET_FETCH_SUCCESS = 'WALLET/WALLET_FETCH_SUCCESS';
export const WALLET_FETCH_ERROR = 'WALLET/WALLET_FETCH_ERROR';
export const walletsFetch = makeApiCall(walletApi.walletsFetch, WALLET_FETCH_START, WALLET_FETCH_SUCCESS, WALLET_FETCH_ERROR);

export const WALLET_SAVE_START = 'WALLET/WALLET_SAVE_START';
export const WALLET_SAVE_SUCCESS = 'WALLET/WALLET_SAVE_SUCCESS';
export const WALLET_SAVE_ERROR = 'WALLET/WALLET_SAVE_ERROR';
export const walletSave = makeApiCall(walletApi.walletSave, WALLET_SAVE_START, WALLET_SAVE_SUCCESS, WALLET_SAVE_ERROR);

export const WALLET_LOCK = 'WALLET/WALLET_LOCK';
export const WALLET_UNLOCK = 'WALLET/WALLET_UNLOCK';
export const lockWallet = (address) => ({ type: WALLET_LOCK, data: { address } });
export const unlockWallet = (address, privateKey) => ({ type: WALLET_UNLOCK, data: { address, privateKey } });

export const VIDEO_VOTE_START = 'VIDEO/VIDEO_VOTE_START';
export const VIDEO_VOTE_SUCCESS = 'VIDEO/VIDEO_VOTE_SUCCESS';
export const VIDEO_VOTE_ERROR = 'VIDEO/VIDEO_VOTE_ERROR';
export const videoVote = makeApiCall(videoApi.videoVote, VIDEO_VOTE_START, VIDEO_VOTE_SUCCESS, VIDEO_VOTE_ERROR);

export const SET_CONFIG = 'SYSTEM/SET_CONFIG'
export const ADD_WALLET = 'USER/ADD_WALLET';
export const ADD_ENCRYPTED_WALLET = 'USER/ADD_ENCRYPTED_WALLET';
export const saveConfig = config => ({ type: SET_CONFIG, payload: config });
