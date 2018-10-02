import React, { Component, Fragment } from "react";
import { connect } from "react-redux";
import { Link, withRouter } from 'react-router-dom';
import Item from '../home/item';
import { roundTwoDecimals, checkAddressValidity, isNumeric } from '../../../../utils';
import { sendEthereum, sendView, transactionWait, fetchBalance, transactionPendingAdd } from '../../../../actions';
import { STATUS_TYPE } from '../../../../constants';
import { CURRENCY } from '../../../../constants/currencies';

@withRouter
@connect((state, props) => ({
  wallet: state.wallet.address === props.match.params.wallet && state.wallet,
  prices: state.prices[state.currency],
  currency: state.currency,
  gasPrice: state.gasPrice,
  transaction: state.transaction,
  // TODO - quick workaround to lock withdraws if at least one transaction is pending
  isWithdrawLocked: state.pendingTransactions.length > 0,
  // isWithdrawLocked: state.pendingTransactions.filter(item =>
  //   item.context && item.context.type === 'withdraw' && item.context.value === props.match.params.type.toUpperCase()
  // ).length > 0
}), (dispatch) => ({
  sendEthereum: ({ amount, address, privateKey, gasPrice, gasLimit }) => dispatch(sendEthereum({ amount, address, privateKey, gasPrice, gasLimit })),
  sendView: ({ amount, address, privateKey, gasPrice, gasLimit }) => dispatch(sendView({ amount, address, privateKey, gasPrice, gasLimit })),
  transactionWait: (txn_id) => dispatch(transactionWait({ txn_id })),
  fetchBalance: (address) => dispatch(fetchBalance({ address })),
  transactionPendingAdd: (txn_id, context) => dispatch(transactionPendingAdd({ txn_id, type: context.type, value: context.value }))
}))
export default class WalletSingleWithdraw extends Component {
  state = {
    address: '',
    amount: '0',
    gasPrice: '',
    gasLimit: 0,
    customGasPrice: false,
    loading: false,
    error: ''
  }

  componentDidMount () {
    const { gasPrice, match } = this.props;
    const type = match.params.type.toLowerCase();

    this.setState({ gasPrice: gasPrice.normal, gasLimit: type === 'eth' ? 21000 : 60000 });
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
    const { sendEthereum, sendView, history, wallet: { privateKey, address: myAddress }, transactionWait, fetchBalance, transactionPendingAdd } = this.props;
    const { gasPrice, gasLimit } = this.state;
    const sendData = { address, amount, privateKey, gasPrice, gasLimit };

    let hash;
    try {
      switch (type.toUpperCase()) {
        case 'ETH': hash = await sendEthereum(sendData); break;
        case 'VIEW': hash = await sendView(sendData); break;
      }
    } catch (e) {
      this.setState({ loading: false, error: e.message });
      return false;
    }

    transactionPendingAdd(hash, { type: 'withdraw', value: type.toUpperCase() });

    const txn = await transactionWait(hash);
    if (this.props.transaction.receipt && this.props.transaction.receipt.status === 0) {
      this.setState({ loading: false });
    } else {
      await fetchBalance(myAddress);
      history.push(`/wallet/${myAddress}`);
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
    const { match, wallet, prices, currency } = this.props;

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
        fiat={roundTwoDecimals(euro)}
        fiatSign={CURRENCY[currency].sign}
        image={image}
        name={type.toUpperCase()}
      />
    )
  }

  render() {
    const { wallet, prices, transaction, gasPrice, isWithdrawLocked } = this.props;
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
          {(loading || isWithdrawLocked) && (
            <div className="ui active dimmer">
              <div className="ui indeterminate text loader">
                Waiting for transaction confirmation
                <br />
                <br />
                <Link to={`/wallet/${wallet.address}`} className='ui button tiny'>Back to wallet</Link>
              </div>
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

            {!this.state.customGasPrice && (
              <div className='fields'>
                <div className='five wide field'>
                  <label>Gas price</label>

                  <select ref={ref => this.selectRef = ref} className="ui fluid dropdown" value={this.state.gasPrice} onChange={this.toggleGasPrice}>
                    <option value={gasPrice.normal}>Regular ({gasPrice.normal} gwei)</option>
                    <option value={gasPrice.fast}>Fast ({gasPrice.fast} gwei)</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
              </div>
            )}

            {this.state.customGasPrice && (
              <Fragment>
                <div className='fields'>
                  <div className='five wide field'>
                    <label>Custom gas price (gwei)</label>
                    <input type="number" value={this.state.gasPrice} onChange={(e) => this.setState({ gasPrice: e.target.value })} maxLength={100} />
                  </div>
                </div>
                <div className='fields'>
                  <div className='five wide field'>
                    <label>Gas Limit</label>
                    <input type="number" value={this.state.gasLimit} onChange={(e) => this.setState({ gasLimit: e.target.value })} maxLength={100} />
                  </div>
                </div>
              </Fragment>
            )}


          <Link to={`/wallet/${wallet.address}`} className="ui button">Cancel</Link>
          <button className={`ui button c-btn--primary ${!canSend ? 'disabled' : ''}`} onClick={this.sendConfirm}>Submit</button>
        </div>
      </div>
    )
  }
}
