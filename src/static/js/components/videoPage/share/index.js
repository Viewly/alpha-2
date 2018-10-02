import React, { Component } from "react";
import { connect } from "react-redux";
import copy from 'copy-to-clipboard';
import {
  EmailIcon,
  EmailShareButton,
  FacebookIcon,
  FacebookShareButton,
  GooglePlusIcon,
  GooglePlusShareButton,
  RedditIcon,
  RedditShareButton,
  TwitterIcon,
  TwitterShareButton,
} from 'react-share';

import Portal from '../../portal';

require('./index.css');

@connect((state, props) => ({
  config: state.config
}))
export default class VideoShare extends Component {
  state = {
    shareUrl: '',
    shareTitle: '',
    twitterTitle: 'Found this video on @OfficialViewly',
    embedCode: ''
  }

  componentDidMount() {
    this.modal = window.jQuery(this.ref).modal();
    this.modal.modal({ inverted: false });

    this.embedModal = window.jQuery(this.embedRef).modal();
    this.embedModal.modal({ inverted: false });

    this.setState({
      shareUrl: window.location.href,
      shareTitle: `View.ly - ${document.title}`,
      embedCode: this.getEmbedCode()
    })
  }

  getEmbedCode = () => {
    const { config: { playerUrl }, match: { params: { videoId } } } = this.props;

    return `<iframe src="${playerUrl}/?videoId=${videoId}&amp;autoPlay=true" frameborder="0" scrolling="0" allowfullscreen="" allow="autoplay"></iframe>`;
  }

  modalOpen = () => {
    this.modal.modal('show');
  }

  modalClose = () => {
    this.modal.modal('hide');
  }

  embedOpen = () => {
    this.embedModal.modal('show');
  }

  embedClose = () => {
    this.embedModal.modal('hide');
  }

  render() {
    return (
      <Portal container='react-share'>
        <a className='c-link-neutral' onClick={() => this.modalOpen()} title="Share">
          <i className="share alternate icon"></i>
        </a>

        <div ref={(ref) => this.ref = ref} className='ui tiny modal'>
          <i className="close icon"></i>

          <div className='header'>
            Share this video
          </div>
          <div className='content social__share'>
            <div className='social__share__item' onClick={() => this.embedOpen()}>
              <div className='social__share__item--embed'>
                <i className="code icon"></i>
              </div>
              <span>Embed</span>
            </div>

            <FacebookShareButton url={this.state.shareUrl} quote={this.state.shareTitle} className='social__share__item'>
              <FacebookIcon
                size={64}
                round />
              <span>Facebook</span>
            </FacebookShareButton>

            <TwitterShareButton url={this.state.shareUrl} title={this.state.twitterTitle} className='social__share__item'>
              <TwitterIcon
                size={64}
                round />
              <span>Twitter</span>
            </TwitterShareButton>

            <RedditShareButton url={this.state.shareUrl} title={this.state.shareTitle} className='social__share__item'>
              <RedditIcon
                size={64}
                round />
              <span>Reddit</span>
            </RedditShareButton>

            <GooglePlusShareButton url={this.state.shareUrl} className='social__share__item'>
              <GooglePlusIcon
                size={64}
                round />
              <span>Google+</span>
            </GooglePlusShareButton>

            <EmailShareButton url={this.state.shareUrl} subject='View.ly' body={this.state.shareTitle} className='social__share__item'>
              <EmailIcon
                size={64}
                round />
              <span>Email</span>
            </EmailShareButton>
          </div>

          <div className="content">
            <div className="ui fluid action input">
              <input type="text" value={this.state.shareUrl} />
              <button className="ui primary right labeled icon button" onClick={() => {
                copy(this.state.shareUrl);
                this.modalClose();
              }}>
                <i className="copy icon" />
                Copy
              </button>
            </div>
          </div>

        </div>

        <div ref={(ref) => this.embedRef = ref} className='ui tiny modal'>
          <i className="close icon"></i>

          <div className='header'>
            Embed
          </div>

          <div className="content">
            <div className="ui form">
              <div className="field">
                <textarea rows="4" readOnly value={this.state.embedCode} />
              </div>
            </div>
          </div>

          <div className="actions">
            <div className="ui primary button" onClick={() => {
              copy(this.state.embedCode);
              this.embedClose();
            }}>Copy to clipboard</div>
            <div className="ui button" onClick={() => this.embedClose()}>Cancel</div>
          </div>

        </div>

      </Portal>
    )
  }
}
