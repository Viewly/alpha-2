import React, { Component, Fragment } from "react";
import { connect } from "react-redux";

import { STATUS_TYPE } from '../../constants';
import { videoVote } from '../../actions';
import Portal from '../portal';
import { saveVoteCache } from '../../utils';

@connect((state, props) => ({
  wallet: state.wallets,
  vote: state.votes[props.match.params.videoId]
}), (dispatch) => ({
  videoVote: (videoId) => dispatch(videoVote(videoId))
}))
export default class VideoPage extends Component {
  voteClick = async () => {
    const { videoVote, match: { params: { videoId } } } = this.props;
    const { address, privateKey } = this.getFirstWallet();

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

  getFirstWallet = () => {
    const { wallet } = this.props;
    const keys = Object.keys(wallet);
    if (keys.length === 0) {
      return false;
    }

    const address = keys[0];
    const { privateKey } = wallet[address];

    return { address, privateKey };
  }

  showVoteButton = () => {
    const wallet = this.getFirstWallet();
    const { vote } = this.props;
    if (!wallet) {
      return <a href='javascript:;' className="ui button c-btn--secondary">Loading wallet</a>;
    }

    switch (vote) {
      case STATUS_TYPE.LOADING:
        return <a href='javascript:;' className="ui button c-btn--secondary">Voting ...</a>;
      case STATUS_TYPE.ERROR:
        return <a href='javascript:;' onClick={this.voteClick} className="ui button c-btn--secondary">Try again</a>;
      case true:
        return <a href='javascript:;' className="ui button c-btn--secondary">Voted</a>;
      default:
        return <a href='javascript:;' onClick={this.voteClick} className="ui button c-btn--secondary">Vote (new)</a>;
    }
  }

  render() {
    return (
      <Portal container='react-vote'>
        <Fragment>
          {this.showVoteButton()}
        </Fragment>
      </Portal>
    )
  }
}
