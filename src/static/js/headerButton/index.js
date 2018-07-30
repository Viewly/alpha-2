import React, { Component} from "react";
import { Link } from 'react-router-dom';
import { withRouter } from 'react-router-dom'

import "./index.css";

@withRouter
export default class HeaderButton extends Component{
  walletClick = () => {
    const { history } = this.props;

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
