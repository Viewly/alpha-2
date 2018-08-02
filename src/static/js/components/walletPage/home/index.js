import React, { Component} from "react";
import { connect } from "react-redux";
import { Link } from 'react-router-dom';

import { getWallets } from '../../../utils';

@connect((state) => ({
  wallets: state.wallets,
}))
export default class WalletHome extends Component {
  renderAddress = (address, wallet) => {
    const isLocked = !wallet.decrypted;

    // console.log('add', wallet);

    return <li key={`address-${address}`}><Link to={`/wallet/${address}`}>{address} {isLocked && "(LOCKED)"}</Link></li>;
  }

  render() {
    const { history, wallets } = this.props;
    // const wallets = getWallets();

    return (
      <div>
        <ul>
          {Object.keys(wallets).map(address => this.renderAddress(address, wallets[address]))}
        </ul>

        {Object.keys(wallets).length === 0 && <button onClick={() => history.push('/wallet/generate')}>Generate new wallet</button>}
      </div>
    )
  }
}
