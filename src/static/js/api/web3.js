import isEmpty from 'lodash/isEmpty';

function getAccounts() {
  try {
    const { web3 } = window;
    // throws if no account selected
    return web3.eth.accounts;
  } catch (e) {
    return [];
  }
}

export async function fetchAccounts (baseUrl) {
  const { web3 } = window;
  const ethAccounts = getAccounts();

  return new Promise((resolve, reject) => {
    if (isEmpty(ethAccounts)) {
      web3 && web3.eth && web3.eth.getAccounts((err, accounts) => {
        err ? reject(err) : resolve(accounts);
      });
    } else {
      resolve(ethAccounts);
    }
  });
}


export async function fetchNetwork (baseUrl) {
  const { web3 } = window;

  if (!web3 || !web3.version) {
    return new Error('No web3');
  }

  return new Promise((resolve, reject) => {
    web3 && web3.version && web3.version.getNetwork((err, netId) => {
      err ? reject(err) : resolve(netId);
    });
  })
}
