import React, { Component} from "react";
import "./index.css";

export default class HeaderButton extends Component {

  walletClick = () => {
    const { history } = this.props;

    console.log('propz', this.props);
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
