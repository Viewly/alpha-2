import React, { Component} from "react";
import { connect } from "react-redux";
import { Link } from 'react-router-dom';
import { providers, utils } from 'ethers';

@connect((state, props) => ({
  wallet: state.wallets[props.match.params.wallet]
}))
export default class WalletSingle extends Component {
  constructor (props) {
    super(props);

    this.state = {
      address: props.match.params.wallet,
      balance: 'Loading ...'
    }
  }

  async componentDidMount() {
    const network = providers.networks.kovan;
    const infuraProvider = new providers.InfuraProvider(network, "eb728907377046c1bc20b92a6fe13e19");

    window.infuraProvider = infuraProvider;
    const balance = await infuraProvider.getBalance(this.state.address);
    const etherString = utils.formatEther(balance);
    this.setState({ balance: etherString });
    console.log('balance', balance);
  }

  render() {

    return (
      <div>
        <Link to='/wallet'>Back</Link>
        <h2>Address: {this.state.address}</h2>
        <ul>
          <li>Balance: {this.state.balance} ETH</li>
        </ul>
      </div>
    )
  }
}
