import React, { Component} from "react";
import { Wallet } from 'ethers';
import { connect } from "react-redux";
import { walletSave } from '../../../../actions';
import { updateWallets } from '../../../../utils';

// const mapDispatchToProps = dispatch => {
//   return {
//     saveEncryptedWallet: wallet => dispatch(saveEncryptedWallet(wallet)),
//     walletSave: wallet => dispatch(walletSave(wallet))
//   };
// };
//
// const mapStateToProps = state => {
//   return { wallet: state.wallet, encryptedWallet: state.encryptedWallet };
// };
@connect(null, (dispatch) => ({
  walletSave: wallet => dispatch(walletSave(wallet))
}))
export default class GeneratorStep4 extends Component {
  state = {
    showPrivate: false
  }

  finishGeneration = async () => {
    const { wallet, changeStep, walletSave } = this.props;
    const storage = { address: wallet.address, privateKey: wallet.privateKey };

    updateWallets(storage);
    await walletSave({ data: wallet.encrypted });
    changeStep(0);
  }

  render() {
    const { wallet } = this.props;

    return (
      <div>
        Wallet generation is complete. Last step is to save wallet so you can start using it.
        <br />
        Clicking on "Finish" button will save encrypted wallet on our website (we won't have access to your wallet).
        <br /><br />

        your address: <input type="text" size={70} readOnly value={wallet.address} />
        <br />

        private key:
        <input type={this.state.showPrivate ? 'text' : 'password'} value={wallet.privateKey} size={70} readOnly />
        <button onClick={() => this.setState({ showPrivate: !this.state.showPrivate })}>{this.state.showPrivate ? 'Hide' : 'Show'} private key</button>
        <br /><br />

        Data that will be saved on our server (encrypted):
        <br />
        <textarea rows={8} cols={120} value={wallet.encrypted} readOnly />
        <br /><br />

        <button onClick={this.finishGeneration}>Finish</button>
      </div>
    )
  }
}

// export default connect(mapStateToProps, mapDispatchToProps)(GeneratorStep4);
