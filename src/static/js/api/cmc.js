import { get } from './request';

export async function fetchExchangeRate () {
  // TODO - move this to configuration
  const baseUrl = 'https://api.coinmarketcap.com/v2/ticker';
  const viewId = 2963;
  const etherId = 1027;

  const [ view, ether ] = await Promise.all([
    fetchEuro(baseUrl, viewId),
    fetchEuro(baseUrl, etherId)
  ]);

  return { view: view.price, eth: ether.price };
}

async function fetchEuro (baseUrl, currencyId) {
  const url = `${baseUrl}/${currencyId}/?convert=EUR`;
  const { body: { data: { quotes: { EUR } } } } = await get(url);

  return EUR;
}
