import React, { Component } from "react";

export default class SearchItem extends Component {

  render() {
    const { url, selected, channel_id, avatar, name } = this.props;
    
    return (
      <li>
        <a href={url} className={`${selected ? 'is-active' : ''}`} key={`channel-${channel_id}`}>
          <div className="o-flag o-flag--tiny">
            <div className="o-flag__img">
              <img className="o-avatar o-avatar--small" src={avatar} onError={(e) => e.target.src = 'https://i.imgur.com/32AwiVw.jpg'} />
            </div>
            <div className="o-flag__body">
              {name}
            </div>
          </div>
        </a>
      </li>

    );
  }
}
