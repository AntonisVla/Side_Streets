CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY,

    name TEXT NOT NULL
        CHECK(length(trim(name)) BETWEEN 2 AND 80),

    category TEXT NOT NULL
        CHECK(category IN (
            'Coffee & bites',
            'Art & culture',
            'Outdoors',
            'Little shops'
        )),

    neighborhood TEXT NOT NULL
        CHECK(length(trim(neighborhood)) BETWEEN 2 AND 60),

    address TEXT NOT NULL
        CHECK(length(trim(address)) BETWEEN 3 AND 120),

    description TEXT NOT NULL
        CHECK(length(trim(description)) BETWEEN 20 AND 1000),

    tip TEXT NOT NULL
        CHECK(length(trim(tip)) BETWEEN 5 AND 400),

    shortlisted INTEGER NOT NULL DEFAULT 0
        CHECK(shortlisted IN (0, 1))
);
CREATE TABLE IF NOT EXISTS app_metadata (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
);