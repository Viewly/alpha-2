import React, { Component} from "react";
import { connect } from "react-redux";
import { Link, withRouter } from 'react-router-dom';
import Item from '../home/item';
import { roundTwoDecimals } from '../../../../utils';
import { sendEthereum, sendView } from '../../../../actions';

@withRouter
@connect((state, props) => ({
  wallet: state.wallet.address === props.match.params.wallet && state.wallet,
  prices: state.prices
}), (dispatch) => ({
  sendEthereum: ({ amount, address, privateKey }) => dispatch(sendEthereum({ amount, address, privateKey })),
  sendView: ({ amount, address, privateKey }) => dispatch(sendView({ amount, address, privateKey }))
}))
export default class WalletSingleWithdraw extends Component {
  state = {
    address: '',
    amount: '0'
  }

  sendConfirm = () => {
    const { match } = this.props;
    const { address, amount } = this.state;

    const type = match.params.type.toLowerCase();

    this.doWithdraw({ address, amount, type });
  }

  doWithdraw = async ({ type, address, amount }) => {
    const { sendEthereum, sendView, history, wallet } = this.props;
    let hash;

    console.log('send', address, amount, wallet.privateKey, type);
    switch (type.toUpperCase()) {
      case 'ETH': hash = await sendEthereum({ address, amount, privateKey: wallet.privateKey }); break;
      case 'VIEW': hash = await sendView({ address, amount, privateKey: wallet.privateKey }); break;
    }

    console.log('DONE hash', hash);
    // this.setState({ notification: `Transaction successful! Hash: ${hash}`});
    history.push(`/wallet/${wallet.address}`);
  }

  displayCurrencyItem = () => {
    const { match, wallet, prices } = this.props;

    const type = match.params.type.toLowerCase();
    const balance = (type === 'eth') ? wallet.balanceEth : wallet.balanceView;
    const euro = (type === 'eth') ? (wallet.balanceEth * prices.eth) : (wallet.balanceView * prices.view);
    const image = (type === 'eth')
      ? 'https://s2.coinmarketcap.com/static/img/coins/128x128/1027.png'
      : 'https://s2.coinmarketcap.com/static/img/coins/128x128/2963.png';

    return (
      <Item
        address={wallet.address}
        balance={balance}
        decrypted={wallet.decrypted}
        euro={roundTwoDecimals(euro)}
        image={image}
        name={type.toUpperCase()}
      />
    )
  }

  render() {
    const { wallet, prices } = this.props;

    return (
      <div>
        <div className='ui divided items'>
          {this.displayCurrencyItem()}
        </div>

        <div className="ui form">
          <div className="field">
            <label>Amount</label>
            <input type="text" name="first-name" placeholder="0" value={this.state.amount} onChange={(e) => this.setState({ amount: e.target.value })} />
          </div>
          <div className="field">
            <label>Send to</label>
            <input type="text" name="last-name" placeholder="0x123abc..." value={this.state.address} onChange={(e) => this.setState({ address: e.target.value })} />
          </div>
          <button className="ui button primary" onClick={this.sendConfirm}>Submit</button>
          <Link to={`/wallet/${wallet.address}`} className="ui button">Cancel</Link>
        </div>
      </div>
    )
  }
}
