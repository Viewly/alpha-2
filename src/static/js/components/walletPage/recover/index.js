import React, { Component} from "react";
import { connect } from "react-redux";
import { Wallet } from 'ethers';

import Strength from '../generate/step3/strength';
import { unlockWallet, walletUpdate } from '../../../actions';
import { updateWallets } from '../../../utils';

@connect((state, props) => ({
  wallet: state.wallet.address === props.match.params.wallet && state.wallet,
}), (dispatch) => ({
  unlockWallet: (address, privateKey) => dispatch(unlockWallet(address, privateKey)),
  walletUpdate: (wallet) => dispatch(walletUpdate(wallet)),
}))
export default class WalletRecover extends Component {
  state = {
    mnemonic: '',
    password: '',
    progress: 0,
    encrypting: false,
    error: false,
    errorText: ''
  }

  checkMnemonic = () => {
    const { wallet, unlockWallet } = this.props;

    this.setState({ error: false });
    try {
      const newWallet = Wallet.fromMnemonic(this.state.mnemonic);

      if (newWallet.address !== wallet.address) {
        this.setState({ error: true, errorText: 'Mnemonic doesn\'t match this wallet'});
        return false;
      }

      updateWallets(newWallet);
      unlockWallet(newWallet.address, newWallet.privateKey);
    } catch (e) {
      this.setState({ error: true, errorText: 'Invalid mnemonic'});
    }
  }

  signMessage = () => {
    const { wallet } = this.props;

    const message = "Viewly Wallet Recovery";
    const tmpWallet = new Wallet(wallet.privateKey);
    const signature = tmpWallet.signMessage(message);

    return JSON.stringify({
      "address": wallet.address,
      "msg": message,
      "sig": signature,
      "version": "2"
    })
  }

  encryptAndSave = () => {
    const { wallet, walletUpdate, history } = this.props;

    const tmpWallet = new Wallet(wallet.privateKey);

    this.setState({ error: false });
    if ((!this.state.password) || (this.state.password.length > 64)) {
      this.setState({ error: true });
      return false;
    }

    this.setState({ encrypting: true });

    var encryptPromise = tmpWallet.encrypt(this.state.password, (progress) => {
      this.setState({ progress });
    });

    encryptPromise.then(async (json) => {
      const payload = {
        data: json,
        signature: this.signMessage()
      };

      await walletUpdate(payload);
      history.push(`/wallet/${wallet.address}`);
    });
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

        {!wallet.decrypted && (
          <div className='ui padded container'>
            <div className='ui message'>
              Recover wallet using 12 word mnemonic
            </div>

            <div className={`ui fluid action input ${this.state.error && 'error'}`}>
              <input type="text" placeholder="Your mnemonic here ..." value={this.state.mnemonic} onChange={(e) => this.setState({ mnemonic: e.target.value })} />
              <div className="ui button" onClick={this.checkMnemonic}>Unlock</div>
            </div>
            {this.state.error && (
              <div className="ui pointing red label">{this.state.errorText}</div>
            )}
          </div>
        )}
        {wallet.decrypted && (
          <div className='ui padded container'>
            <div className='ui positive message'>
              Wallet successfully unlocked !<br />
              You can change password now using the input below.
            </div>

            {this.state.encrypting && <h3 className='ui header'>Encrypting wallet: {Math.round(this.state.progress * 100)}%</h3>}
            {!this.state.encrypting && (
              <div>
                <div className="ui fluid action input">
                  <input type="password" placeholder="New password" value={this.state.password} onChange={(e) => this.setState({ password: e.target.value })} />
                  <div className="ui button" onClick={this.encryptAndSave}>Save password</div>
                </div>
                <div className="eight wide column">
                  {this.state.password && <Strength password={this.state.password} />}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    )
  }
}
