import React, { Component } from "react";
import { connect } from "react-redux";
import { bindActionCreators } from "redux";

import Portal from '../../portal';

import { reportVideo, checkVideoReport } from '../../../actions/video';
import ReportItem from './report_item';
import { REPORT_REASONS } from '../../../constants/report_reasons';

@connect((state, props) => ({
  videoReports: state.videoReports[props.match.params.videoId]
}), (dispatch) => (
  bindActionCreators({ reportVideo, checkVideoReport }, dispatch)
))
export default class VideoReport extends Component {
  state = {
    reason: REPORT_REASONS[0].id  // select first reason
  }

  componentDidMount() {
    this.modal = window.jQuery(this.ref).modal();
    this.modal.modal({ inverted: false });
  }

  modalOpen = () => {
    const { checkVideoReport, match: { params: { videoId } } } = this.props;
    checkVideoReport({ videoId })
    this.modal.modal('show');
  }

  modalClose = () => {
    this.modal.modal('hide');
  }

  reportVideo = () => {
    const { reportVideo, match: { params: { videoId } } } = this.props;

    reportVideo({ videoId, reason: this.state.reason });
  }

  render() {
    const { videoReports } = this.props;
    const isLoaded = videoReports && videoReports._status === 'LOADED';

    return (
      <Portal container='react-report'>
        <a className='c-link-neutral' onClick={() => this.modalOpen()} title="REPORT">
          <svg className="o-icon" width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 14.214s.75-.785 3-.785S12.75 15 15 15s3-.786 3-.786V4.786s-.75.785-3 .785S11.25 4 9 4s-3 .786-3 .786v9.428zM6 20v-6" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </a>

        <div ref={(ref) => this.ref = ref} className='ui modal c-modal c-modal--medium'>
          <i className="close icon small c-modal__close"></i>
          <header className="c-modal__header">Report this video</header>

          <div className="content">
            {!isLoaded && (
              <div className="ui">
                <div className="ui active inverted dimmer">
                  <div className="ui text loader">Loading</div>
                </div>
                <p></p>
              </div>
            )}

            {isLoaded && !videoReports.reported && (
              <ul className="c-report-list">
                {REPORT_REASONS.map(item => (
                  <ReportItem
                    {...item}
                    key={`report-${item.id}`}
                    reason={this.state.reason}
                    onChange={(e) => this.setState({ reason: e.target.value })}
                  />
                ))}
              </ul>
            )}

            {isLoaded && videoReports.reported && (
              <div>Thanks for reporting this video</div>
            )}

            <div className="u-text-right u-margin-top-large">
              <button className="ui button large u-margin-right-tiny" type="button" onClick={() => this.modalClose()}>Close</button>
              {isLoaded && !videoReports.reported && (
                <button className="ui button large c-btn--primary" type="submit" onClick={this.reportVideo}>Report video</button>
              )}
            </div>
          </div>
        </div>

      </Portal>
    )
  }
}
