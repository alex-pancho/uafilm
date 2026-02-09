
CREATE TABLE IF NOT EXISTS season (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER,
    season_number INTEGER DEFAULT 0,
    title_season TEXT
);

CREATE TABLE IF NOT EXISTS playlist (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER,
    season_id INTEGER,
    info TEXT,
    source TEXT,
    m3u_url TEXT,
    subtitle TEXT,
    ext_player TEXT
);

INSERT INTO season (content_id, season_number, title_season)
SELECT
    c._id,
    CASE
        WHEN c.type_src IN ('serial', 'series') THEN 1
        ELSE 0
    END AS season_number,
    NULL
FROM films_bk.content c;


INSERT INTO playlist (content_id, season_id, ext_player, source)
SELECT
    c._id,
    s._id,
    o.m3u_links,
    'import'
FROM films_bk.content o
JOIN content c ON c._id = o._id
JOIN season s ON s.content_id = c._id;