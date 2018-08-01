import React, { Component} from "react";
import { getWallets } from '../../../utils';

export default class WalletHome extends Component {
  renderAddress = (address, wallet) => {
    const isLocked = !wallet.decrypted;

    console.log('add', wallet);

    return <li key={`address-${address}`}>{address} {isLocked && "(LOCKED)"}</li>;
  }

  render() {
    const { history } = this.props;
    const wallets = getWallets();

    return (
      <div>
        <ul>
          {Object.keys(wallets).map(address => this.renderAddress(address, wallets[address]))}
        </ul>

        <button onClick={() => history.push('/wallet/generate')}>Generate new wallet</button>
      </div>
    )
  }
}
