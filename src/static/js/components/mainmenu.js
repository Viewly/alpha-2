import React, { Component } from "react";
import { connect } from "react-redux";

import { toggleCurrency } from '../actions';
import Portal from './portal';

@connect((state, props) => ({
  currency: state.currency,
}), (dispatch) => ({
  toggleCurrency: () => dispatch(toggleCurrency()),
}))
export default class MainMenu extends Component {
  state = {
    currencies: {
      EUR: {
        icon: 'euro sign',
        label: 'EUR'
      },
      USD: {
        icon: 'dollar sign',
        label: 'USD'
      }
    }
  }

  changeCurrency = (e) => {
    const { toggleCurrency } = this.props;

    e.preventDefault();
    toggleCurrency();
  }

  render() {
    const { currency } = this.props;
    return (
      <Portal container='react-main-menu'>
        <a href="#" onClick={this.changeCurrency}><i className={`${this.state.currencies[currency].icon} icon`} style={{ lineHeight: '1' }}></i> Currency ({this.state.currencies[currency].label})</a>
      </Portal>
    )
  }
}
