import React, { Component} from "react";
import { Route, withRouter } from 'react-router-dom';
import { connect } from "react-redux";
import { hot } from "react-hot-loader";

import { saveConfig, fetchAuthToken, walletsFetch, walletSave, fetchExchangeRate } from './actions';
import { walletsToStorage } from './utils';

import HeaderButton from './components/headerButton';
import UnlockModal from './components/unlockModal';
import WalletPage from './components/walletPage';
import VideoPage from './components/videoPage';

@withRouter
@connect((state) => ({
  authToken: state.authToken,
}), (dispatch) => ({
  saveConfig: wallet => dispatch(saveConfig(wallet)),
  fetchAuthToken: () => dispatch(fetchAuthToken()),
  walletsFetch: () => dispatch(walletsFetch()),
  fetchExchangeRate: () => dispatch(fetchExchangeRate())
}))
class App extends Component {
  // Load all initial data
  async componentDidMount() {
    const { saveConfig, fetchAuthToken, config, walletsFetch, fetchExchangeRate } = this.props;

    saveConfig(config);
    fetchExchangeRate();
    await fetchAuthToken();
    walletsFetch();
  }

  render() {
    const { authToken } = this.props;

    if (!authToken) {
      return null;
    }

    return(
      <React.Fragment>
        <Route path='/' component={HeaderButton} />
        <Route path='/' component={UnlockModal} />
        <Route path='/wallet' component={WalletPage} />
        <Route path='/v/:videoId' component={VideoPage} />
      </React.Fragment>
    );
  }
}

export default hot(module)(App);
