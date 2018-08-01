import React, { Component} from "react";
import { Switch, Route, IndexRoute } from 'react-router-dom';
import { hot } from "react-hot-loader";

import HeaderButton from './components/headerButton';
import Wallet from './components/walletPage';


class App extends Component {
  render() {
    return(
      <React.Fragment>
        <Route path='/' component={HeaderButton}/>
        <Route path='/wallet' component={Wallet} />
      </React.Fragment>
    );
  }
}

export default hot(module)(App);
