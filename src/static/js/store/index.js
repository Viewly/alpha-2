import { applyMiddleware, createStore } from "redux";
import rootReducer from "../reducers/index";
import logger from 'redux-logger'

// const store = createStore(rootReducer);
const store = createStore(
  rootReducer,
  applyMiddleware(logger)
)


export default store;
