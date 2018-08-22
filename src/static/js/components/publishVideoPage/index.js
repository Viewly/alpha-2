import React, { Component } from "react";
import { connect } from "react-redux";

import {
  unlockModalOpen,
  fetchBalance,
  fetchVideoPublisherData,
  authorizeAllowance,
  publishVideo
} from '../../actions';
import Portal from '../portal';

import provider from '../../ethereum'; // TODO - move to api
import { roundTwoDecimals } from '../../utils';

@connect((state, props) => ({
  wallet: state.wallet,
  prices: state.prices,
  gasPrice: state.gasPrice,
  videoPublisher: state.videoPublisher
}), (dispatch) => ({
  unlockModalOpen: () => dispatch(unlockModalOpen()),
  fetchBalance: (address) => dispatch(fetchBalance({ address })),
  fetchVideoPublisherData: ({ videoHex }) => dispatch(fetchVideoPublisherData({ videoHex })),
  authorizeAllowance: ({ address, privateKey, amount, gasPrice, gasLimit }) => dispatch(authorizeAllowance({ address, privateKey, amount, gasPrice, gasLimit })),
  publishVideo: ({ address, privateKey, videoHex, value, gasPrice, gasLimit }) => dispatch(publishVideo({ address, privateKey, videoHex, value, gasPrice, gasLimit })),
}))
export default class PublishVideoPage extends Component {
  state = {
    txnPending: false,
    txnId: '',
    errorText: '',
    gasPrice: '',
    gasLimit: 0,
    customGasPrice: false
  }

  componentDidMount() {
    const { fetchBalance, wallet, gasPrice } = this.props;

    this.loadVideoContractData();
    this.setState({ gasPrice: gasPrice.normal, gasLimit: 100000 });
    wallet.status === 'loaded' && fetchBalance(wallet.address);
  }

  componentDidUpdate(prevProps) {
    const { fetchBalance, wallet, gasPrice } = this.props;

    if (wallet.address !== prevProps.wallet.address) {
      fetchBalance(wallet.address);
    }

    if (gasPrice.normal !== prevProps.gasPrice.normal) {
      this.setState({ gasPrice: gasPrice.normal });
    }
  }

  loadVideoContractData = async () => {
    const { videoHex } = this.ref.container.dataset;
    const { fetchVideoPublisherData } = this.props;

    await fetchVideoPublisherData({ videoHex });
  }

  waitForTxn = async (txn_id) => {
    const { wallet, fetchBalance } = this.props;

    const wait = await new Promise(resolve => {
      const refreshInterval = setInterval(async () => {
        const txn = await provider.getTransaction(txn_id);

        if (txn && txn.blockHash) {
          clearInterval(refreshInterval);
          resolve();
        }
      }, 1000);
    });

    await Promise.all([
      fetchBalance(wallet.address),
      this.loadVideoContractData()
    ]);

    this.setState({ txnPending: false, txnId: '' });
  }

  publishClick = (type) => async () => {
    const { wallet, unlockModalOpen, videoPublisher, authorizeAllowance, publishVideo } = this.props;
    const { address, privateKey } = wallet;
    const { videoHex } = this.ref.container.dataset;
    const { gasPrice, gasLimit } = this.state;

    if (!wallet.decrypted) {
      unlockModalOpen();
    } else {
      let hash;

      this.setState({ txnPending: true, errorText: '' });

      try {
        if (type === 'authorize') {
          const amount = videoPublisher.priceViewBn.mul(100); // multiply price by 100
          hash = await authorizeAllowance({ amount, address, privateKey, gasPrice, gasLimit });
        } else if ((type === 'publish') || (type === 'publish_eth')) {
          hash = await publishVideo({ videoHex, address, privateKey, value: type === 'publish' ? 0 : videoPublisher.priceEthBn, gasPrice, gasLimit });
        } else {
          throw new Error('Invalid type: ' + type);
        }

        this.setState({ txnId: hash, txnPending: true });
        this.waitForTxn(hash);
      } catch (e) {
        this.setState({ txnId: '', txnPending: false, errorText: e.message });
      }
    }
  }

  renderPublisher = () => {
    const { wallet, prices, videoPublisher } = this.props;
    const { isPublished } = videoPublisher;

    const publishText = 'Publish the video';

    if ((wallet._status === 'LOADING') || (videoPublisher.priceView === -1)) {
      return <button className='ui button large primary disabled'>Loading ...</button>;
    }

    if (!wallet.address) {
      return <a href='/wallet' className="ui button primary">{publishText}</a>;
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

    if (wallet.balanceView >= videoPublisher.priceView) {
      if (wallet.allowance < videoPublisher.priceView) {
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
          data-tooltip={`${videoPublisher.priceView} VIEW ~ ${roundTwoDecimals(videoPublisher.priceView * prices.view)}€`}
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
        data-tooltip={`${videoPublisher.priceEth} ETH ~ ${roundTwoDecimals(videoPublisher.priceEth * prices.eth)}€`}
        data-position='right center'
        onClick={this.publishClick('publish_eth')}
        className='ui button large primary'
      >
        {publishText}
      </button>
    );
  }

  render() {
    return (
      <Portal ref={(ref) => this.ref = ref} container='react-publish'>
        {this.state.errorText && (
          <div className='ui negative message'>
            <div className='header'>{this.state.errorText}</div>
          </div>
        )}

        {!this.state.customGasPrice && this.renderPublisher()}

        {!this.state.txnPending && (
          <div className="ui message">
            {!this.state.customGasPrice && <p>Gas price for transaction will be {this.state.gasPrice} gwei, if want to customize it <a href='#' onClick={() => this.setState({ customGasPrice: true })}>click here</a></p>}
            {this.state.customGasPrice && (
              <div className='ui form'>
                <div className='fields'>
                  <div className='five wide field'>
                    <label>Gas price (gwei)</label>
                    <input type="number" value={this.state.gasPrice} onChange={(e) => this.setState({ gasPrice: e.target.value })} maxLength={100} />
                  </div>
                </div>
                <div className='fields'>
                  <div className='five wide field'>
                    <label>Gas Limit</label>
                    <input type="number" value={this.state.gasLimit} onChange={(e) => this.setState({ gasLimit: e.target.value })} maxLength={100} />
                  </div>
                </div>
                <button className='ui button primary' onClick={() => this.setState({ customGasPrice: false })}>Save</button>
              </div>
            )}
          </div>
        )}
      </Portal>
    )
  }
}
