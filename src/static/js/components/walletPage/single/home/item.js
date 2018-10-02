import React, { Component} from "react";
import NumberFormat from 'react-number-format';

export default class Item extends Component {
  render() {
    const { name, image, balance, fiat, fiatSign, labels, sendCallback, decrypted } = this.props;

    return (
      <div className="o-grid o-grid--auto o-grid--middle">
        <div className='o-grid__cell'>
          <div className='c-wallet__cryptocurrency-icon'>
            <img src={image} />
          </div>
        </div>
        <div className='o-grid__cell'>
          <dl className="c-wallet__currency">
            <dt className="header">
              {name}
            </dt>
            <dd className="c-wallet__currency__amount">
              <span className="price">
                <NumberFormat value={balance} displayType={'text'} thousandSeparator={true} suffix={` ${name}`} decimalScale={3} />
              </span>
            </dd>
            <dd className="c-wallet__currency__fiat"><span className="stay">~ {fiat}{fiatSign}</span></dd>
          </dl>
        </div>
        <div className="o-grid__cell u-margin-left-auto">
          {sendCallback && (
            <button onClick={() => sendCallback(name)} className='ui right floated button c-btn--primary'>
              Send
              {decrypted && <i className='right sign out icon'></i>}
              {!decrypted && <i className='right lock icon'></i>}
            </button>
          )}
        </div>
      </div>
    )
  }
}
