import React, { Component} from "react";

import Stepper from './stepper';
import GeneratorStep1 from './step1';
import GeneratorStep2 from './step2';
import GeneratorStep3 from './step3';
import GeneratorStep4 from './step4';

export default class WalletGenerator extends Component {

  state = {
    step: 1,
    maxStep: 1,
    wallet: {}
  }

  changeStep = (nextStepNumber, wallet = {}) => {
    const { history } = this.props;

    if (nextStepNumber === 0) {
      this.setState({ step: 1 });
      history.push(`/wallet/${this.state.wallet.address}`);
    } else {
      if (this.state.maxStep < nextStepNumber) {
        this.setState({ maxStep: nextStepNumber });
      }
      this.setState({ step: nextStepNumber, wallet });
    }
  }

  renderStep = () => {
    switch (this.state.step) {
      case 1: return <GeneratorStep1 changeStep={this.changeStep} wallet={this.state.wallet} />;
      case 2: return <GeneratorStep2 changeStep={this.changeStep} wallet={this.state.wallet} />;
      case 3: return <GeneratorStep3 changeStep={this.changeStep} wallet={this.state.wallet} />;
      case 4: return <GeneratorStep4 changeStep={this.changeStep} wallet={this.state.wallet} />;
    }
  }
  render() {
    return (
      <div className='ui container'>
        <Stepper step={this.state.step} maxStep={this.state.maxStep} />

        {this.renderStep()}
      </div>
    )
  }
}
