import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter } from 'react-router-dom'
import { Provider } from "react-redux";
import store from "./store/index";
import App from "./App.js";

ReactDOM.render((
    <Provider store={store}>
      <BrowserRouter>
          <App />
      </BrowserRouter>
    </Provider>
  ), document.getElementById("wallet_app_container")
);
