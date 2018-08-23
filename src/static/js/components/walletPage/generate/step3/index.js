import React, { Component} from "react";
import { Wallet } from 'ethers';
import Strength from './strength';

export default class GeneratorStep3 extends Component {
  state = {
    password: '',
    progress: 0,
    encrypting: false
  }

  encryptWallet = () => {
    const { wallet, changeStep } = this.props;

    if ((!this.state.password) || (this.state.password.length > 64)) {
      this.passwordInput.focus();
      this.passwordInput.parentElement.classList.add('error');
      return false;
    }

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
            <div className="ui grid middle aligned">

              <div className="eight wide column">
                <div className="field">
                  <label>Encryption password</label>
                  <input ref={(ref) => this.passwordInput = ref} type="password" placeholder="Password" value={this.state.password} onChange={(e) => this.setState({ password: e.target.value })} autoComplete="new-password" maxLength={64} />
                  <div className="ui pointing label">
                    If you forget this password, only way to recover is using mnemonic words
                  </div>
                </div>
              </div>

              <div className="eight wide column">
                {this.state.password && <Strength password={this.state.password} />}
              </div>

              <div className="eight wide column">
                <button className='ui button right labeled icon primary' onClick={this.encryptWallet}><i className="right lock icon"></i> Encrypt</button>
              </div>
            </div>

          </div>
        )}

        {this.state.encrypting && <h3 className='ui header'>Encrypting wallet: {Math.round(this.state.progress * 100)}%</h3>}
      </div>
    )
  }
}
