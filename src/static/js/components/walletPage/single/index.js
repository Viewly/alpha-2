import React, { Component} from "react";
import { connect } from "react-redux";
import { Link } from 'react-router-dom';
import { Route } from 'react-router-dom';
import { providers, utils, Contract, Wallet } from 'ethers';

import WalletWithdraw from './withdraw';
import abi from '../../../abi.json';
import { lockWallet, fetchBalance, sendEthereum, sendView, unlockModalOpen } from '../../../actions';
import { getWalletByAddress, updateWallets, roundTwoDecimals } from '../../../utils';

@connect((state, props) => ({
  wallet: state.wallet.address === props.match.params.wallet && state.wallet,
  prices: state.prices
}), (dispatch) => ({
  lockWallet: (address) => dispatch(lockWallet(address)),
  unlockModalOpen: () => dispatch(unlockModalOpen()),
  fetchBalance: (address) => dispatch(fetchBalance({ address })),
  sendEthereum: ({ amount, address, privateKey }) => dispatch(sendEthereum({ amount, address, privateKey })),
  sendView: ({ amount, address, privateKey }) => dispatch(sendView({ amount, address, privateKey }))
}))
export default class WalletSingle extends Component {
  constructor (props) {
    super(props);

    const address = props.match.params.wallet;
    const localWallet = getWalletByAddress(address);

    this.state = {
      address: address,
      notification: '',
    }
  }

  async componentDidMount() {
    const { fetchBalance } = this.props;

    fetchBalance(this.state.address);
  }

  doWithdraw = async ({ type, address, amount }) => {
    const { sendEthereum, sendView, history, wallet: { privateKey } } = this.props;
    let hash;

    switch (type) {
      case 'ETH': hash = await sendEthereum({ address, amount, privateKey }); break;
      case 'VIEW': hash = await sendView({ address, amount, privateKey }); break;
    }

    this.setState({ notification: `Transaction successful! Hash: ${hash}`});
    history.push(`/wallet/${this.state.address}`);
  }

  lockWallet = () => {
    const { lockWallet } = this.props;

    lockWallet(this.state.address);
    updateWallets({ address: this.state.address });
  }

  render() {
    const { wallet, prices, unlockModalOpen } = this.props;

    if (!wallet) {
      return null;
    }

    return (
      <div>
        <h2>Address: {this.state.address}</h2>

        {!wallet.decrypted && <span style={{color:'red'}}>WALLET LOCKED</span>}
        {this.state.notification && <div><strong>{this.state.notification}</strong></div>}

        <ul>
          <li>
            Balance: {wallet.balanceEth} ETH
            {wallet.decrypted && <Link to={`/wallet/${this.state.address}/withdraw/eth`}>(withdraw)</Link>}
            <br />
            ({roundTwoDecimals(wallet.balanceEth * prices.eth)} &euro;)
          </li>
          <Route exact path='/wallet/:wallet/withdraw/eth' render={() => <WalletWithdraw doWithdraw={this.doWithdraw} type='ETH' address={this.state.address} />} />

          <li>
            Balance: {wallet.balanceView} VIEW
            {wallet.decrypted && <Link to={`/wallet/${this.state.address}/withdraw/view`}>(withdraw)</Link>}
            <br />
            ({roundTwoDecimals(wallet.balanceView * prices.view)} &euro;)
          </li>
          <Route exact path='/wallet/:wallet/withdraw/view' render={() => <WalletWithdraw doWithdraw={this.doWithdraw} type='VIEW' address={this.state.address} />} />
        </ul>

        {!wallet.decrypted && (
          <button onClick={unlockModalOpen}>CLICK TO UNLOCK WALLET</button>
        )}
        {wallet.decrypted && (
          <button onClick={this.lockWallet}>LOCK WALLET</button>
        )}

      </div>
    )
  }
}
