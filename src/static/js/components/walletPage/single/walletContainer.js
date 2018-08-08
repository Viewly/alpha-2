import React, { Component} from "react";
import { connect } from "react-redux";
import { withRouter } from 'react-router-dom';

import { fetchBalance } from '../../../actions';
import { getWalletByAddress } from '../../../utils';

@withRouter
@connect((state, props) => ({
  wallet: state.wallet.address === props.match.params.wallet && state.wallet
}), (dispatch) => ({
  fetchBalance: (address) => dispatch(fetchBalance({ address })),
}))
export default class WalletContainer extends Component {
  constructor (props) {
    super(props);

    const address = props.match.params.wallet;
    const localWallet = getWalletByAddress(address);

    this.state = {
      address: address,
    }
  }

  async componentDidMount() {
    const { fetchBalance } = this.props;

    fetchBalance(this.state.address);
  }

  render() {
    const { wallet, children } = this.props;

    if (!wallet) {
      return null;
    }

    return (
      <div>
        <h2 className="ui center aligned icon dividing header">
          {wallet.decrypted && <i className="circular lock open icon"></i>}
          {!wallet.decrypted && <i className="circular lock icon"></i>}
          Wallet
          <div className="sub header">{wallet.address}</div>
        </h2>

        {children}
      </div>
    )
  }
}
