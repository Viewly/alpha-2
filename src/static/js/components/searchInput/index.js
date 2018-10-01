import React, { Component } from "react";
import { connect } from "react-redux";

import Portal from '../portal';
import { doSearch } from '../../actions';
import { STATUS_TYPE } from '../../constants';

import SearchItem from './search_item';

const MIN_SEARCH_CHARACTERS = 3;

@connect((state) => ({
  search: state.search
}), (dispatch) => ({
  doSearch: (query) => dispatch(doSearch({ query })),
}))
export default class SearchInput extends Component {
  state = {
    searchText: '',
    selected: -1,
    dropdownOpen: false,
    focused: false,
  }

  componentDidMount() {
    const elem = document.getElementById('search-box');
    const reactSearchContainer = document.getElementById('react-search');
    elem && elem.parentNode.removeChild(elem);
    reactSearchContainer.classList.add('u-1/1');
  }

  componentDidUpdate(prevProps, prevState) {
    const { doSearch } = this.props;

    if (prevState.searchText !== this.state.searchText) {
      this.setState({
        selected: -1,
        dropdownOpen: this.state.searchText.length >= MIN_SEARCH_CHARACTERS
      });

      this.state.searchText.length >= MIN_SEARCH_CHARACTERS && doSearch(this.state.searchText);
    }

    if (prevState.focused === false && this.state.focused === true) {
      document.body.classList.add('has-search-activated');
    } else if (prevState.focused === true && this.state.focused === false) {
      document.body.classList.remove('has-search-activated');
    }
  }

  onKeyDown = (e) => {
    const { search: { data } } = this.props;

    switch (e.key) {
      case 'Enter':
        this.onSearch();
        break;

      case 'Escape':
        this.onBlur();
        break;

      case 'ArrowUp':
        this.setState({ selected: (this.state.selected === -1) ? data.length - 1 : this.state.selected - 1 });
        break;

      case 'ArrowDown':
        this.setState({ selected: (this.state.selected >= data.length - 1) ? -1 : this.state.selected + 1 });
        break;
    }
  }

  onSearch = () => {
    const { search: { data } } = this.props;

    this.setState({ dropdownOpen: false });
    window.location = (this.state.selected === -1)
      ? "/search?q=" + this.state.searchText
      : data[this.state.selected].channel_url;
  }

  onBlur = () => {
    this.input.blur();
    setTimeout(() => this.setState({ dropdownOpen: false, selected: -1, focused: false }), 100);
  }

  onFocus = (e) => {
    this.setState({ focused: true, dropdownOpen: this.state.searchText.length >= MIN_SEARCH_CHARACTERS });
    e.target.select();
  }

  render() {
    const { search } = this.props;

    return (
      <Portal container='react-search'>

        <div className="ui action icon input">
          <button className="ui button" onClick={this.onSearch}>
            <svg className="o-icon o-icon--small" width="24" height="24" viewBox="0 0 24 24">
              <g fill="none" fillRule="evenodd" stroke="currentColor" strokeWidth="2">
                <circle cx="10.5" cy="10.5" r="9.5" />
                <path d="M17.656 17.656l4.864 4.864" strokeLinecap="round" strokeLinejoin="round" />
              </g>
            </svg>
          </button>

          <input
            ref={(ref) => this.input = ref}
            className="c-header__search__input"
            placeholder={this.state.selected === -1 ? 'Search' : search.data[this.state.selected].display_name}
            name="search_input"
            value={this.state.selected === -1 ? this.state.searchText : ''}
            onChange={(e) => this.setState({ searchText: e.target.value })}
            onBlur={this.onBlur}
            onFocus={this.onFocus}
            onKeyDown={this.onKeyDown}
          />
        </div>

        {this.state.dropdownOpen && search.data.length !== 0 && (
          <div className="c-search-dropdown">
            <p className="c-search-dropdown__info-message">To search for videos press enter on your keyboard.</p>

            <h3 className="c-search-dropdown__heading">Channels</h3>
            <ul className="c-search-dropdown__list">
              {search.data.map((item, idx) => (
                <SearchItem
                  key={`search-${item.channel_id}`} 
                  channel_id={item.channel_id} 
                  url={item.channel_url} 
                  selected={this.state.selected === idx} 
                  avatar={item.avatar_url} 
                  name={item.display_name} />
              ))}
            </ul>
          </div>
        )}

      </Portal>
    );
  }
}
