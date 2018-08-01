import React, { Component} from "react";
import ReactDOM from "react-dom";

const walletPageContainer = document.getElementById('wallet-container');

export default class WalletPortal extends Component{
  constructor(props) {
    super(props);

    this.el = document.createElement('div');
  }

  componentDidMount() {
    walletPageContainer.appendChild(this.el);
  }

  componentWillUnmount() {
    walletPageContainer.removeChild(this.el);
  }

  render() {
    return ReactDOM.createPortal(
      this.props.children,
      this.el,
    );
  }
}
