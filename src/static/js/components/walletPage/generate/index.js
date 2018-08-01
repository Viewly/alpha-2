import React, { Component} from "react";
import GeneratorStep1 from './step1';
import GeneratorStep2 from './step2';
import GeneratorStep3 from './step3';
import GeneratorStep4 from './step4';

export default class WalletGenerator extends Component {

  state = {
    step: 1
  }

  changeStep = (nextStepNumber) => {
    const { history } = this.props;

    if (nextStepNumber === 0) {
      this.setState({ step: 1 });
      history.push('/wallet');
    } else {
      this.setState({ step: nextStepNumber });
    }
  }

  render() {
    console.log('propz', this.props);
    switch (this.state.step) {
      case 1: return <GeneratorStep1 changeStep={this.changeStep} />;
      case 2: return <GeneratorStep2 changeStep={this.changeStep} />;
      case 3: return <GeneratorStep3 changeStep={this.changeStep} />;
      case 4: return <GeneratorStep4 changeStep={this.changeStep} />;
    }
  }
}
