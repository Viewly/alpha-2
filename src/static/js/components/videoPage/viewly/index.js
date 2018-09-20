import React, { Component } from "react";
import { connect } from "react-redux";

import { STATUS_TYPE } from '../../../constants';
import { videoVote, unlockModalOpen } from '../../../actions';
import { saveVoteCache } from '../../../utils';
require('../index.css');

const VOTE_TOKENS_NEEDED = 100;

@connect(null, (dispatch) => ({
  videoVote: (videoId) => dispatch(videoVote(videoId)),
  unlockModalOpen: () => dispatch(unlockModalOpen()),
}))
export default class VoteViewly extends Component {
  voteClick = async () => {
    const { wallet, unlockModalOpen, videoVote, videoId } = this.props;
    const { address, privateKey } = wallet;

    if (!wallet.decrypted) {
      unlockModalOpen();
    } else if (wallet.balanceView < VOTE_TOKENS_NEEDED) {
      this.props.onError();
    } else {
      const response = await videoVote({ videoId, address, privateKey });

      if (response) {
        saveVoteCache(videoId);
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
    return this.showVoteButton();
  }
}
