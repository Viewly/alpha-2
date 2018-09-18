import { makeApiCall, makeAuthCall } from '../api/request';
import * as authApi from '../api/auth_token';
import * as walletApi from '../api/wallet';
import * as voteApi from '../api/vote';
import * as cmcApi from '../api/cmc';
import * as videoPublisherApi from '../api/video_publisher';
import * as transactionApi from '../api/transaction';
import * as searchApi from '../api/search';

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

export const GAS_PRICE_FETCH_START = 'WALLET/GAS_PRICE_FETCH_START';
export const GAS_PRICE_FETCH_SUCCESS = 'WALLET/GAS_PRICE_FETCH_SUCCESS';
export const GAS_PRICE_FETCH_ERROR = 'WALLET/GAS_PRICE_FETCH_ERROR';
export const fetchGasPrice = makeApiCall(walletApi.fetchGasPrice, GAS_PRICE_FETCH_START, GAS_PRICE_FETCH_SUCCESS, GAS_PRICE_FETCH_ERROR);

export const WALLET_SAVE_START = 'WALLET/WALLET_SAVE_START';
export const WALLET_SAVE_SUCCESS = 'WALLET/WALLET_SAVE_SUCCESS';
export const WALLET_SAVE_ERROR = 'WALLET/WALLET_SAVE_ERROR';
export const walletSave = makeApiCall(walletApi.walletSave, WALLET_SAVE_START, WALLET_SAVE_SUCCESS, WALLET_SAVE_ERROR);

export const WALLET_UPDATE_START = 'WALLET/WALLET_UPDATE_START';
export const WALLET_UPDATE_SUCCESS = 'WALLET/WALLET_UPDATE_SUCCESS';
export const WALLET_UPDATE_ERROR = 'WALLET/WALLET_UPDATE_ERROR';
export const walletUpdate = makeApiCall(walletApi.walletUpdate, WALLET_UPDATE_START, WALLET_UPDATE_SUCCESS, WALLET_UPDATE_ERROR);

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

export const WALLET_AUTHORIZE_ALLOWANCE_START = 'WALLET/WALLET_AUTHORIZE_ALLOWANCE_START';
export const WALLET_AUTHORIZE_ALLOWANCE_SUCCESS = 'WALLET/WALLET_AUTHORIZE_ALLOWANCE_SUCCESS';
export const WALLET_AUTHORIZE_ALLOWANCE_ERROR = 'WALLET/WALLET_AUTHORIZE_ALLOWANCE_ERROR';
export const authorizeAllowance = makeApiCall(walletApi.authorizeAllowance, WALLET_AUTHORIZE_ALLOWANCE_START, WALLET_AUTHORIZE_ALLOWANCE_SUCCESS, WALLET_AUTHORIZE_ALLOWANCE_ERROR);

export const WALLET_LOCK = 'WALLET/WALLET_LOCK';
export const WALLET_UNLOCK = 'WALLET/WALLET_UNLOCK';
export const lockWallet = (address) => ({ type: WALLET_LOCK, data: { address } });
export const unlockWallet = (address, privateKey) => ({ type: WALLET_UNLOCK, data: { address, privateKey } });

export const VOTE_VIDEO_START = 'VOTE/VOTE_VIDEO_START';
export const VOTE_VIDEO_SUCCESS = 'VOTE/VOTE_VIDEO_SUCCESS';
export const VOTE_VIDEO_ERROR = 'VOTE/VOTE_VIDEO_ERROR';
export const videoVote = makeApiCall(voteApi.videoVote, VOTE_VIDEO_START, VOTE_VIDEO_SUCCESS, VOTE_VIDEO_ERROR);

export const PUBLISHER_FETCH_DATA_START = 'VOTE/PUBLISHER_FETCH_DATA_START';
export const PUBLISHER_FETCH_DATA_SUCCESS = 'VOTE/PUBLISHER_FETCH_DATA_SUCCESS';
export const PUBLISHER_FETCH_DATA_ERROR = 'VOTE/PUBLISHER_FETCH_DATA_ERROR';
export const fetchVideoPublisherData = makeApiCall(videoPublisherApi.fetchVideoPublisherData, PUBLISHER_FETCH_DATA_START, PUBLISHER_FETCH_DATA_SUCCESS, PUBLISHER_FETCH_DATA_ERROR);

export const PUBLISHER_VIDEO_PUBLISH_START = 'VOTE/PUBLISHER_VIDEO_PUBLISH_START';
export const PUBLISHER_VIDEO_PUBLISH_SUCCESS = 'VOTE/PUBLISHER_VIDEO_PUBLISH_SUCCESS';
export const PUBLISHER_VIDEO_PUBLISH_ERROR = 'VOTE/PUBLISHER_VIDEO_PUBLISH_ERROR';
export const publishVideo = makeApiCall(videoPublisherApi.publishVideo, PUBLISHER_VIDEO_PUBLISH_START, PUBLISHER_VIDEO_PUBLISH_SUCCESS, PUBLISHER_VIDEO_PUBLISH_ERROR);

export const TRANSACTION_WAIT_START = 'VOTE/TRANSACTION_WAIT_START';
export const TRANSACTION_WAIT_SUCCESS = 'VOTE/TRANSACTION_WAIT_SUCCESS';
export const TRANSACTION_WAIT_ERROR = 'VOTE/TRANSACTION_WAIT_ERROR';
export const transactionWait = makeApiCall(transactionApi.transactionWait, TRANSACTION_WAIT_START, TRANSACTION_WAIT_SUCCESS, TRANSACTION_WAIT_ERROR);

export const TRANSACTION_PENDING_ADD_START = 'VOTE/TRANSACTION_PENDING_ADD_START';
export const TRANSACTION_PENDING_ADD_SUCCESS = 'VOTE/TRANSACTION_PENDING_ADD_SUCCESS';
export const TRANSACTION_PENDING_ADD_ERROR = 'VOTE/TRANSACTION_PENDING_ADD_ERROR';
export const transactionPendingAdd = makeApiCall(transactionApi.transactionPendingAdd, TRANSACTION_PENDING_ADD_START, TRANSACTION_PENDING_ADD_SUCCESS, TRANSACTION_PENDING_ADD_ERROR);

export const TRANSACTION_PENDING_REMOVE_START = 'VOTE/TRANSACTION_PENDING_REMOVE_START';
export const TRANSACTION_PENDING_REMOVE_SUCCESS = 'VOTE/TRANSACTION_PENDING_REMOVE_SUCCESS';
export const TRANSACTION_PENDING_REMOVE_ERROR = 'VOTE/TRANSACTION_PENDING_REMOVE_ERROR';
export const transactionPendingRemove = makeApiCall(transactionApi.transactionPendingRemove, TRANSACTION_PENDING_REMOVE_START, TRANSACTION_PENDING_REMOVE_SUCCESS, TRANSACTION_PENDING_REMOVE_ERROR);

export const SEARCH_VIDEOS_START = 'SEARCH/SEARCH_VIDEOS_START';
export const SEARCH_VIDEOS_SUCCESS = 'SEARCH/SEARCH_VIDEOS_SUCCESS';
export const SEARCH_VIDEOS_ERROR = 'SEARCH/SEARCH_VIDEOS_ERROR';
export const doSearch = makeApiCall(searchApi.doSearch, SEARCH_VIDEOS_START, SEARCH_VIDEOS_SUCCESS, SEARCH_VIDEOS_ERROR);

export const getTransaction = transactionApi.getTransaction;

export const SET_CONFIG = 'SYSTEM/SET_CONFIG'
export const ADD_WALLET = 'USER/ADD_WALLET';
export const ADD_ENCRYPTED_WALLET = 'USER/ADD_ENCRYPTED_WALLET';
export const UNLOCK_MODAL_OPEN = 'MODAL/UNLOCK_MODAL_OPEN';
export const UNLOCK_MODAL_CLOSE = 'MODAL/UNLOCK_MODAL_CLOSE';
export const unlockModalOpen = () => ({ type: UNLOCK_MODAL_OPEN });
export const unlockModalClose = () => ({ type: UNLOCK_MODAL_CLOSE });
export const saveConfig = config => ({ type: SET_CONFIG, payload: config });
