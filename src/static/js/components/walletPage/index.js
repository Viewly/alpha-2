import React, { Component} from "react";
import WalletPortal from './portal';
import { Switch, Route } from 'react-router-dom';

import WalletHome from './home';
import WalletSingle from './single';
import WalletGenerator from './generate';

export default class WalletPage extends Component {
  render() {
    return (
      <WalletPortal>
        <Switch>
          <Route exact path='/wallet' component={WalletHome} />
          <Route exact path='/wallet/generate' component={WalletGenerator} />
          <Route exact path='/wallet/:wallet' component={WalletSingle} />
        </Switch>
      </WalletPortal>
    )
  }
}
