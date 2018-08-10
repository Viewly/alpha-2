import { get } from './request';
import { cacheSet, cacheGet } from '../utils';
import { CACHE_KEYS } from '../cache';

export async function fetchExchangeRate () {
  const cachedPrices = cacheGet(CACHE_KEYS.CMC_PRICES);

  if (cachedPrices) {
    return JSON.parse(cachedPrices);
  } else {
    // TODO - move this to configuration
    const baseUrl = 'https://api.coinmarketcap.com/v2/ticker';
    const viewId = 2963;
    const etherId = 1027;

    const [ view, ether ] = await Promise.all([
      fetchEuro(baseUrl, viewId),
      fetchEuro(baseUrl, etherId)
    ]);

    const prices = { view: view.price, eth: ether.price };
    cacheSet(CACHE_KEYS.CMC_PRICES, JSON.stringify(prices), 1800); // 1800 seconds = 30 mins

    return prices;
  }
}

async function fetchEuro (baseUrl, currencyId) {
  const url = `${baseUrl}/${currencyId}/?convert=EUR`;
  const { body: { data: { quotes: { EUR } } } } = await get(url);

  return EUR;
}
