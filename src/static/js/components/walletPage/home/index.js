import React, { Component} from "react";
import { connect } from "react-redux";
import { Link } from 'react-router-dom';

@connect((state) => ({
  wallet: state.wallet,
}))
export default class WalletHome extends Component {
  getSnapshotBeforeUpdate(prevProps) {
    const { wallet, history } = this.props;

    if (wallet !== prevProps.wallet && wallet.address) {
      history.replace(`/wallet/${wallet.address}`);
    }

    return null;
  }

  render() {
    const { history, wallet } = this.props;

    return (
      <div>
        {!wallet.address && <button onClick={() => history.push('/wallet/generate')}>Generate new wallet</button>}
      </div>
    )
  }
}
