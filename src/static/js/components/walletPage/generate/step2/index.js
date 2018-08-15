import React, { Component} from "react";
import { Wallet } from 'ethers';
import { arrayShuffle } from '../../../../utils';

export default class GeneratorStep2 extends Component {
  state = {
    words: [1, 2, 3],
    input0: '',
    input1: '',
    input2: '',
    isOpen: false,
  }

  componentDidMount () {
    this.modal = window.jQuery(this.ref).modal();
    this.modal.modal({
      inverted: true,
      onHide: () => {
        this.setState({ isOpen: false });
      },
      onShow: () => {
        this.setState({ isOpen: true });
      }
    });
  }

  componentDidUpdate (prevProps, prevState) {
    const { wallet, changeStep } = this.props;
    const words = wallet.mnemonic.split(' ');

    if ( (this.state.input0 === words[this.state.words[0] - 1])
      && (this.state.input1 === words[this.state.words[1] - 1])
      && (this.state.input2 === words[this.state.words[2] - 1])) {

      this.modalClose();
      changeStep(3, wallet)
    }
  }

  modalOpen = () => {
    this.setState({ words: this.generateRandomNumbers() });
    this.modal.modal('show');
  }

  modalClose = () => {
    this.modal.modal('hide');
  }

  generateRandomNumbers = () => {
    return arrayShuffle([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]).splice(0, 3).sort(function(a,b) {return a - b});
  }

  render() {
    const { wallet } = this.props;
    const { isOpen } = this.state;
    const words = wallet.mnemonic.split(' ');

    return (
      <div className='ui padded segment'>

        <div ref={(ref) => this.ref = ref} className='ui mini modal'>
          <div className='header'>Confirm</div>
          <div className='content'>
            <div className='ui warning message'>
              <p>We need to make sure you have written mnemonic words!</p>
            </div>

            <div className='ui form'>
              {this.state.words.map((item, idx) => {
                return (
                  <div key={`form-items-${idx}-${item}`} className={`field ${this.state[`input${idx}`] === words[item - 1] ? 'disabled' : 'error'}`}>
                    <label>Word #{item}</label>
                    <input type='text' value={this.state[`input${idx}`]} onClick={() => this.className = 'lolz'} onChange={(e) => this.setState({ [`input${idx}`]: e.target.value })} disabled={ this.state[`input${idx}`] === words[item-1] } />
                  </div>
                );
              })}
            </div>
          </div>

          <div className="actions">
            <div className="ui button" onClick={() => this.modalClose()}>Cancel</div>
          </div>

        </div>

        <div className="ui negative message">
          <div className="header">
            Caution
          </div>
          <ul className="list">
            <li>Please write these words down and save them in a secure place</li>
            <li>Without these words you might permanently lose access to your wallet</li>
          </ul>
        </div>

        <ol style={{ columns: 2, columnGap: '60px' }}>
          {words.map((word, idx) => <li key={`word-${word}-${idx}`}><strong>{!isOpen ? word : '*'.repeat(word.length)}</strong></li>)}
        </ol>

        <button className='ui right labeled icon button primary' onClick={() => this.modalOpen()}><i className="right arrow icon"></i> Next</button>
      </div>
    )
  }
}
