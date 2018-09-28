import React, { Component} from "react";
import { connect } from "react-redux";
import { withRouter } from 'react-router-dom';

import { unlockModalOpen, lockWallet, toggleCurrency } from '../../../../actions';
import Item from './item';

import { roundTwoDecimals, updateWallets } from '../../../../utils';
import { CURRENCY } from '../../../../constants/currencies';

@withRouter
@connect((state, props) => ({
  wallet: state.wallet.address === props.match.params.wallet && state.wallet,
  prices: state.prices[state.currency],
  currency: state.currency
}), (dispatch) => ({
  unlockModalOpen: () => dispatch(unlockModalOpen()),
  lockWallet: (address) => dispatch(lockWallet(address)),
  toggleCurrency: () => dispatch(toggleCurrency()),
}))
export default class WalletSingleHome extends Component {
  state = {
    currencies: {
      EUR: {
        icon: 'euro sign',
        label: 'EUR'
      },
      USD: {
        icon: 'dollar sign',
        label: 'USD'
      }
    }
  }

  sendClick = (name) => {
    const { wallet, history, unlockModalOpen } = this.props;

    if (wallet.decrypted) {
      history.push(`/wallet/${wallet.address}/withdraw/${name}`);
    } else {
      unlockModalOpen();
    }
  }

  lockWallet = () => {
    const { wallet, lockWallet } = this.props;

    lockWallet(wallet.address);
    updateWallets({ address: wallet.address });
  }

  render() {
    const { wallet, prices, unlockModalOpen, currency, toggleCurrency } = this.props;

    return (
      <div>
        <div className="ui center aligned container">
          {wallet.decrypted && (
            <button onClick={this.lockWallet} className="ui right labeled icon button">
              <i className="right lock icon"></i>
              Lock wallet
            </button>
          )}

          {!wallet.decrypted && (
            <button onClick={unlockModalOpen} className="ui right labeled icon button">
              <i className="right lock open icon"></i>
              Unlock wallet
            </button>
          )}

          <button onClick={toggleCurrency} className="ui right labeled icon button">
            <i className={`right ${this.state.currencies[currency].icon} icon`}></i>
            Currency
          </button>
        </div>

        <div className='ui divided items'>

          <Item
            address={wallet.address}
            balance={wallet.balanceEth}
            decrypted={wallet.decrypted}
            fiat={roundTwoDecimals(wallet.balanceEth * prices.eth)}
            fiatSign={CURRENCY[currency].sign}
            image='https://s2.coinmarketcap.com/static/img/coins/128x128/1027.png'
            sendCallback={this.sendClick}
            name='ETH'
          />

          <Item
            address={wallet.address}
            balance={wallet.balanceView}
            decrypted={wallet.decrypted}
            fiat={roundTwoDecimals(wallet.balanceView * prices.view)}
            fiatSign={CURRENCY[currency].sign}
            image='https://s2.coinmarketcap.com/static/img/coins/128x128/2963.png'
            sendCallback={this.sendClick}
            name='VIEW'
            labels={['erc20']}
          />

        </div>
      </div>
    )
  }
}
