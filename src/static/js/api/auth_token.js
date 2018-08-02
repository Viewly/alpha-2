import { get } from './request';

export async function fetchAuthToken (baseUrl) {
  const url = baseUrl;
  const { body } = await get(url);

  return body.auth_token;
}
