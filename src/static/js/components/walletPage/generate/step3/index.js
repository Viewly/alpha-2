import React, { Component} from "react";
import { Wallet } from 'ethers';

export default class GeneratorStep3 extends Component {
  state = {
    password: '',
    progress: 0,
    encrypting: false
  }

  encryptWallet = () => {
    const { wallet, changeStep } = this.props;

    this.setState({ encrypting: true });

    var encryptPromise = wallet.encrypt(this.state.password, (progress) => {
      this.setState({ progress });
    });

    encryptPromise.then((json) => {
      changeStep(4, { ...wallet, encrypted: json });
    });
  }

  render() {
    const { wallet } = this.props;

    return (
      <div className='ui padded segment'>

        {!this.state.encrypting && (
          <div className="ui form">
            <div className="twelve wide field">
              <label>Encryption password</label>
              <input type="password" placeholder="Password" value={this.state.password} onChange={(e) => this.setState({ password: e.target.value })} />
              <div className="ui pointing label">
                If you forget this password, only way to recover is using mnemonic words
              </div>
            </div>

            <button className='ui button primary' onClick={this.encryptWallet}>Encrypt</button>
          </div>
        )}

        {this.state.encrypting && <h3 className='ui header'>Encrypting wallet: {Math.round(this.state.progress * 100)}%</h3>}
      </div>
    )
  }
}
