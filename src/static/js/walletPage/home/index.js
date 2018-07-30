import React, { Component} from "react";

export default class WalletHome extends Component {
  render() {
    const { history } = this.props;

    return (
      <div>
        <button onClick={() => history.push('/wallet/generate')}>Generate wallet</button>
      </div>
    )
  }
}
