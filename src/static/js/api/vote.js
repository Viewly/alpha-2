import { get, put } from './request';

export async function videoVote (baseUrl, { videoId, address, weight = 100, ecc_message, ecc_signature }) {
  try {
    const checkVote = await isVoted(baseUrl, { videoId, address });

    return { videoId };
  } catch (e) {
    const url = `${baseUrl}/vote`;
    const response = await put(url, {
      video_id: videoId,
      weight,
      eth_address: address,
      ecc_message,
      ecc_signature
    });

    return { videoId };
  }
}

async function isVoted (baseUrl, { videoId, address }) {
  const url = `${baseUrl}/vote?video_id=${videoId}&eth_address=${address}`;

  const { body } = await get(url);
  return body;
}
