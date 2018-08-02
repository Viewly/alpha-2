import { get, put } from './request';

export async function walletsFetch (baseUrl) {
  const url = `${baseUrl}/wallet`;
  const { body } = await get(url);

  return body.data;
}

export async function walletSave (baseUrl, data) {
  const url = `${baseUrl}/wallet`;
  const { body } = await put(url, data);

  return body.data;
}
