import React, { Component} from "react";
import { Link } from 'react-router-dom';
import { withRouter } from 'react-router-dom'
import { connect } from "react-redux";
import { saveConfig, fetchAuthToken } from '../../actions';

import "./index.css";

@connect(null, (dispatch) => ({
  saveConfig: wallet => dispatch(saveConfig(wallet)),
  fetchAuthToken: () => dispatch(fetchAuthToken())
}))
export default class HeaderButton extends Component {

  componentDidMount() {
    const { saveConfig, fetchAuthToken, config } = this.props;

    saveConfig(config);
    fetchAuthToken();
  }

  walletClick = () => {
    const { history } = this.props;

    console.log('propz', this.props);
    // history.push('/wallet');
    window.location.href = '/wallet';
  }

  render() {
    return(
      <div className="App">
        <p onClick={this.walletClick}>[Wallet]</p>
      </div>
    );
  }
}
