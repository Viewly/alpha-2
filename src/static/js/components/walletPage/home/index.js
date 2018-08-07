import React, { Component} from "react";
import { connect } from "react-redux";
import { Link } from 'react-router-dom';

import { getWallets, getFirstWallet } from '../../../utils';

@connect((state) => ({
  wallets: state.wallets,
}))
export default class WalletHome extends Component {
  getSnapshotBeforeUpdate(prevProps) {
    const { wallets, history } = this.props;
    const firstWallet = getFirstWallet(wallets);

    if (wallets !== prevProps.wallet) {
      history.replace(`/wallet/${firstWallet.address}`);
    }

    return null;
  }

  render() {
    const { history, wallets } = this.props;

    return (
      <div>
        {Object.keys(wallets).length === 0 && <button onClick={() => history.push('/wallet/generate')}>Generate new wallet</button>}
      </div>
    )
  }
}
