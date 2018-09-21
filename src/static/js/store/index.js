import { applyMiddleware, createStore } from "redux";
import rootReducer from "../reducers/index";
import { createLogger } from 'redux-logger'
import thunk from 'redux-thunk';

const logger = createLogger({
  collapsed: true,
  predicate: (getState, action) => {
    // don't log actions that starts with SEARCH/WEB3_
    if (action.type.startsWith('SEARCH/WEB3_')) {
      return false;
    }

    return true;
  }
});

const store = createStore(
  rootReducer,
  // window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__(),
  applyMiddleware(thunk, logger)
)

export default store;
