import React, { Component} from "react";
import ReactDOM from "react-dom";

export default class Portal extends Component{
  constructor(props) {
    super(props);

    this.container = document.getElementById(props.container);
    this.el = document.createElement('div');
  }

  componentDidMount() {
    if (this.container) {
      this.container.innerHTML = '';
      this.container.appendChild(this.el);
    }
  }

  componentWillUnmount() {
    this.container && this.container.removeChild(this.el);
  }

  render() {
    return this.container && ReactDOM.createPortal(
      this.props.children,
      this.el,
    );
  }
}
