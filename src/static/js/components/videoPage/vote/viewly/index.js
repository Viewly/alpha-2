import React, { Component } from "react";
import { connect } from "react-redux";

import { STATUS_TYPE } from '../../../../constants';
import { videoVote, unlockModalOpen, isVoted } from '../../../../actions';
import { saveVoteCache, signVoteHash } from '../../../../utils';

require('../index.css');

const VOTE_TOKENS_NEEDED = 100;
const VOTE_WEIGHT = 100;

@connect(null, (dispatch) => ({
  videoVote: (videoId, address, weight, ecc_message, ecc_signature) => dispatch(videoVote({ videoId, address, weight, ecc_message, ecc_signature })),
  unlockModalOpen: () => dispatch(unlockModalOpen()),
  isVoted: (videoId, address) => dispatch(isVoted({ videoId, address })),
}))
export default class VoteViewly extends Component {
  componentDidMount () {
    const { isVoted, videoId, wallet } = this.props;

    isVoted(videoId, wallet.address);
  }

  voteClick = async () => {
    const { wallet, unlockModalOpen, videoVote, videoId } = this.props;
    const { address, privateKey } = wallet;

    if (!wallet.decrypted) {
      unlockModalOpen();
    } else if (wallet.balanceView < VOTE_TOKENS_NEEDED) {
      this.props.onError();
    } else {
      const voteSigned = signVoteHash(videoId, address, privateKey, VOTE_WEIGHT);
      const response = await videoVote(videoId, address, VOTE_WEIGHT, voteSigned.ecc_message, voteSigned.ecc_signature);

      response && saveVoteCache(videoId);
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
