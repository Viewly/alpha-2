import React, { Component} from "react";
import { Switch, Route } from 'react-router-dom';
import { hot } from "react-hot-loader";

import HeaderButton from './headerButton';
import WalletPage from './walletPage';

class App extends Component {
  render() {
    return(
      <React.Fragment>
        <Route path='/' component={HeaderButton}/>
        <Route path='/wallet' component={WalletPage}/>
      </React.Fragment>
    );
  }
}

export default hot(module)(App);
