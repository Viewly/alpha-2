import LocalStorageCache from 'localstorage-cache';

export default new LocalStorageCache(2 * 1024, 'LRU');

export const CACHE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  VIDEO_VOTES: 'video_votes'
}
