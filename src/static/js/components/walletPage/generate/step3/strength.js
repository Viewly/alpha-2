import React, { Component} from "react";
import taiPasswordStrength from 'tai-password-strength';

export default class Strength extends Component {
  state = {
    currentStatusText: 'Very weak'
  }

  statuses = {
    'VERY_WEAK': {
      percentage: 0,
      label: 'Very weak'
    },
    'WEAK' : {
      percentage: 25,
      label: 'Weak'
    },
    'REASONABLE' : {
      percentage: 50,
      label: 'Reasonable'
    },
    'STRONG': {
      percentage: 75,
      label: 'Strong'
    },
    'VERY_STRONG': {
      percentage: 100,
      label: 'Very strong'
    }
  }

  componentDidMount () {
    const { password } = this.props;

    this.progress = window.jQuery(this.ref);
    this.handlePassword(password);
  }

  componentDidUpdate (prevProps) {
    const { password } = this.props;

    if (prevProps.password !== password) {
      this.handlePassword(password);
    }
  }

  handlePassword = (password) => {
    if (password.length === 0) {
      this.progress.progress({ percent: 0 });
      this.setState({ currentStatusText: 'Very weak' });
    } else {
      const strengthTester = new taiPasswordStrength.PasswordStrength();
      const results = strengthTester.check(password);
      const current = this.statuses[results.strengthCode];

      this.progress.progress({ percent: current.percentage });
      this.setState({ currentStatusText: this.statuses[results.strengthCode].label });
    }
  }

  render() {
    const { password } = this.props;

    return (
      <div className="ui indicating progress" ref={ref => this.ref = ref} data-value="0" data-total="100">
        <div className="bar"></div>
        <div className="label">Password strength - {this.state.currentStatusText}</div>
      </div>
    )
  }
}
