import provider from '../ethereum';

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
