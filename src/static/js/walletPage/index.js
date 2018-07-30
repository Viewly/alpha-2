import React, { Component} from "react";
import WalletPortal from './portal';
import { Route } from 'react-router-dom';
import WalletHome from './home';
import WalletGenerate from './generate';

export default class Wallet extends Component {
  render() {
    return (
      <WalletPortal>
        <Route exact path='/wallet' component={WalletHome} />
        <Route exact path='/wallet/generate' component={WalletGenerate} />
      </WalletPortal>
    )
  }
}
