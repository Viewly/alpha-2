import React, { Component } from "react";

export default class ReportItem extends Component {
  render() {
    const { id, title, description, reason, onChange } = this.props;

    return (
      <li>
        <div className="o-flag o-flag--top o-flag--small">
          <div className="o-flag__img">
            <label className="c-input-radio">
              <input
                className="c-input-radio__input"
                type="radio"
                name="reason"
                id={`report-${id}`}
                value={id}
                checked={reason === id}
                onChange={onChange}
              />
              <span className="c-input-radio__faux-input"></span>
            </label>
          </div>
          <div className="o-flag__body">
            <dl>
              <dt><label htmlFor={`report-${id}`}>{title}</label></dt>
              <dd>{description}</dd>
            </dl>
          </div>
        </div>
      </li>

    )
  }
}
