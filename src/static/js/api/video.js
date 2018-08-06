import { put } from './request';
import sigUtil from 'eth-sig-util';
import ethUtil from 'ethereumjs-util';

export async function videoVote (baseUrl, { videoId, address, privateKey, weight = 100 }) {
  const privateBuffer = ethUtil.toBuffer(privateKey);
  const time = Math.round(+new Date()/1000);
  const params = [
    {"type": "string", "name": "Video ID", "value": videoId},
    {"type": "uint8", "name": "Vote Weight (%)", "value": weight},
    {"type": "uint32", "name": "Timestamp", "value": time}
  ];

  const msgParams = { data: params };
  const signedHash = sigUtil.signTypedData(privateBuffer, msgParams);

  const url = `${baseUrl}/vote`;
  const response = await put(url, {
    video_id: videoId,
    weight,
    eth_address: address,
    ecc_message: JSON.stringify([ params, address ]),
    ecc_signature: signedHash
  });

  return { videoId };
}
