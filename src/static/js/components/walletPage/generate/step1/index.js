import React, { Component} from "react";
import { Wallet } from 'ethers';
import { connect } from "react-redux";
import { saveWallet } from '../../../../actions';

const mapDispatchToProps = dispatch => {
  return {
    saveWallet: wallet => dispatch(saveWallet(wallet))
  };
};

class GeneratorStep1 extends Component {

  state = {
    generated: false,
    wallet: {}
  }

  generateNew = () => {
    const wallet = Wallet.createRandom();

    this.setState({ wallet, generated: true });
  }

  saveWallet = () => {
    const { saveWallet, changeStep } = this.props;

    saveWallet(this.state.wallet);
    changeStep(2);
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
        {this.state.generated && <button onClick={this.saveWallet}>Next</button>}
      </div>
    )
  }
}

export default connect(null, mapDispatchToProps)(GeneratorStep1);
