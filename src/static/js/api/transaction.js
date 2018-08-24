import provider from '../ethereum';
import { addPendingTransaction, removePendingTransaction } from '../utils';

export async function transactionWait(baseUrl, { txn_id }) {
  let txn;

  const wait = await new Promise(resolve => {
    const refreshInterval = setInterval(async () => {
      txn = await provider.getTransaction(txn_id);

      if (txn && txn.blockHash) {
        clearInterval(refreshInterval);
        resolve();
      }
    }, 1000);
  });

  const receipt = await provider.getTransactionReceipt(txn_id);

  if (receipt && receipt.status === 0) {
    throw new Error('Transaction execution has failed.');
  }

  return { txn, receipt };
}

export async function getTransaction(txn_id) {
  const txn = await provider.getTransaction(txn_id);

  return txn;
}

export async function transactionPendingAdd(baseUrl, { txn_id, type, value }) {
  const transaction = {
    txn_id,
    context: { type, value }
  };

  addPendingTransaction(transaction);

  return transaction;
}

export async function transactionPendingRemove(baseUrl, { txn_id }) {
  removePendingTransaction(txn_id);

  return txn_id;
}
