import { get } from './request';

export async function fetchAuthToken (baseUrl) {
  const { body } = await get(baseUrl);

  return body.auth_token;
}
