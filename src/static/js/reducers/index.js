import * as actions from '../actions';
import { getWallets, getVotes } from '../utils';
import { STATUS_TYPE } from '../constants';
import { cacheSet, cacheGet, checksumAddress, getPendingTransactions } from '../utils';
import { CACHE_KEYS } from '../cache';

const initialState = {
  config: { apiUrl: '' },
  authToken: '',
  wallet: {},
  votes: getVotes(),
  prices: {
    view: 0,
    eth: 0
  },
  gasPrice: {
    normal: 10,
    fast: 16
  },
  walletUnlockModal: false,
  videoPublisher: {
    priceEth: -1,
    priceEthBn: -1,
    priceView: -1,
    priceViewBn: -1,
    isPublished: false
  },
  transaction: {
    _status: STATUS_TYPE.LOADED,
    error: '',
    txn_id: '',
    txn: {},
    receipt: {}
  },
  search: {
    _status: STATUS_TYPE.LOADED,
    data: []
  },
  pendingTransactions: getPendingTransactions(),
  web3: {
    accounts: {
      accounts: null,
      _status: STATUS_TYPE.PENDING
    },
    network: {
      network_id: null,
      _status: STATUS_TYPE.PENDING
    }
  }
};

const rootReducer = (state = initialState, action) => {
  let wallet = {};
  let address;

  switch (action.type) {
    case actions.SET_CONFIG:
      return { ...state, config: action.payload };
    case actions.AUTH_TOKEN_FETCH_SUCCESS:
      return { ...state, authToken: action.data };

    case actions.GAS_PRICE_FETCH_SUCCESS:
      return { ...state, gasPrice: { ...action.data }};

    case actions.WEB3_FETCH_NETWORK_SUCCESS:
      return { ...state, web3: { ...state.web3, network: { network_id: parseInt(action.data, 10), _status: STATUS_TYPE.LOADED } }};
    case actions.WEB3_FETCH_ACCOUNTS_SUCCESS:
      return { ...state, web3: { ...state.web3, accounts: { accounts: action.data, _status: STATUS_TYPE.LOADED } }};

    case actions.TRANSACTION_PENDING_ADD_SUCCESS:
      return { ...state, pendingTransactions: [ ...state.pendingTransactions, action.data ]};
    case actions.TRANSACTION_PENDING_REMOVE_SUCCESS:
      return { ...state, pendingTransactions: state.pendingTransactions.filter(item => item.txn_id !== action.data) };

    case actions.SEARCH_VIDEOS_START:
      return { ...state, search: { ...state.search, _status: STATUS_TYPE.LOADING, data: [] }};
    case actions.SEARCH_VIDEOS_SUCCESS:
      return { ...state, search: { ...state.search, _status: STATUS_TYPE.LOADED, data: action.data }};
    case actions.SEARCH_VIDEOS_ERROR:
      return { ...state, search: { ...state.search, _status: STATUS_TYPE.ERROR }};

    case actions.TRANSACTION_WAIT_START:
      return { ...state, transaction: { ...state.transaction, _status: STATUS_TYPE.LOADING, error: '' }};
    case actions.TRANSACTION_WAIT_SUCCESS:
      return { ...state, transaction: { ...state.transaction, _status: STATUS_TYPE.LOADED, txn_id: action.txn_id, ...action.data }};
    case actions.TRANSACTION_WAIT_ERROR:
      return { ...state, transaction: { ...state.transaction, _status: STATUS_TYPE.ERROR, error: action.error.message }};

    case actions.VOTE_VIDEO_START:
      return { ...state, votes: { ...state.votes, [action.videoId]: STATUS_TYPE.LOADING }};
    case actions.VOTE_VIDEO_SUCCESS:
      return { ...state, votes: { ...state.votes, [action.data.videoId]: true }};
    case actions.VOTE_VIDEO_ERROR:
      return { ...state, votes: { ...state.votes, [action.videoId]: STATUS_TYPE.ERROR }};

    case actions.PUBLISHER_FETCH_DATA_START:
      return { ...state, videoPublisher: { ...state.videoPublisher, _status: STATUS_TYPE.LOADING }};
    case actions.PUBLISHER_FETCH_DATA_SUCCESS:
      return { ...state, videoPublisher: { ...state.videoPublisher, _status: STATUS_TYPE.LOADED, ...action.data }};
    case actions.PUBLISHER_FETCH_DATA_ERROR:
      return { ...state, videoPublisher: { ...state.videoPublisher, _status: STATUS_TYPE.ERROR }};

    case actions.WALLET_LOCK:
      return { ...state, wallet: { ...state.wallet, decrypted: false, privateKey: null } };
    case actions.WALLET_UNLOCK:
      return { ...state, wallet: { ...state.wallet, decrypted: true, privateKey: action.data.privateKey } };

    case actions.WALLET_FETCH_START:
      return { ...state, wallet: { ...state.wallet, _status: STATUS_TYPE.LOADING } };
    case actions.WALLET_FETCH_SUCCESS:
    case actions.WALLET_SAVE_SUCCESS:
    case actions.WALLET_UPDATE_SUCCESS:
      const localWallets = getWallets();

      address = checksumAddress(`0x${action.data.address}`);

      if (localWallets[address] && localWallets[address].decrypted) {
        wallet = { ...state.wallet, _status: STATUS_TYPE.LOADED, address, decrypted: true, encryptedWallet: action.data, privateKey: localWallets[address].privateKey };
      } else {
        wallet = { ...state.wallet, _status: STATUS_TYPE.LOADED, address, decrypted: false, encryptedWallet: action.data };
      }

      return { ...state, wallet };
    case actions.WALLET_FETCH_ERROR:
      return { ...state, wallet: { ...state.wallet, _status: STATUS_TYPE.ERROR } };

    case actions.WALLET_FETCH_BALANCE_START:
      let cachedBalance = JSON.parse(cacheGet(CACHE_KEYS.WALLET_BALANCES) || null) || { balanceEth: STATUS_TYPE.LOADING, balanceView: STATUS_TYPE.LOADING, allowance: STATUS_TYPE.LOADING };

      return { ...state, wallet: { ...state.wallet, ...cachedBalance }};
    case actions.WALLET_FETCH_BALANCE_SUCCESS:
      const { balanceEth, balanceView, allowance } = action.data;
      cacheSet(CACHE_KEYS.WALLET_BALANCES, JSON.stringify({ balanceEth, balanceView, allowance }), 1800);

      return { ...state, wallet: { ...state.wallet, balanceEth, balanceView, allowance }};

    case actions.CMC_FETCH_SUCCESS:
      return { ...state, prices: action.data};

    case actions.UNLOCK_MODAL_OPEN:
      return { ...state, walletUnlockModal: true };
    case actions.UNLOCK_MODAL_CLOSE:
      return { ...state, walletUnlockModal: false };

    default:
      return state;
  }
};

export default rootReducer;
