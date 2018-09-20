import React, { Component } from "react";

require('../index.css');

export default class VoteMetamask extends Component {
  showVoteButton = () => {
    return <a href='javascript:;' className="ui button c-btn--secondary right labeled icon metamask-icon">Vote</a>;
  }

  render() {
    return this.showVoteButton()
  }
}
