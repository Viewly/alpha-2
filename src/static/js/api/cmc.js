import { get } from './request';
import { cacheSet, cacheGet } from '../utils';
import { CACHE_KEYS } from '../cache';
import { CMC_API, VIEW_ID, ETHEREUM_ID } from '../constants/coinmarketcap';

export async function fetchExchangeRate () {
  const cachedPrices = cacheGet(CACHE_KEYS.CMC_PRICES);

  if (cachedPrices) {
    return JSON.parse(cachedPrices);
  } else {
    const [ view, ether ] = await Promise.all([
      fetchEuro(CMC_API, VIEW_ID),
      fetchEuro(CMC_API, ETHEREUM_ID)
    ]);

    const prices = { 
      EUR: {
        view: view.EUR.price,
        eth: ether.EUR.price
      },
      USD: {
        view: view.USD.price,
        eth: ether.USD.price
      }
    };
    cacheSet(CACHE_KEYS.CMC_PRICES, JSON.stringify(prices), 1800); // 1800 seconds = 30 mins

    return prices;
  }
}

async function fetchEuro (baseUrl, currencyId) {
  const url = `${baseUrl}/${currencyId}/?convert=EUR`;
  const { body: { data: { quotes: { EUR, USD } } } } = await get(url);

  return { EUR, USD };
}
