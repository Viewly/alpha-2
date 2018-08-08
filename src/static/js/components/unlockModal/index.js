import React, { Component} from "react";
import { connect } from "react-redux";

import Portal from '../portal';
import { unlockModalOpen, unlockModalClose } from '../../actions';

@connect((state) => ({
  walletUnlockModal: state.walletUnlockModal,
}), (dispatch) => ({
  unlockModalOpen: () => dispatch(unlockModalOpen()),
  unlockModalClose: () => dispatch(unlockModalClose()),
}))
export default class UnlockModal extends Component {
  componentDidMount () {
    const { unlockModalOpen, unlockModalClose } = this.props;

    this.modal = window.jQuery(this.ref);
    this.modal.modal({
      inverted: true,
      onHide: () => {
        unlockModalClose();
      },
      onShow: () => {
        unlockModalOpen();
      }
    })
  }

  getSnapshotBeforeUpdate(prevProps) {
    const { walletUnlockModal } = this.props;

    if (!prevProps.walletUnlockModal && walletUnlockModal) {
      this.modal.modal('show');
    } else if (prevProps.walletUnlockModal && !walletUnlockModal) {
      this.modal.modal('hide');
    }

    return null;
  }

  render() {
    return (
      <Portal container='react-modal'>
        <div ref={(ref) => window.ref = this.ref = ref} className='ui mini modal'>
          <div className='header'>
            Unlock wallet
          </div>
          <div className='content'>
            <div className='ui form'>
              <div className="field">
                <label>Wallet password</label>
                <input type='text' />
              </div>
            </div>
          </div>
          <div className="actions">
            <div className="ui button">Cancel</div>
            <div className="ui green button">Unlock</div>
          </div>
        </div>
      </Portal>
    );
  }
}
