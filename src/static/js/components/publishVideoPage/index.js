import React, { Component } from "react";
import { connect } from "react-redux";

import { unlockModalOpen, fetchBalance } from '../../actions';
import Portal from '../portal';

import provider, { CONTRACT_VIDEO_PUBLISHER, contract, videoContract, contractSigned, videoContractSigned } from '../../ethereum'; // TODO - move to api
import { utils, Wallet } from 'ethers'; // TODO - move to api
import { roundTwoDecimals } from '../../utils';

@connect((state, props) => ({
  wallet: state.wallet,
  prices: state.prices
}), (dispatch) => ({
  unlockModalOpen: () => dispatch(unlockModalOpen()),
  fetchBalance: (address) => dispatch(fetchBalance({ address })),
}))
export default class PublishVideoPage extends Component {
  state = {
    priceEth: -1,
    priceEthBn: -1,
    priceView: -1,
    priceViewBn: -1,
    isPublished: false,
    txnPending: false,
    txnId: ''
  }

  componentDidMount() {
    const { fetchBalance, wallet } = this.props;

    this.loadVideoContractData();
    wallet.status === 'loaded' && fetchBalance(wallet.address);
  }

  componentDidUpdate(prevProps) {
    const { fetchBalance, wallet } = this.props;

    if (wallet.address !== prevProps.wallet.address) {
      fetchBalance(wallet.address);
    }
  }

  loadVideoContractData = async () => {
    const { videoHex } = this.ref.container.dataset;

    const priceView = await videoContract.priceView();
    const priceEth = await videoContract.priceEth();
    const isPublished = await videoContract.videos(videoHex) !== '0x0000000000000000000000000000000000000000';

    this.setState({
      priceView: utils.formatEther(priceView),
      priceViewBn: priceView,
      priceEth: utils.formatEther(priceEth),
      priceEthBn: priceEth,
      isPublished
    })
  }

  reloadTxn = async (txn_id) => {
    const { wallet, fetchBalance } = this.props;

    let txn;
    let refreshInterval = setInterval(async () => {
      txn = await provider.getTransaction(txn_id);

      if (txn && txn.blockHash) {
        clearInterval(refreshInterval);
        fetchBalance(wallet.address);
        this.loadVideoContractData();

        setTimeout(() => {
          // fake the loader, leave it one more second to fetch balances
          this.setState({ txnPending: false, txnId: '' });
        }, 1000);
      }
    }, 1000);
  }

  publishClick = (type) => async () => {
    const { wallet, unlockModalOpen } = this.props;
    const { videoHex } = this.ref.container.dataset;

    if (!wallet.decrypted) {
      unlockModalOpen();
    } else {
      const tmpWallet = new Wallet(wallet.privateKey, provider);

      let transaction;

      this.setState({ txnPending: true });
      try {
        if (type === 'authorize') {
          const authorizedContract = contractSigned(tmpWallet);
          const multiplied = this.state.priceViewBn.mul(100); // multiply price by 100

          transaction = await authorizedContract.approve(CONTRACT_VIDEO_PUBLISHER, multiplied);
        } else if (type === 'publish') {
          const authorizedVideoContract = videoContractSigned(tmpWallet);

          transaction = await authorizedVideoContract.publish(videoHex, { value: 0 });
        } else if (type === 'publish_eth') {
          const authorizedVideoContract = videoContractSigned(tmpWallet);

          transaction = await authorizedVideoContract.publish(videoHex, { value: this.state.priceEthBn });
        }

        this.setState({ txnId: transaction.hash, txnPending: true });
        this.reloadTxn(transaction.hash);
      } catch (e) {
        this.setState({ txnId: '', txnPending: false });
      }
    }
  }

  renderPublisher = () => {
    const { wallet, prices } = this.props;
    const { isPublished } = this.state;

    const publishText = 'Publish the video';

    if ((wallet._status === 'LOADING') || (this.state.priceView === -1)) {
      return <button className='ui button large primary disabled'>Loading ...</button>;
    }

    if (isPublished) {
      return <div>Video has been published, and will be live in a few minutes. <i className="checkmark icon green"></i></div>
    }

    if (this.state.txnPending) {
      return (
        <div>
          <div className="ui active inline loader"></div>
          {this.state.txnId ? `Waiting for transaction to confirm - ${this.state.txnId}` : 'Sending transaction to blockchain'}
        </div>
      );
    }

    if (wallet.balanceView >= this.state.priceView) {
      if (wallet.allowance < this.state.priceView) {
        return (
          <button
            data-tooltip="Authorize VideoPublisher's allowance for 100 videos at current price"
            data-position='right center'
            onClick={this.publishClick('authorize')}
            className='ui button large primary'
          >
            Authorize VideoPublisher
          </button>
        );
      }

      return (
        <button
          data-tooltip={`${this.state.priceView} VIEW ~ ${roundTwoDecimals(this.state.priceView * prices.view)}€`}
          data-position='right center'
          onClick={this.publishClick('publish')}
          className='ui button large primary'
        >
          {publishText}
        </button>
      )
    }

    return (
      <button
        data-tooltip={`${this.state.priceEth} ETH ~ ${roundTwoDecimals(this.state.priceEth * prices.eth)}€`}
        data-position='right center'
        onClick={this.publishClick('publish_eth')}
        className='ui button large primary'
      >
        {publishText}
      </button>
    );
  }

  render() {
    console.log('render state', this.state);

    return (
      <Portal ref={(ref) => this.ref = ref} container='react-publish'>
        {this.renderPublisher()}
      </Portal>
    )
  }
}
