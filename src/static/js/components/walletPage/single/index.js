import React, { Component} from "react";
import { Route } from 'react-router-dom';

import WalletContainer from './walletContainer';
import WalletSingleHome from './home';
import WalletSingleWithdraw from './withdraw/index';

export default class WalletSingle extends Component {
  render() {
    return (
      <WalletContainer>
        <Route exact path='/wallet/:wallet' component={WalletSingleHome} />
        <Route path='/wallet/:wallet/withdraw/:type' component={WalletSingleWithdraw} />
      </WalletContainer>
    )
  }
}
