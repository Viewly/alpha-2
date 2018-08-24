import React, { Component} from "react";
import { connect } from "react-redux";
import { showPendingTransactions, getTransaction, transactionPendingRemove } from '../../actions';

@connect((state, props) => ({
  pendingTransactions: state.pendingTransactions,
}), (dispatch) => ({
  showPendingTransactions: () => dispatch(showPendingTransactions()),
  transactionPendingRemove: (txn_id) => dispatch(transactionPendingRemove({ txn_id })),
}))
export default class HeaderContainer extends Component {
  componentDidMount () {
    this.mounted = true;
    this.checkTransactions();
  }

  componentWillUnmount () {
    this.mounted = false;
  }

  checkTransactions = async () => {
    const { pendingTransactions } = this.props;

    await Promise.all(pendingTransactions.map(item => this.checkSingleTransaction(item)))

    this.mounted && setTimeout(this.checkTransactions, 5000);
  }

  checkSingleTransaction = async (transaction) => {
    const { transactionPendingRemove } = this.props;
    const data = await getTransaction(transaction.txn_id);

    if (data && data.blockHash) {
      transactionPendingRemove(transaction.txn_id);
    }

    return true;
  }

  render() {
    const { pendingTransactions } = this.props;

    if (pendingTransactions.length === 0) {
      return null;
    }

    return (
      <div data-tooltip="At least one transaction is pending" data-position="bottom center">
        <div className="ui active inline loader">
          <div className="ui small text loader">Loading</div>
        </div>
      </div>
    );
  }
}
