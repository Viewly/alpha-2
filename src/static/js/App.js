import React, { Component} from "react";
import { Switch, Route, IndexRoute } from 'react-router-dom';
import { connect } from "react-redux";
import { bindActionCreators } from 'redux';

import { saveConfig, fetchAuthToken } from './actions';
import { hot } from "react-hot-loader";

import HeaderButton from './components/headerButton';
import Wallet from './components/walletPage';

class App extends Component {
  render() {
    const { config } = this.props;

    return(
      <React.Fragment>
        <Route path='/' render={() => <HeaderButton config={config} />}/>
        <Route path='/wallet' component={Wallet} />
      </React.Fragment>
    );
  }
}

export default hot(module)(App);
