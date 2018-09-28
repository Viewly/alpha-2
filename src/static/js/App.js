import React, { Component} from "react";
import { Route, withRouter } from 'react-router-dom';
import { connect } from "react-redux";
import { hot } from "react-hot-loader";

import { saveConfig, fetchAuthToken, walletsFetch, walletSave, fetchExchangeRate } from './actions';
import { walletsToStorage } from './utils';
import { STATUS_TYPE } from './constants';

import HeaderContainer from './components/headerContainer';
import UnlockModal from './components/unlockModal';
import WalletPage from './components/walletPage';
import VideoVote from './components/videoPage/vote';
import VideoShare from './components/videoPage/share';
import PublishVideoPage from './components/publishVideoPage';
import SearchInput from './components/searchInput';

@withRouter
@connect((state) => ({
  authToken: state.authToken,
  config: state.config,
}), (dispatch) => ({
  saveConfig: wallet => dispatch(saveConfig(wallet)),
  fetchAuthToken: () => dispatch(fetchAuthToken()),
  walletsFetch: () => dispatch(walletsFetch()),
  fetchExchangeRate: () => dispatch(fetchExchangeRate())
}))
class App extends Component {
  // Load all initial data
  async componentDidMount() {
    const { saveConfig, fetchAuthToken, walletsFetch, fetchExchangeRate } = this.props;

    saveConfig(window.walletConfig);

    if (window.walletConfig.isAuthenticated) {
      fetchExchangeRate();
      await fetchAuthToken();
      walletsFetch();
    }
  }

  render() {
    const { authToken, config } = this.props;

    if (config._status !== STATUS_TYPE.LOADED) {
      return false;
    }

    return(
      <React.Fragment>
        <Route path='/' component={HeaderContainer} />
        <Route path='/' component={UnlockModal} />
        <Route path='/' component={SearchInput} />
        <Route path='/v/:videoId' component={VideoShare} />
        {authToken && <Route path='/wallet' component={WalletPage} />}
        {authToken && <Route path='/v/:videoId' component={VideoVote} />}
        {authToken && <Route path='/upload/publish/to_ethereum/:videoId' component={PublishVideoPage} />}
      </React.Fragment>
    );
  }
}

export default hot(module)(App);
