import { makeApiCall } from '../api/request';
import * as videoApi from '../api/video';

export const VIDEO_REPORT_START = 'AUTH/VIDEO_REPORT_START';
export const VIDEO_REPORT_SUCCESS = 'AUTH/VIDEO_REPORT_SUCCESS';
export const VIDEO_REPORT_ERROR = 'AUTH/VIDEO_REPORT_ERROR';
export const reportVideo = makeApiCall(videoApi.reportVideo, VIDEO_REPORT_START, VIDEO_REPORT_SUCCESS, VIDEO_REPORT_ERROR);

export const VIDEO_REPORT_CHECK_START = 'AUTH/VIDEO_REPORT_CHECK_START';
export const VIDEO_REPORT_CHECK_SUCCESS = 'AUTH/VIDEO_REPORT_CHECK_SUCCESS';
export const VIDEO_REPORT_CHECK_ERROR = 'AUTH/VIDEO_REPORT_CHECK_ERROR';
export const checkVideoReport = makeApiCall(videoApi.checkVideoReport, VIDEO_REPORT_CHECK_START, VIDEO_REPORT_CHECK_SUCCESS, VIDEO_REPORT_CHECK_ERROR);
