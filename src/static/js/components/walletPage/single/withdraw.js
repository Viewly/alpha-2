import React, { Component} from "react";
import { connect } from "react-redux";
import { Link } from 'react-router-dom';

export default class WalletWithdraw extends Component {
  state = {
    address: '',
    amount: '0'
  }

  sendConfirm = () => {
    const { type, doWithdraw } = this.props;

    doWithdraw({ toAddress: this.state.address, amount: this.state.amount, type });
  }

  render() {
    const { address, type } = this.props;

    return (
      <div>
        Amount: <input type="text" value={this.state.amount} onChange={(e) => this.setState({ amount: e.target.value })} /> {type}
        <br />
        Send to: <input type="text" value={this.state.address} onChange={(e) => this.setState({ address: e.target.value })} placeholder="0x0000 ..." />
        <br />
        <button onClick={this.sendConfirm}>Send</button>
        <Link to={`/wallet/${address}`}>Cancel</Link>
      </div>
    )
  }
}
