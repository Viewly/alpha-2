import { get } from './request';

export async function doSearch (baseUrl, { query }) {
  const url = `${baseUrl}/find/channel?q=${query}`;

  const { body } = await get(url);
  return body;
}
