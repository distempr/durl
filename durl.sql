CREATE TABLE IF NOT EXISTS url (
  id TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  description TEXT,
  created TEXT,
  expires TEXT,
  last_hit TEXT,
  hit_count INTEGER DEFAULT 0 NOT NULL,
  archived INTEGER DEFAULT 0 NOT NULL
);

CREATE INDEX IF NOT EXISTS url_archived ON url (archived);
