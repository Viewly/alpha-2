import React, { Component} from "react";
import { Link } from 'react-router-dom';
import { withRouter } from 'react-router-dom'
import { connect } from "react-redux";

import "./index.css";

// @withRouter
// @connect
const mapDispatchToProps = dispatch => {
  return {
    addArticle: article => dispatch(addArticle(article))
  };
};

class HeaderButton extends Component{
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


export default connect(null, mapDispatchToProps)(HeaderButton);
