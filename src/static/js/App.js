import React, { Component} from "react";
import { Route, withRouter } from 'react-router-dom';
import { connect } from "react-redux";
import { hot } from "react-hot-loader";

import { saveConfig, fetchAuthToken, walletsFetch, walletSave } from './actions';
import { walletsToStorage } from './utils';

import HeaderButton from './components/headerButton';
import WalletPage from './components/walletPage';
import VideoPage from './components/videoPage';

@withRouter
@connect((state) => ({
  authToken: state.authToken,
}), (dispatch) => ({
  saveConfig: wallet => dispatch(saveConfig(wallet)),
  fetchAuthToken: () => dispatch(fetchAuthToken()),
  walletsFetch: () => dispatch(walletsFetch())
}))
class App extends Component {
  // Load all initial data
  async componentDidMount() {
    const { saveConfig, fetchAuthToken, config, walletsFetch } = this.props;

    saveConfig(config);
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
        <Route path='/wallet' component={WalletPage} />
        <Route path='/v/:videoId' component={VideoPage} />
      </React.Fragment>
    );
  }
}

export default hot(module)(App);
