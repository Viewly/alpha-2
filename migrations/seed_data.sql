-- Seed Data for Viewly Alpha 2.
--
-- It creates root account, Viewly channel, and the entry for the Viewly Welcome Video.

-- Viewly Account
INSERT INTO "user" ("id", email, "password", confirmed_at, active, can_upload) VALUES (
  1,
  'info@view.ly',
  '$2b$12$Y02gWrjhV88GHvW6xg061.F1/U2nzt3amewAqofpeZGqNYAz79JIC',
  '2018-02-05 04:11:39.164642',
  true,
  true
);

-- Manually bump auto-increment, since we used hard-coded id above
ALTER SEQUENCE user_id_seq INCREMENT BY 1;

-- Viewly Channel
INSERT INTO channel ("id", user_id, slug, display_name, created_at) VALUES (
  '4947a648a26821e2',
  1,
  'Viewly',
  'Viewly',
  '2018-02-01 21:57:18.309355+01'
);

-- Viewly Welcome Video
INSERT INTO video (id, transcoder_job_id, transcoder_status, title,
                   description, tags, license, uploaded_at, published_at,
                   language, is_nsfw, video_metadata, stats, user_id, channel_id) VALUES
  ('0Ji59cI7oF3a',
    '1517873192661-7u9nxp',
    'complete',
    'Viewly @ London Blockchain Week 2018',
    'Next week the Viewly team will join some of the world’s top blockchain experts in London for London Blockchain Week 2018 at the Grange Tower Bridge Hotel. ',
    NULL, NULL,
    '2018-02-05 23:26:31.741524+00',
    '2018-02-05 23:34:41.500008+00',
    NULL, NULL, NULL, NULL, 1,
   '4947a648a26821e2');

INSERT INTO file_mapper (id,
                         s3_upload_bucket, s3_upload_video_key, s3_upload_thumbnail_key,
                         video_manifest_version, video_files, thumbnail_files, video_id) VALUES (
  1,
  'viewly-uploads-us1',
  '97595719-0454-4d69-b048-021650d7a95d.mp4',
  'f7924717-0246-40fe-9a5d-5a95996092b6.png',
  'v1', NULL,
  '{"nano": "us-west-2:viewly-videos-us1:/thumbnails/0Ji59cI7oF3a/nano.png", "tiny": "us-west-2:viewly-videos-us1:/thumbnails/0Ji59cI7oF3a/tiny.png", "large": "us-west-2:viewly-videos-us1:/thumbnails/0Ji59cI7oF3a/large.png", "small": "us-west-2:viewly-videos-us1:/thumbnails/0Ji59cI7oF3a/small.png"}',
  '0Ji59cI7oF3a');
