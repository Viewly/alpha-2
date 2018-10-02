import React, { Component} from "react";
import NumberFormat from 'react-number-format';

export default class Item extends Component {
  render() {
    const { name, image, balance, fiat, fiatSign, labels, sendCallback, decrypted } = this.props;

    return (
      <div className='item'>
        <div className='ui tiny image'>
          <img src={image} />
        </div>
        <div className='middle aligned content'>
          <div className="header">{name}</div>

          <div className="meta">
            <span className="price">
              <NumberFormat value={balance} displayType={'text'} thousandSeparator={true} suffix={` ${name}`} decimalScale={3} />
            </span>
            <span className="stay">~ {fiat}{fiatSign}</span>
          </div>

          <div className="extra">
            {sendCallback && (
              <button onClick={() => sendCallback(name)} className='ui right floated button c-btn--primary'>
                Send
                {decrypted && <i className='right sign out icon'></i>}
                {!decrypted && <i className='right lock icon'></i>}
              </button>
            )}
            {labels && labels.map(item => <div key={`label-${item}`} className="ui label">{item}</div>)}
          </div>
        </div>
      </div>
    )
  }
}
