import React, { Component} from "react";
import WalletPortal from './portal';
import { Route } from 'react-router-dom';

import WalletHome from './home';
import WalletGenerator from './generate';

export default class WalletPage extends Component {
  render() {
    return (
      <WalletPortal>
        <Route exact path='/wallet' component={WalletHome} />
        <Route exact path='/wallet/generate' component={WalletGenerator} />
      </WalletPortal>
    )
  }
}
