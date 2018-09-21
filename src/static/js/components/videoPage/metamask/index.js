import React, { Component } from "react";
import { connect } from "react-redux";

import { videoVoteMetamask, videoVote } from '../../../actions';
import { saveVoteCache } from '../../../utils';
require('../index.css');

const VOTE_WEIGHT = 100;

@connect((state) => ({
  web3: state.web3,
}), (dispatch) => ({
  videoVoteMetamask: (videoId, account, weight) => dispatch(videoVoteMetamask({ videoId, account, weight })),
  videoVote: (videoId, address, weight, ecc_message, ecc_signature) => dispatch(videoVote({ videoId, address, weight, ecc_message, ecc_signature }))
}))
export default class VoteMetamask extends Component {

  voteClick = async () => {
    const { videoVoteMetamask, videoVote, videoId, web3: { metamask } } = this.props;
    const address = metamask.accounts[0];

    const voteSigned = await videoVoteMetamask(videoId, address, VOTE_WEIGHT);
    const response = await videoVote(videoId, address, VOTE_WEIGHT, voteSigned.ecc_message, voteSigned.ecc_signature);

    response && saveVoteCache(videoId);
  }

  showVoteButton = () => {
    return <a href='javascript:;' className="ui button c-btn--secondary right labeled icon metamask-icon" onClick={this.voteClick}>Vote</a>;
  }

  render() {
    return this.showVoteButton()
  }
}
