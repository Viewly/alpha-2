import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter } from 'react-router-dom'
import { Provider } from "react-redux";
import store from "./store/index";
import App from "./App.js";

const rootElement = document.getElementById("wallet_app_container");
const config = {
  apiUrl: rootElement.getAttribute('data-api-url'),
  authUrl: rootElement.getAttribute('data-auth-url')
}

ReactDOM.render((
  <Provider store={store}>
    <BrowserRouter>
      <App config={config} />
    </BrowserRouter>
  </Provider>), rootElement
);
