import React, { Component} from "react";
import WalletPortal from './portal';
import { Route } from 'react-router-dom';
import { connect } from "react-redux";
import WalletHome from './home';
import WalletGenerator from './generate';

@connect((state) => ({
  authToken: state.authToken,
}), null)
export default class Wallet extends Component {
  render() {
    const { authToken } = this.props;

    if (!authToken) {
      return (
        <WalletPortal>
          <div>Loading ...</div>
        </WalletPortal>
      );
    }

    return (
      <WalletPortal>
        <Route exact path='/wallet' component={WalletHome} />
        <Route exact path='/wallet/generate' component={WalletGenerator} />
      </WalletPortal>
    )
  }
}
