import React, { Fragment, Component } from "react";
import { connect } from "react-redux";

import { STATUS_TYPE } from '../../../../constants';
import { videoVoteMetamask, videoVote } from '../../../../actions';
import { fetchBalance } from '../../../../api/wallet';
import { saveVoteCache } from '../../../../utils';
require('../index.css');

const VOTE_WEIGHT = 100;

@connect((state) => ({
  web3: state.web3,
  config: state.config,
}), (dispatch) => ({
  videoVoteMetamask: (videoId, account, weight) => dispatch(videoVoteMetamask({ videoId, account, weight })),
  videoVote: (videoId, address, weight, ecc_message, ecc_signature) => dispatch(videoVote({ videoId, address, weight, ecc_message, ecc_signature }))
}))
export default class VoteMetamask extends Component {
  state = {
    errorType: false
  }

  componentDidMount () {
    this.modal = window.jQuery(this.ref).modal();
    this.modal.modal({ inverted: true });
  }

  checkViewBalance = async (address) => {
    const resp = await fetchBalance(null, { address });

    return resp.balanceView;
  }

  voteClick = async () => {
    const { config, web3, web3: { metamask } } = this.props;
    const address = metamask.accounts[0];

    if (config.ethChainId !== web3.network.network_id) {
      this.modalOpen('network');
    } else if (!address) {
      this.modalOpen('locked');
    } else {
      const balance = await this.checkViewBalance(address);

      if (balance < 100) {
        this.modalOpen('balance');
      } else {
        const { videoVoteMetamask, videoVote, videoId } = this.props;
  
        const voteSigned = await videoVoteMetamask(videoId, address, VOTE_WEIGHT);
  
        if (voteSigned.ecc_signature) {
          const response = await videoVote(videoId, address, VOTE_WEIGHT, voteSigned.ecc_message, voteSigned.ecc_signature);
          response && saveVoteCache(videoId);
        }
      }
    }
  }

  modalOpen = (type) => {
    this.setState({ errorType: type });
    this.modal.modal('show');
  }

  modalClose = () => {
    this.setState({ errorType: false })
    this.modal.modal('hide');
  }

  showVoteButton = () => {
    const { vote, web3: { metamask } } = this.props;

    if (metamask._status === STATUS_TYPE.ERROR) {
      // don't show metamask button if metamask is not installed
      // return <a href='javascript:;' onClick={() => this.modalOpen('metamask')} className="ui button c-btn--secondary right labeled icon metamask-icon">Install</a>;
      return null;
    }

    switch (vote) {
      case STATUS_TYPE.LOADING:
        return <a href='javascript:;' className="ui button c-btn--secondary right labeled icon metamask-icon">Voting ...</a>;
      case STATUS_TYPE.ERROR:
        return <a href='javascript:;' onClick={this.voteClick} className="ui button c-btn--secondary right labeled icon metamask-icon">Try again</a>;
      case true:
        return <a href='javascript:;' className="ui button c-btn--secondary disabled right labeled icon metamask-icon"><i className='check icon' />Voted</a>;
      default:
        return <a href='javascript:;' onClick={this.voteClick} className="ui button c-btn--secondary right labeled icon metamask-icon">Vote</a>;
    }
  }

  render() {
    const { config } = this.props;

    return (
      <Fragment>
        {this.showVoteButton()}

        <div className="ui modal c-modal c-modal--narrow" ref={(ref) => this.ref = ref}>
          <i className="close icon small c-modal__close"></i>

          <div className="content u-padding-bottom-large">
            {this.state.errorType === 'network' && (
                <div className="u-text-center">
                  <h3 className="c-modal__title">Wrong network</h3>
                  <p>Please select {config.ethChain.toUpperCase()} Ethereum network in Metamask.</p>
                  <img src="https://i.imgur.com/1XBQ7Tl.png" alt="" />
                </div>
            )}

            {this.state.errorType === 'locked' && (
              <div className="u-text-center">
                <div className="c-metamask-logo is-locked">
                  <img src="/static/img/metamask-logo.png" alt="" />
                  <span className="c-metamask-logo__icon-locked">
                    <svg className="o-icon" width="24" height="24" viewBox="0 0 24 24">
                      <g transform="translate(2 1)" stroke="currentColor" strokeWidth="2" fill="none" fillRule="evenodd" strokeLinecap="round" strokeLinejoin="round">
                        <rect y="10" width="20" height="12" rx="2"/>
                        <path d="M5 10V5.556C5 2.487 7.239 0 10 0s5 2.487 5 5.556V10"/>
                      </g>
                    </svg>
                  </span>
                </div>
                <h3 className="c-modal__title">MetaMask locked</h3>
                <p>Metamask wallet appears to be <b>locked</b>! <br />Please unlock it to proceed.</p>
              </div>
            )}

            {this.state.errorType === 'metamask' && (
              <div className="u-text-center">
                <div className="c-metamask-logo">
                  <img src="/static/img/metamask-logo.png" alt="" />
                  <span className="c-metamask-logo__icon-locked">
                    <svg className="o-icon" width="24" height="24" viewBox="0 0 24 24">
                      <g transform="translate(2 1)" stroke="currentColor" strokeWidth="2" fill="none" fillRule="evenodd" strokeLinecap="round" strokeLinejoin="round">
                        <rect y="10" width="20" height="12" rx="2"/>
                        <path d="M5 10V5.556C5 2.487 7.239 0 10 0s5 2.487 5 5.556V10"/>
                      </g>
                    </svg>
                  </span>
                </div>

                <h3 className="c-modal__title">Get Metamask for your browser</h3>
                <p>Metamask wallet is the bridge between Viewly and Ethereum blockchain.</p>
                <a className="ui button c-btn--primary c-btn--with-icon u-type-uppercase u-margin-top-small" href="https://metamask.io/" target="_blank">
                  <svg className="o-icon o-icon--small" width="24" height="24" viewBox="0 0 24 24">
                    <path d="M1 14v3.6C1 18.925 2.094 20 3.444 20h17.112C21.906 20 23 18.925 23 17.6V14M7 9l5 5 5-5m-5-7v12" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  Get MetaMask
                </a>
              </div>
            )}

            {this.state.errorType === 'balance' && (
              <div className="u-text-center">
                <h3 className="c-modal__title">Insufficient VIEW Tokens</h3>
                <p>
                  Voting is free, however it does require at least 100 VIEW Tokens in your
                  Ethereum wallet <i>(for a minimum of 7 days)</i>.
                </p>
              </div>
            )}

          </div>
        </div>

      </Fragment>
    )
  }
}
