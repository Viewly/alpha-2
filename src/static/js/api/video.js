import { get, put } from './request';

export async function reportVideo(baseUrl, { videoId, reason }) {
  const url = `${baseUrl}/content_flag?video_id=${videoId}&flag_type=${reason}`;

  try {
    await put(url);
  } catch (e) {}

  return { videoId: videoId, reported: true };
}

export async function checkVideoReport(baseUrl, { videoId }) {
  const url = `${baseUrl}/content_flag?video_id=${videoId}`;
  try {
    await get(url);
    // If call is successfull, that means user has already reported this video
    return { videoId: videoId, reported: true };
  } catch (e) {
    // If user didn't report a video - GET will throw error 404 - we catch it here
    return { videoId, reported: false };
  }
}
