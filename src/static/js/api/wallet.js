import { get, put } from './request';

// export async function fetchWallet (baseUrl) {
//   const url = baseUrl;
//   const { body } = await get(url);
//
//   return body.auth_token;
// }

export async function walletSave (baseUrl, data) {
  const url = `${baseUrl}/wallet`;
  const { body } = await put(url, data);

  return true;
}
