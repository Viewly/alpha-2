import React, { Component} from "react";
import { connect } from "react-redux";
import { Link } from 'react-router-dom';
import { Route } from 'react-router-dom';
import { providers, utils, Contract, Wallet } from 'ethers';
import WalletWithdraw from './withdraw';
import abi from '../../../abi.json';

import { getWalletByAddress, updateWallets } from '../../../utils';

@connect((state, props) => ({
  wallet: state.wallets[props.match.params.wallet]
}))
export default class WalletSingle extends Component {
  constructor (props) {
    super(props);

    const address = props.match.params.wallet;
    const localWallet = getWalletByAddress(address);
console.log('haz lokal', localWallet);

    this.state = {
      address: address,
      unlocked: (localWallet && localWallet.decrypted) ? true : false,
      privateKey: (localWallet && localWallet.decrypted) ? localWallet.privateKey : '',
      unlockingPercent: 0,
      unlockingProgress: false,
      balance: 'Loading ...',
      balanceToken: 'Loading ...',
      notification: '',
    }
  }

  async componentDidMount() {
    const network = providers.networks.kovan;
    this.provider = new providers.InfuraProvider(network, "eb728907377046c1bc20b92a6fe13e19");

    const contractAddress = '0xfbce7c17608ebd5640313ecf4d2ff09b6726bab9';
    const contract = new Contract(contractAddress, abi, this.provider);

    const etherBN = await this.provider.getBalance(this.state.address);
    const viewBN = await contract.balanceOf(this.state.address);

    this.setState({
      balance: utils.formatEther(etherBN),
      balanceToken: utils.formatEther(viewBN)
    });
  }

  doWithdraw = async (sendData) => {
    const { history } = this.props;

    const wallet = new Wallet(this.state.privateKey);
    wallet.provider = this.provider;

    const amount = utils.parseEther(sendData.amount);
    const { hash } = await wallet.send(sendData.toAddress, amount);

    this.setState({ notification: `Transaction successful! Hash: ${hash}`});
    history.push(`/wallet/${this.state.address}`);
  }

  unlockWallet = async () => {
    const { wallet } = this.props;
    const password = prompt("Please enter password to unlock");
    if (!password) {
      return;
    }

    this.setState({ unlockingProgress: true });

    try {
      const decrypted = await Wallet.fromEncryptedWallet(JSON.stringify(wallet.encryptedWallet), password, (percent) => {
        this.setState({ unlockingPercent: Math.round(percent * 100) });
      });

      updateWallets(decrypted);
      this.setState({ unlockingProgress: false, privateKey: decrypted.privateKey, unlocked: true });
    } catch (e) {
      this.setState({ unlockingProgress: false });
      alert('Invalid wallet password');
    }
  }

  render() {

    return (
      <div>
        <Link to='/wallet'>Back</Link>
        <h2>Address: {this.state.address}</h2>

        {!this.state.unlocked && <span style={{color:'red'}}>WALLET LOCKED</span>}
        {this.state.notification && <div><strong>{this.state.notification}</strong></div>}

        <ul>
          <li>
            Balance: {this.state.balance} ETH
            {this.state.unlocked && <Link to={`/wallet/${this.state.address}/withdraw/eth`}>(withdraw)</Link>}
          </li>
          <Route exact path='/wallet/:wallet/withdraw/eth' render={() => <WalletWithdraw doWithdraw={this.doWithdraw} type='ETH' address={this.state.address} />} />

          <li>
            Balance: {this.state.balanceToken} VIEW
            {this.state.unlocked && <Link to={`/wallet/${this.state.address}/withdraw/view`}>(withdraw)</Link>}
          </li>
          <Route exact path='/wallet/:wallet/withdraw/view' render={() => <WalletWithdraw doWithdraw={this.doWithdraw} type='VIEW' address={this.state.address} />} />
        </ul>

        {!this.state.unlocked && (
          <div>
            {this.state.unlockingProgress && <button>Unlocking {this.state.unlockingPercent}%</button>}
            {!this.state.unlockingProgress && <button onClick={this.unlockWallet}>CLICK TO UNLOCK WALLET</button>}
          </div>
        )}

      </div>
    )
  }
}
