import React, { Component} from "react";

const steps = [{
  title: 'Generate',
  description: 'Generate wallet'
}, {
  title: 'Backup',
  description: 'Save mnemonic'
}, {
  title: 'Encrypt',
  description: 'Encrypt wallet'
}, {
  title: 'Save',
  description: 'Save wallet'
}];

export default class Stepper extends Component {
  render() {
    const { step, maxStep } = this.props;

    return (
      <div>
        <div className="ui mini four ordered steps">
          {steps.map((item, idx) => {
            let classes = ['step'];

            if (maxStep > (idx + 1)) {
              classes.push('completed');
            }

            if (step === (idx + 1)) {
              classes.push('active');
            }

            return (
              <div key={`step-${item.title}`} className={classes.join(' ')}>
                <div className="content">
                  <div className="title">{item.title}</div>
                  <div className="description">{item.description}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    )
  }
}
