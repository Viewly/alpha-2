import React, { Component} from "react";
import { Wallet } from 'ethers';

export default class GeneratorStep1 extends Component {

  state = {
    generated: false,
    wallet: {}
  }

  generateNew = () => {
    const wallet = Wallet.createRandom();

    this.setState({ wallet, generated: true });
  }

  saveWallet = () => {
    const { changeStep } = this.props;

    changeStep(2, this.state.wallet);
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
        <br />
        {this.state.generated && <button onClick={this.saveWallet}>Next</button>}
      </div>
    )
  }
}
