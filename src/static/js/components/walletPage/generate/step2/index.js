import React, { Component} from "react";
import { Wallet } from 'ethers';

export default class GeneratorStep2 extends Component {
  render() {
    const { wallet, changeStep } = this.props;
    const words = wallet.mnemonic.split(' ');

    return (
      <div className='ui padded segment'>

        <div className="ui negative message">
          <div className="header">
            Caution
          </div>
          <ul className="list">
            <li>Please write these words down and save them in a secure place</li>
            <li>Without these words you might permanently lose access to your wallet</li>
          </ul>
        </div>

        <ol>
          {words.map((word, idx) => <li key={`word-${word}-${idx}`}><strong>{word}</strong></li>)}
        </ol>

        <button className='ui right labeled icon button primary' onClick={() => changeStep(3, wallet)}><i class="right arrow icon"></i> Next</button>
      </div>
    )
  }
}
