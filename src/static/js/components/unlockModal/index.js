import React, { Component} from "react";
import { Link } from "react-router-dom";
import { connect } from "react-redux";
import { providers, utils, Contract, Wallet } from 'ethers';

import Portal from '../portal';
import { unlockModalOpen, unlockModalClose, unlockWallet } from '../../actions';
import { updateWallets } from '../../utils';

@connect((state) => ({
  walletUnlockModal: state.walletUnlockModal,
  wallet: state.wallet
}), (dispatch) => ({
  unlockModalOpen: () => dispatch(unlockModalOpen()),
  unlockModalClose: () => dispatch(unlockModalClose()),
  unlockWallet: (address, privateKey) => dispatch(unlockWallet(address, privateKey))
}))
export default class UnlockModal extends Component {

  state = {
    password: '',
    unlockingPercent: 0,
    unlockingProgress: false,
    notification: ''
  }

  componentDidMount () {
    const { unlockModalOpen, unlockModalClose } = this.props;

    this.modal = window.jQuery(this.ref);
    this.modal.modal({
      inverted: true,
      // closable: false,
      onHide: () => {
        unlockModalClose();
      },
      onShow: () => {
        this.setState({ password: '' });
        unlockModalOpen();
      }
    });
  }

  getSnapshotBeforeUpdate(prevProps) {
    const { walletUnlockModal } = this.props;

    if (!prevProps.walletUnlockModal && walletUnlockModal) {
      this.modal.modal('show');
    } else if (prevProps.walletUnlockModal && !walletUnlockModal) {
      this.modal.modal('hide');
    }

    return null;
  }

  unlockWalletClick = async () => {
    const { wallet, unlockWallet, unlockModalClose } = this.props;

    this.setState({ notification: '', unlockingPercent: 0 });
    if (!this.state.password) {
      this.setState({ notification: 'Please enter wallet password !'});
      return false;
    }
    this.setState({ unlockingProgress: true });

    try {
      let lastPercent = 0;
      const decrypted = await Wallet.fromEncryptedWallet(JSON.stringify(wallet.encryptedWallet), this.state.password, (percent) => {
        this.setState({ unlockingPercent: Math.round(percent * 100) });
      });

      updateWallets(decrypted);
      this.setState({ unlockingProgress: false, password: '' });
      unlockWallet(wallet.address, decrypted.privateKey);
      unlockModalClose();
    } catch (e) {
      this.setState({ unlockingProgress: false, notification: 'Invalid wallet password' });
      this.passwordInput.focus();
    }
  }

  onKeyDown = (e) => {
    if (e.key === 'Enter') {
      this.unlockWalletClick();
    }
  }

  render() {
    const { wallet, unlockModalClose } = this.props;

    return (
      <Portal container='react-modal'>
        <div ref={(ref) => this.ref = ref} className='ui mini modal'>
          <div className='header'>
            Unlock wallet
          </div>
          <div className='content'>
            {this.state.notification && (
              <div className='ui warning message'>
                <p>{this.state.notification}</p>
              </div>
            )}

            {!this.state.unlockingProgress && (
              <div className='ui form'>
                <div className="field">
                  <label>Wallet password</label>
                  <input ref={(ref) => this.passwordInput = ref} type='password' value={this.state.password} onKeyDown={this.onKeyDown} onChange={(e) => this.setState({ password: e.target.value })} maxLength={64} />
                </div>
                <Link to={`/wallet/${wallet.address}/recover`} onClick={() => unlockModalClose()}>Forgot password?</Link>
              </div>
            )}

            {this.state.unlockingProgress && (
              <div className="ui progress">
                <div className="label">Unlocking your wallet {this.state.unlockingPercent}%</div>
              </div>
            )}
          </div>
          {!this.state.unlockingProgress && (
            <div className="actions">
              <div className="ui button" onClick={() => this.modal.modal('hide')}>Cancel</div>
              <div className="ui primary button" onClick={this.unlockWalletClick}>Unlock</div>
            </div>
          )}
        </div>
      </Portal>
    );
  }
}
