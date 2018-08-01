import React, { Component} from "react";
import { Wallet } from 'ethers';
import { connect } from "react-redux";

const mapStateToProps = state => {
  return { wallet: state.wallet };
};

class GeneratorStep2 extends Component {
  render() {
    const { wallet, changeStep } = this.props;

    return (
      <div>
        Save mnemonic - only way to recover your wallet !
        <br />
        Mnemonic: <strong>{wallet.mnemonic}</strong>
        <br />
        <button onClick={() => changeStep(3)}>Next</button>
      </div>
    )
  }
}

export default connect(mapStateToProps, null)(GeneratorStep2);
