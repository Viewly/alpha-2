import { makeApiCall, makeAuthCall } from '../api/request';
import * as authApi from '../api/auth_token';
import * as walletApi from '../api/wallet';
import * as videoApi from '../api/video';
import * as cmcApi from '../api/cmc';

export const AUTH_TOKEN_FETCH_START = 'AUTH/AUTH_TOKEN_FETCH_START';
export const AUTH_TOKEN_FETCH_SUCCESS = 'AUTH/AUTH_TOKEN_FETCH_SUCCESS';
export const AUTH_TOKEN_FETCH_ERROR = 'AUTH/AUTH_TOKEN_FETCH_ERROR';
export const fetchAuthToken = makeAuthCall(authApi.fetchAuthToken, AUTH_TOKEN_FETCH_START, AUTH_TOKEN_FETCH_SUCCESS, AUTH_TOKEN_FETCH_ERROR);

export const CMC_FETCH_START = 'CMC/CMC_FETCH_START';
export const CMC_FETCH_SUCCESS = 'CMC/CMC_FETCH_SUCCESS';
export const CMC_FETCH_ERROR = 'CMC/CMC_FETCH_ERROR';
export const fetchExchangeRate = makeApiCall(cmcApi.fetchExchangeRate, CMC_FETCH_START, CMC_FETCH_SUCCESS, CMC_FETCH_ERROR);

export const WALLET_FETCH_START = 'WALLET/WALLET_FETCH_START';
export const WALLET_FETCH_SUCCESS = 'WALLET/WALLET_FETCH_SUCCESS';
export const WALLET_FETCH_ERROR = 'WALLET/WALLET_FETCH_ERROR';
export const walletsFetch = makeApiCall(walletApi.walletsFetch, WALLET_FETCH_START, WALLET_FETCH_SUCCESS, WALLET_FETCH_ERROR);

export const WALLET_SAVE_START = 'WALLET/WALLET_SAVE_START';
export const WALLET_SAVE_SUCCESS = 'WALLET/WALLET_SAVE_SUCCESS';
export const WALLET_SAVE_ERROR = 'WALLET/WALLET_SAVE_ERROR';
export const walletSave = makeApiCall(walletApi.walletSave, WALLET_SAVE_START, WALLET_SAVE_SUCCESS, WALLET_SAVE_ERROR);

export const WALLET_FETCH_BALANCE_START = 'WALLET/WALLET_FETCH_BALANCE_START';
export const WALLET_FETCH_BALANCE_SUCCESS = 'WALLET/WALLET_FETCH_BALANCE_SUCCESS';
export const WALLET_FETCH_BALANCE_ERROR = 'WALLET/WALLET_FETCH_BALANCE_ERROR';
export const fetchBalance = makeApiCall(walletApi.fetchBalance, WALLET_FETCH_BALANCE_START, WALLET_FETCH_BALANCE_SUCCESS, WALLET_FETCH_BALANCE_ERROR);

export const WALLET_SEND_ETHEREUM_START = 'WALLET/WALLET_SEND_ETHEREUM_START';
export const WALLET_SEND_ETHEREUM_SUCCESS = 'WALLET/WALLET_SEND_ETHEREUM_SUCCESS';
export const WALLET_SEND_ETHEREUM_ERROR = 'WALLET/WALLET_SEND_ETHEREUM_ERROR';
export const sendEthereum = makeApiCall(walletApi.sendEthereum, WALLET_SEND_ETHEREUM_START, WALLET_SEND_ETHEREUM_SUCCESS, WALLET_SEND_ETHEREUM_ERROR);

export const WALLET_SEND_VIEW_START = 'WALLET/WALLET_SEND_VIEW_START';
export const WALLET_SEND_VIEW_SUCCESS = 'WALLET/WALLET_SEND_VIEW_SUCCESS';
export const WALLET_SEND_VIEW_ERROR = 'WALLET/WALLET_SEND_VIEW_ERROR';
export const sendView = makeApiCall(walletApi.sendView, WALLET_SEND_VIEW_START, WALLET_SEND_VIEW_SUCCESS, WALLET_SEND_VIEW_ERROR);

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
export const UNLOCK_MODAL_OPEN = 'MODAL/UNLOCK_MODAL_OPEN';
export const UNLOCK_MODAL_CLOSE = 'MODAL/UNLOCK_MODAL_CLOSE';
export const unlockModalOpen = () => ({ type: UNLOCK_MODAL_OPEN });
export const unlockModalClose = () => ({ type: UNLOCK_MODAL_CLOSE });
export const saveConfig = config => ({ type: SET_CONFIG, payload: config });
