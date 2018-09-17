import React, { Component} from "react";
import { connect } from "react-redux";
import { Wallet } from 'ethers';
import { unlockWallet } from '../../../actions';

@connect((state, props) => ({
  wallet: state.wallet.address === props.match.params.wallet && state.wallet,
}), (dispatch) => ({
  unlockWallet: (address, privateKey) => dispatch(unlockWallet(address, privateKey))
}))
export default class WalletRecover extends Component {
  state = {
    mnemonic: '',
    error: false,
    errorText: ''
  }

  checkMnemonic = () => {
    const { wallet, unlockWallet, history } = this.props;

    this.setState({ error: false });
    try {
      const newWallet = Wallet.fromMnemonic(this.state.mnemonic);

      if (newWallet.address !== wallet.address) {
        this.setState({ error: true, errorText: 'Mnemonic doesn\'t match this wallet'});
        return false;
      }

      unlockWallet(newWallet.address, newWallet.privateKey);
      history.push(`/wallet/${newWallet.address}`);

    } catch (e) {
      this.setState({ error: true, errorText: 'Invalid mnemonic'});
    }
  }

  render() {
    const { wallet } = this.props;

    return (
      <div className='ui container'>
        <h2 className="ui center aligned icon dividing header">
          {wallet.decrypted && <i className="circular lock open icon"></i>}
          {!wallet.decrypted && <i className="circular lock icon"></i>}
          Wallet recovery
          <div className="sub header">{wallet.address}</div>
        </h2>

        <div className='ui padded container'>
          <div className='ui message'>
            Recover wallet using 12 word mnemonic
          </div>

          <div className={`ui fluid action input ${this.state.error && 'error'}`}>
            <input type="text" placeholder="Your mnemonic here ..." value={this.state.mnemonic} onChange={(e) => this.setState({ mnemonic: e.target.value })} />
            <div className="ui button" onClick={this.checkMnemonic}>Check</div>
          </div>
          {this.state.error && (
            <div className="ui pointing red label">{this.state.errorText}</div>
          )}
        </div>
      </div>
    )
  }
}
