import { applyMiddleware, createStore } from "redux";
import rootReducer from "../reducers/index";
import logger from 'redux-logger'
import thunk from 'redux-thunk';

const store = createStore(
  rootReducer,
  // window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__(),
  applyMiddleware(thunk, logger)
)

export default store;
