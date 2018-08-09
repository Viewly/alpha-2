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
      <div className='ui padded segment'>
        {this.state.generated && (
          <div>
            <div className="ui label">
              <i className="ethereum icon"></i> {this.state.wallet.address}
            </div>
            <div><br /></div>
          </div>
        )}


        <button className={`ui button ${!this.state.generated && 'primary' || 'grey basic'}`} onClick={this.generateNew}>Generate new</button>
        <button className={`ui button ${!this.state.generated && 'disabled' || 'primary'}`} onClick={this.saveWallet}>Next</button>
      </div>
    )
  }
}
