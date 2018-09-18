import axios from 'axios';

export async function get(url) {
  const response = await axios.get(url);
  return { body: response.data };
}

export async function put(url, data) {
  const response = await axios.put(url, data);
  return { body: response.data };
}

export async function patch(url, data) {
  const response = await axios.patch(url, data);
  return { body: response.data };
}

export function makeApiCall (_apiCall, startActionType, successActionType, errorActionType) {
  return function (params) {
    return async (dispatch, getState) => {
      const state = getState();

      const apiBaseUrl = state.config.apiUrl;
      const authenticationToken = state.authToken;

      dispatch({ ...params, type: startActionType });
      try {
        const data = await _apiCall(apiBaseUrl, params);
        dispatch({ ...params, data, type: successActionType });
        return data;
      } catch (error) {
        dispatch({ ...params, error, type: errorActionType });
        throw error;
      }
    };
  };
}

export function makeAuthCall (_apiCall, startActionType, successActionType, errorActionType) {
  return function (params) {
    return async (dispatch, getState) => {
      const state = getState();
      const authUrl = state.config.authUrl;

      dispatch({ ...params, type: startActionType });
      try {
        const data = await _apiCall(authUrl, params);
        dispatch({ ...params, data, type: successActionType });
        return data;
      } catch (error) {
        dispatch({ ...params, error, type: errorActionType });
        throw error;
      }
    };
  };
}
