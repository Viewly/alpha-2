import axios from 'axios';

export async function get(url) {
  const response = await axios.get(url);
  return { body: response.data };
}

export function makeApi (_apiCall, startActionType, successActionType, errorActionType) {
  return function (params) {
    return async (dispatch, getState) => {
      const state = getState();

      const apiBaseUrl = state.config.apiUrl;
      const authenticationToken = '123';

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
