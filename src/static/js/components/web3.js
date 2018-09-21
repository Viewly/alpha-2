import React, { Component } from "react";
import { connect } from "react-redux";
import { bindActionCreators } from 'redux';
import { fetchAccounts, fetchNetwork } from '../actions';

/* @source https://medium.com/coinmonks/react-web-dapp-with-metamask-web3-sotp-part-4-f252ebe8d07f */
const ONE_SECOND = 1000;
const ONE_MINUTE = ONE_SECOND * 60;

@connect(null, (dispatch) => (
  bindActionCreators({ fetchAccounts, fetchNetwork }, dispatch)
))
export default class Web3Provider extends Component {
  constructor(props) {
    super(props);

    this.props.fetchAccounts();
    this.props.fetchNetwork();
    this.interval = null;
    this.networkInterval = null;
  }

  /**
   * Start polling accounts, & network. We poll indefinitely so that we can
   * react to the user changing accounts or networks.
   */
  componentDidMount() {
    this.props.fetchAccounts();
    this.props.fetchNetwork();
    this.initPoll();
    this.initNetworkPoll();
  }

  /**
   * Init Web3/account polling, and prevent duplicate interval.
   * @return {void}
   */
  initPoll() {
    if (!this.interval) {
      this.interval = setInterval(this.props.fetchAccounts, ONE_SECOND);
    }
  }

  /**
   * Init network polling, and prevent duplicate intervals.
   * @return {void}
   */
  initNetworkPoll() {
    if (!this.networkInterval) {
      this.networkInterval = setInterval(this.props.fetchNetwork, ONE_MINUTE);
    }
  }

  render() {
    return null;
  }
}
