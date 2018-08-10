import { get } from './request';
import { cacheSet, cacheGet } from '../utils';
import { CACHE_KEYS } from '../cache';

export async function fetchAuthToken (baseUrl) {
  const token = cacheGet(CACHE_KEYS.AUTH_TOKEN);

  if (token) {
    return token;
  } else {
    const { body } = await get(baseUrl);

    cacheSet(CACHE_KEYS.AUTH_TOKEN, body.auth_token, 60 * 60);
    return body.auth_token;
  }
}
