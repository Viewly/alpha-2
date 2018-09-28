import LocalStorageCache from 'localstorage-cache';

export default new LocalStorageCache(2 * 1024, 'LRU');

export const CACHE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  CMC_PRICES: 'cmc_prices',
  WALLET_BALANCES: 'wallet_balances',
  VIDEO_VOTES: 'video_votes',
  PENDING_TRANSACTIONS: 'pending_transactions',
  SELECTED_CURRENCY: 'selected_currency'
}
