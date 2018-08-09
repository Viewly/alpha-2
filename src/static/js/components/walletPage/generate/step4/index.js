import React, { Component} from "react";
import { Wallet } from 'ethers';
import { connect } from "react-redux";
import { walletSave } from '../../../../actions';
import { updateWallets } from '../../../../utils';

@connect(null, (dispatch) => ({
  walletSave: wallet => dispatch(walletSave(wallet))
}))
export default class GeneratorStep4 extends Component {
  state = {
    showPrivate: false
  }

  finishGeneration = async () => {
    const { wallet, changeStep, walletSave } = this.props;
    const storage = { address: wallet.address, privateKey: wallet.privateKey };

    updateWallets(storage);
    await walletSave({ data: wallet.encrypted });
    changeStep(0);
  }

  render() {
    const { wallet } = this.props;

    return (
      <div className='ui padded segment'>
        <div className="ui positive message">
          <div className="header">
            Wallet generation is complete.
          </div>
          <p>Last step is to save wallet so you can start using it.</p>
          <p>Clicking on <b>Finish</b> button will save encrypted wallet on our website (we won't have access to your wallet).</p>
        </div>

        <div className='ui form'>
          <div className="twelve wide field">
            <label>Your address</label>
            <input type="text" value={wallet.address} readOnly />
          </div>

          <div className='twelve wide field'>
            <label>Private key</label>

            <div className="ui action input small">
              <input type={this.state.showPrivate ? 'text' : 'password'} value={wallet.privateKey} size={60} readOnly  />

              <button className="ui icon button" onClick={() => this.setState({ showPrivate: !this.state.showPrivate })}>
                <i className="eye icon"></i>
              </button>
            </div>
          </div>

          <div className="field">
            <label>Encrypted data</label>
            <textarea value={wallet.encrypted} rows={8} readOnly></textarea>

            <div className="ui pointing label">
              This is the only data that will be sent to our server
            </div>
          </div>

          <button className='ui button primary' onClick={this.finishGeneration}>Finish</button>
        </div>

      </div>
    )
  }
}
