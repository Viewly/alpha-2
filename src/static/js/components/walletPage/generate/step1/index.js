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

        <div>
          <div className="ui label">
            <i className="ethereum icon"></i>
            {this.state.generated ? this.state.wallet.address : 'Click on a button below to generate a new wallet' }
          </div>
          <div><br /></div>
        </div>

        <button className={`ui button right labeled icon ${!this.state.generated && 'primary' || 'primary basic'}`} onClick={this.generateNew}><i className="right sync icon"></i> Generate new</button>
        <button className={`ui button right labeled icon ${!this.state.generated && 'disabled' || 'primary'}`} onClick={this.saveWallet}><i className="right arrow icon"></i> Next</button>
      </div>
    )
  }
}
