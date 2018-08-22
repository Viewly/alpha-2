import React, { Component } from "react";
import { connect } from "react-redux";

import { STATUS_TYPE } from '../../constants';
import { videoVote, unlockModalOpen, fetchBalance } from '../../actions';
import Portal from '../portal';
import { saveVoteCache } from '../../utils';
require('./index.css');

const VOTE_TOKENS_NEEDED = 100;

@connect((state, props) => ({
  wallet: state.wallet,
  vote: state.votes[props.match.params.videoId]
}), (dispatch) => ({
  videoVote: (videoId) => dispatch(videoVote(videoId)),
  unlockModalOpen: () => dispatch(unlockModalOpen()),
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

  voteClick = async () => {
    const { wallet, unlockModalOpen, videoVote, match: { params: { videoId } } } = this.props;
    const { address, privateKey } = wallet;

    if (!wallet.decrypted) {
      unlockModalOpen();
    } else if (wallet.balanceView < VOTE_TOKENS_NEEDED) {
      this.modalOpen();
    } else {
      const response = await videoVote({ videoId, address, privateKey });

      if (response) {
        saveVoteCache(videoId);
        // window && window.refreshVotingStats && window.refreshVotingStats();
        // dirty hack to increment number of votes
        document
          && document.querySelector('.statistic .value')
          && document.querySelector('.statistic .value').innerHTML++;
      }
    }
  }

  showVoteButton = () => {
    const { vote, wallet } = this.props;

    if (wallet._status === STATUS_TYPE.LOADING) {
      return <a href='javascript:;' className="ui button c-btn--secondary right labeled icon viewly-icon">Loading wallet</a>;
    } else if (!wallet.address) {
      return <a href='/wallet' className="ui button c-btn--secondary right labeled icon viewly-icon">Vote</a>; // fake vote button - takes you to /wallet page
    }

    switch (vote) {
      case STATUS_TYPE.LOADING:
        return <a href='javascript:;' className="ui button c-btn--secondary right labeled icon viewly-icon">Voting ...</a>;
      case STATUS_TYPE.ERROR:
        return <a href='javascript:;' onClick={this.voteClick} className="ui button c-btn--secondary right labeled icon viewly-icon">Try again</a>;
      case true:
        return <a href='javascript:;' className="ui button c-btn--secondary disabled right labeled icon viewly-icon"><i className='check icon' />Voted</a>;
      default:
        return <a href='javascript:;' onClick={this.voteClick} className="ui button c-btn--secondary right labeled icon viewly-icon">Vote</a>;
    }
  }

  render() {
    return (
      <Portal container='react-vote'>
        {this.showVoteButton()}

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
