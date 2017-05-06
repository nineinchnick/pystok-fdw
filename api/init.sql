CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name CHARACTER VARYING
);

CREATE TABLE groups (
    id INTEGER PRIMARY KEY,
    name CHARACTER VARYING
);

CREATE TABLE group_user (
    user_id INTEGER REFERENCES users(id),
    group_id INTEGER REFERENCES groups(id),
    PRIMARY KEY (user_id, group_id)
);
