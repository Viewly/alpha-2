import React, { Component} from "react";
import { Switch, Route } from 'react-router-dom';

import Portal from '../portal';

import WalletHome from './home';
import WalletSingle from './single';
import WalletGenerator from './generate';

export default class WalletPage extends Component {
  render() {
    return (
      <Portal container='wallet-container'>
        <Switch>
          <Route exact path='/wallet' component={WalletHome} />
          <Route exact path='/wallet/generate' component={WalletGenerator} />
          <Route path='/wallet/:wallet' component={WalletSingle} />
        </Switch>
      </Portal>
    )
  }
}
