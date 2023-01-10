DROP TABLE IF EXISTS "post_like";
DROP TABLE IF EXISTS "tags";
DROP TABLE IF EXISTS "post";
DROP TABLE IF EXISTS "user";


CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE "post" (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES "user" (id)
);


CREATE TABLE "post_like" (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(post_id) REFERENCES "post" (id),
    FOREIGN KEY(user_id) REFERENCES "user" (id)
);


CREATE TABLE "tags" (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    tag TEXT,
    FOREIGN KEY(post_id) REFERENCES "post" (id)
);