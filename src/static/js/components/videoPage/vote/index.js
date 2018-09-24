import React, { Component } from "react";
import { connect } from "react-redux";

import Web3 from '../../web3';
import VoteMetamask from './metamask';
import VoteViewly from './viewly';

import { videoVote, fetchBalance } from '../../../actions';
import Portal from '../../portal';

const VOTE_TOKENS_NEEDED = 100;

@connect((state, props) => ({
  wallet: state.wallet,
  vote: state.votes[props.match.params.videoId]
}), (dispatch) => ({
  // videoVote: (videoId) => dispatch(videoVote(videoId)),
  fetchBalance: (address) => dispatch(fetchBalance({ address })),
}))
export default class VideoPage extends Component {
  componentDidMount () {
    const { fetchBalance, wallet } = this.props;

    wallet.status === 'loaded' && fetchBalance(wallet.address);

    this.modal = window.jQuery(this.ref).modal();
    this.modal.modal({ inverted: true });
  }

  componentDidUpdate(prevProps) {
    const { fetchBalance, wallet } = this.props;

    if (wallet.address !== prevProps.wallet.address) {
      fetchBalance(wallet.address);
    }
  }

  modalOpen = () => {
    this.modal.modal('show');
  }

  modalClose = () => {
    this.modal.modal('hide');
  }

  render() {
    const { wallet, vote, match: { params: { videoId } } } = this.props;

    return (
      <Portal container='react-vote'>
        <Web3 />

        <VoteMetamask wallet={wallet} vote={vote} videoId={videoId} onError={this.modalOpen} />
        <VoteViewly wallet={wallet} vote={vote} videoId={videoId} onError={this.modalOpen} />

        {/* {this.showVoteButton()} */}

        <div ref={(ref) => this.ref = ref} className='ui mini modal'>
          <div className='header'>Insufficient VIEW Tokens</div>
          <div className='content'>
            <p>Voting is free, however it does require at least {VOTE_TOKENS_NEEDED} VIEW Tokens in your
            Ethereum wallet <i>(for a minimum of 7 days)</i>.</p>
          </div>

          <div className="actions">
            <div className="ui button" onClick={() => this.modalClose()}>Cancel</div>
          </div>
        </div>

      </Portal>
    )
  }
}
