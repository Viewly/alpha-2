import React, { Component } from "react";
import { connect } from "react-redux";

import {
  unlockModalOpen,
  fetchBalance,
  fetchVideoPublisherData,
  authorizeAllowance,
  publishVideo,
  transactionWait,
  transactionBlockWait,
  transactionPendingAdd,
  fetchGasPrice
} from '../../actions';
import Portal from '../portal';
import { roundTwoDecimals } from '../../utils';
import { CURRENCY } from '../../constants/currencies';

const BLOCKS_TO_WAIT = 2;

@connect((state, props) => ({
  wallet: state.wallet,
  prices: state.prices[state.currency],
  currency: state.currency,
  gasPrice: state.gasPrice,
  videoPublisher: state.videoPublisher,
  transaction: state.transaction,
  hasPendingTransaction: state.pendingTransactions.length > 0,
}), (dispatch) => ({
  unlockModalOpen: () => dispatch(unlockModalOpen()),
  fetchBalance: (address) => dispatch(fetchBalance({ address })),
  fetchVideoPublisherData: ({ videoHex }) => dispatch(fetchVideoPublisherData({ videoHex })),
  transactionWait: (txn_id) => dispatch(transactionWait({ txn_id })),
  transactionBlockWait: (blockNumber, offset) => dispatch(transactionBlockWait({ blockNumber, offset })),
  authorizeAllowance: ({ address, privateKey, amount, gasPrice, gasLimit }) => dispatch(authorizeAllowance({ address, privateKey, amount, gasPrice, gasLimit })),
  publishVideo: ({ address, privateKey, videoHex, value, gasPrice, gasLimit }) => dispatch(publishVideo({ address, privateKey, videoHex, value, gasPrice, gasLimit })),
  transactionPendingAdd: (txn_id, context) => dispatch(transactionPendingAdd({ txn_id, type: context.type, value: context.value })),
  fetchGasPrice: () => dispatch(fetchGasPrice())
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
    const { fetchBalance, wallet, gasPrice, fetchGasPrice } = this.props;

    fetchGasPrice();
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

  publishClick = (type) => async () => {
    const { wallet,
      unlockModalOpen,
      videoPublisher,
      authorizeAllowance,
      publishVideo,
      transactionWait,
      transactionBlockWait,
      fetchBalance,
      transactionPendingAdd
    } = this.props;
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

        transactionPendingAdd(hash, { type: 'publish', value: videoHex });

        this.setState({ txnId: hash, txnPending: true });
        const { txn: { blockNumber } } = await transactionWait(hash);

        // TODO - leave this as debug for now in case someone has any issue
        console.log('transaction block number', blockNumber, 'waiting for', (blockNumber + BLOCKS_TO_WAIT), 'block to be mined');
        const latestBlock = await transactionBlockWait(blockNumber, BLOCKS_TO_WAIT);
        console.log('blockchain latest block', latestBlock);

        if (this.props.transaction.receipt && this.props.transaction.receipt.status === 0) {
          this.setState({ txnPending: false, errorText: 'Transaction wasnt successful' });
        } else {
          await Promise.all([
            fetchBalance(wallet.address),
            this.loadVideoContractData()
          ]);

          this.setState({ txnPending: false, txnId: '' });
        }
      } catch (e) {
        this.setState({ txnId: '', txnPending: false, errorText: e.message });
      }
    }
  }

  renderPublisher = () => {
    const { wallet, prices, videoPublisher, hasPendingTransaction, currency } = this.props;
    const { isPublished } = videoPublisher;

    const publishText = 'Publish the video';
    const sign = CURRENCY[currency].sign;

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
        <div className="ui icon message">
          <i className="notched circle loading icon"></i>
          <div className="content">
            <div className="header">
              {this.state.txnId ? `Waiting for transaction to confirm` : 'Sending transaction to blockchain'}
            </div>
            {this.state.txnId && <p>{this.state.txnId}</p>}
          </div>
        </div>
      );
    }

    if (hasPendingTransaction) {
      return (
        <div className="ui icon message">
          <i className="notched circle loading icon"></i>
          <div className="content">
            <div className="header">Transaction in progress</div>
            <p>Waiting for previous transaction to finish.</p>
          </div>
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
          data-tooltip={`${videoPublisher.priceView} VIEW ~ ${roundTwoDecimals(videoPublisher.priceView * prices.view)}${sign}`}
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
        data-tooltip={`${videoPublisher.priceEth} ETH ~ ${roundTwoDecimals(videoPublisher.priceEth * prices.eth)}${sign}`}
        data-position='right center'
        onClick={this.publishClick('publish_eth')}
        className='ui button large primary'
      >
        {publishText}
      </button>
    );
  }

  render() {
    const { videoPublisher, hasPendingTransaction } = this.props;
    const { isPublished } = videoPublisher;

    return (
      <Portal ref={(ref) => this.ref = ref} container='react-publish'>
        {this.state.errorText && (
          <div className='ui negative message'>
            <div className='header'>{this.state.errorText}</div>
          </div>
        )}

        {!this.state.customGasPrice && this.renderPublisher()}

        {!this.state.txnPending && !isPublished && !hasPendingTransaction && (
          <div className="ui message">
            {!this.state.customGasPrice && <p>Gas price for transaction will be {this.state.gasPrice} gwei (<a href='#' onClick={() => this.setState({ customGasPrice: true })}>edit</a>)</p>}
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
