-- Seed Data for Viewly Alpha 2.
--
-- It creates root account, Viewly channel, and the entry for the Viewly Welcome Video.

-- Viewly Account
INSERT INTO "user" ("id", email, "password") VALUES (
  1,
  'info@view.ly',
  '$2b$12$Y02gWrjhV88GHvW6xg061.F1/U2nzt3amewAqofpeZGqNYAz79JIC'
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