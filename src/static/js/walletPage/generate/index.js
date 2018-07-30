import React, { Component} from "react";
import { Wallet } from 'ethers';

export default class WalletHome extends Component {

  state = {
    generated: false,
    wallet: {}
  }

  generateNew = () => {
    const wallet = Wallet.createRandom();

    // console.log('generated', wallet);
    console.log('ethers', wallet);
    this.setState({ wallet, generated: true });
  }

  render() {
    return (
      <div>
        Lets generate a new wallet.
        <br />
        {this.state.generated && (
          <div>
            {/* Your mnemonic: <b>{this.state.wallet.mnemonic}</b> */}
            <br />
            Your address: <b>{this.state.wallet.address}</b>
            <br />
            {/* Your private key: <b>{this.state.wallet.privateKey}</b> */}
          </div>
        )}

        <button onClick={this.generateNew}>Generate</button>
      </div>
    )
  }
}
