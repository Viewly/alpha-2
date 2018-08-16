import React, { Component} from "react";
import { connect } from "react-redux";
import { Link, withRouter } from 'react-router-dom';
import Item from '../home/item';
import { roundTwoDecimals, checkAddressValidity, isNumeric } from '../../../../utils';
import { sendEthereum, sendView, transactionWait, fetchBalance } from '../../../../actions';
import { STATUS_TYPE } from '../../../../constants';

@withRouter
@connect((state, props) => ({
  wallet: state.wallet.address === props.match.params.wallet && state.wallet,
  prices: state.prices,
  gasPrice: state.gasPrice,
  transaction: state.transaction,
}), (dispatch) => ({
  sendEthereum: ({ amount, address, privateKey, gasPrice }) => dispatch(sendEthereum({ amount, address, privateKey, gasPrice })),
  sendView: ({ amount, address, privateKey, gasPrice }) => dispatch(sendView({ amount, address, privateKey, gasPrice })),
  transactionWait: (txn_id) => dispatch(transactionWait({ txn_id })),
  fetchBalance: (address) => dispatch(fetchBalance({ address }))
}))
export default class WalletSingleWithdraw extends Component {
  state = {
    address: '',
    amount: '0',
    gasPrice: '',
    customGasPrice: false,
    loading: false,
    error: ''
  }

  componentDidMount () {
    const { gasPrice } = this.props;
    this.setState({ gasPrice: gasPrice.normal });
  }

  componentDidUpdate(prevProps) {
    const { transaction, gasPrice } = this.props;

    if (transaction.error !== prevProps.transaction.error) {
      this.setState({ error: transaction.error });
      this.setState({ loading: false });
    }

    if (gasPrice.normal !== prevProps.gasPrice.normal) {
      this.setState({ gasPrice: gasPrice.normal });
    }
  }

  sendConfirm = () => {
    const { match, wallet } = this.props;
    const { address, amount } = this.state;
    const type = match.params.type.toLowerCase();
    const balance = this.getCurrentBalance();
    const isAddressValid = checkAddressValidity(address) !== 'error';

    if (parseFloat(amount, 10) > parseFloat(balance, 10)) {
      this.setState({ error: 'Trying to send more than you have.' });
    } else if (!isAddressValid) {
      this.setState({ error: 'Please double check the address' });
    } else if (!this.state.gasPrice) {
      this.setState({ error: 'You must specify gas price' });
    } else {
      this.setState({ loading: true, error: '' });
      this.doWithdraw({ address, amount, type });
    }
  }

  doWithdraw = async ({ type, address, amount }) => {
    const { sendEthereum, sendView, history, wallet, transactionWait, fetchBalance } = this.props;
    let hash;

    try {
      switch (type.toUpperCase()) {
        case 'ETH': hash = await sendEthereum({ address, amount, privateKey: wallet.privateKey, gasPrice: this.state.gasPrice }); break;
        case 'VIEW': hash = await sendView({ address, amount, privateKey: wallet.privateKey, gasPrice: this.state.gasPrice }); break;
      }
    } catch (e) {
      this.setState({ loading: false, error: e.message });
      return false;
    }

    const txn = await transactionWait(hash);
    if (this.props.transaction.receipt && this.props.transaction.receipt.status === 0) {
      this.setState({ loading: false });
    } else {
      await fetchBalance(wallet.address);
      history.push(`/wallet/${wallet.address}`);
    }

  }

  getCurrentBalance = () => {
    const { match, wallet } = this.props;

    const type = match.params.type.toLowerCase();
    return (type === 'eth') ? wallet.balanceEth : wallet.balanceView;
  }

  toggleGasPrice = (e) => {
    const val = e.target.value;

    if (isNumeric(val)) {
      this.setState({ gasPrice: e.target.value, customGasPrice: false });
    } else {
      this.setState({ customGasPrice: true })
    }
  }

  displayCurrentItem = () => {
    const { match, wallet, prices } = this.props;

    const type = match.params.type.toLowerCase();
    const balance = this.getCurrentBalance();
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
    const { wallet, prices, transaction, gasPrice } = this.props;
    const { loading, error } = this.state;
    const balance = parseFloat(this.getCurrentBalance(), 10);
    const amount = parseFloat(this.state.amount, 10);

    const addressValidity = checkAddressValidity(this.state.address);
    const balanceValidity = ((balance >= amount) && (amount > 0));
    const canSend = ((addressValidity !== 'error') && balanceValidity);

    return (
      <div>
        <div className='ui divided items'>
          {this.displayCurrentItem()}
        </div>

        {error && (
          <div className="ui negative message">
            <div className="header">
              An error occurred
            </div>
            <p>{error}</p>
          </div>
        )}

        <div className={`ui form ${addressValidity === 'warning' ? 'warning' : ''}`}>
          {loading && (
            <div className="ui active dimmer">
              <div className="ui indeterminate text loader">Waiting for transaction confirmation</div>
            </div>
          )}

          <div className={`field ${!balanceValidity ? 'error' : ''}`}>
            <label>Amount</label>
            <input type="number" placeholder="0" value={this.state.amount} onChange={(e) => this.setState({ amount: e.target.value })} maxLength={100} />
          </div>

          <div className={`field ${addressValidity === 'error' ? 'error' : ''}`}>
            <label>Send to</label>
            <input type="text" placeholder="0x123abc..." value={this.state.address} onChange={(e) => this.setState({ address: e.target.value })} maxLength={100} />

            <div className="ui warning message">
              <div className="header">Double check the address!</div>
              <ul className="list">
                <li>While the address above might be correct, we have noticed its failing our checksum check</li>
                <li>That usually happens if you mix cases or if the entire address is lowercase</li>
                <li>Don't click Submit unless you are 100% sure the address is correct !</li>
              </ul>
            </div>
          </div>

          <div className='fields'>
            {!this.state.customGasPrice && (
              <div className='five wide field'>
                <label>Gas price</label>

                <select className="ui fluid dropdown" value={this.state.gasPrice} onChange={this.toggleGasPrice}>
                  <option value={gasPrice.normal}>Regular ({gasPrice.normal} gwei)</option>
                  <option value={gasPrice.fast}>Fast ({gasPrice.fast} gwei)</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
            )}

            {this.state.customGasPrice && (
              <div className='five wide field'>
                <label>Custom gas price (gwei)</label>
                <input type="number" value={this.state.gasPrice} onChange={(e) => this.setState({ gasPrice: e.target.value })} maxLength={100} />
              </div>
            )}

          </div>

          <button className={`ui button primary ${!canSend ? 'disabled' : ''}`} onClick={this.sendConfirm}>Submit</button>
          <Link to={`/wallet/${wallet.address}`} className="ui button">Cancel</Link>
        </div>
      </div>
    )
  }
}
