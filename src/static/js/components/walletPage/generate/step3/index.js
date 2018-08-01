import React, { Component} from "react";
import { Wallet } from 'ethers';
import { connect } from "react-redux";
import { saveEncryptedWallet } from '../../../../actions';

const mapDispatchToProps = dispatch => {
  return {
    saveEncryptedWallet: wallet => dispatch(saveEncryptedWallet(wallet))
  };
};

const mapStateToProps = state => {
  return { wallet: state.wallet };
};

class GeneratorStep3 extends Component {
  state = {
    password: '',
    progress: 0,
    encrypting: false
  }

  encryptWallet = () => {
    const { wallet, saveEncryptedWallet, changeStep } = this.props;

    this.setState({ encrypting: true });

    var encryptPromise = wallet.encrypt(this.state.password, (progress) => {
      this.setState({ progress });
    });

    encryptPromise.then((json) => {
      saveEncryptedWallet(json);
      changeStep(4);
    });
  }

  render() {
    const { wallet } = this.props;

    return (
      <div>
        Lets encrypt your wallet so its 100% secure
        <br />
        Type new password -
        <input type="password" name="password" value={this.state.password} onChange={(e) => this.setState({ password: e.target.value })} />
        <strong>(if you forget this password, we can't recover it. Only way to recover your wallet is using mnemonic from last step)</strong>
        <br />

        {!this.state.encrypting && <button onClick={this.encryptWallet}>Encrypt</button>}

        {this.state.encrypting && <div>Progress: {Math.round(this.state.progress * 100)}%</div>}
      </div>
    )
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(GeneratorStep3);
