import React, { Component, Fragment } from "react";
import { connect } from "react-redux";
import { Link, Redirect } from 'react-router-dom';
import { STATUS_TYPE } from '../../../constants';

@connect((state) => ({
  wallet: state.wallet,
}))
export default class WalletHome extends Component {

  renderWalletHome = () => {
    const { wallet } = this.props;
    const isLoaded = wallet._status !== STATUS_TYPE.LOADING;

    if (isLoaded) {
      if (wallet.address) {
        return <Redirect to={`/wallet/${wallet.address}`} />;
      } else {
        return (
          <div className='ui padded segment'>
            <div className="ui message">
              <div className="header">
                view.ly wallet
              </div>

              <div className="ui list">
                <div className='item'>If you don't own a wallet, we can generate a new one.</div>
              </div>

              <Link to='/wallet/generate' className='ui button primary'>Generate new wallet</Link>
            </div>
          </div>
        );
      }
    } else {
      return <div>Loading ...</div>;
    }
  }

  render() {
    return this.renderWalletHome();
  }
}
