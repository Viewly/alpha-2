import React, { Component} from "react";
import { connect } from "react-redux";

import Portal from '../portal';
import { doSearch } from '../../actions';
import { STATUS_TYPE } from '../../constants';

const MIN_SEARCH_CHARACTERS = 3;

@connect((state) => ({
  search: state.search
}), (dispatch) => ({
  doSearch: (query) => dispatch(doSearch({ query })),
}))
export default class SearchInput extends Component {
  state = {
    searchText: ''
  }

  componentDidMount() {
    const elem = document.getElementById('search-box');
    elem && elem.parentNode.removeChild(elem);
  }

  componentDidUpdate(prevProps, prevState) {
    const { doSearch } = this.props;

    if (prevState.searchText !== this.state.searchText) {
      doSearch(this.state.searchText);
    }
  }

  onKeyDown = (e) => {
    if (e.key === 'Enter') {
      window.location = "/search?q=" + this.state.searchText;
    }
  }

  render() {
    const { search } = this.props;
    const isLoading = search._status === STATUS_TYPE.LOADING;

    return (
      <Portal container='react-search'>

        <div className="ui action icon input js-search-box">
          <button className="ui button js-search-button">
            <svg className="o-icon o-icon--small" width="24" height="24" viewBox="0 0 24 24">
              <g fill="none" fillRule="evenodd" stroke="currentColor" strokeWidth="2">
                <circle cx="10.5" cy="10.5" r="9.5" />
                <path d="M17.656 17.656l4.864 4.864" strokeLinecap="round" strokeLinejoin="round"/>
              </g>
            </svg>
          </button>
          <input className="c-header__search__input" placeholder="Search" value={this.state.searchText} onChange={(e) => this.setState({ searchText: e.target.value })} onKeyDown={this.onKeyDown} />
        </div>

        {this.state.searchText.length >= MIN_SEARCH_CHARACTERS && (
          <div className="c-header-dropdown">

            <div className="ui middle aligned selection list">

              {search.data.length === 0 && !isLoading && (
                <div className="item">
                  <div className="content">
                    <div className="header">No results found</div>
                  </div>
                </div>
              )}

              {search.data.map(item => (
                <a href={item.channel_url} className="item" key={`channel-${item.channel_id}`}>
                  <img className="ui avatar image" src={item.avatar_url} onError={(e) => e.target.src = 'https://i.imgur.com/32AwiVw.jpg' } />
                  <div className="content">
                    <div className="header">{item.display_name}</div>
                  </div>
                </a>
              ))}
            </div>

          </div>
        )}

      </Portal>
    );
  }
}
