DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS recipe;
DROP TABLE IF EXISTS ingredient;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    password VARCHAR UNIQUE NOT NULL
    );

CREATE TABLE recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    rcp_ingredients VARCHAR NOT NULL,
    text TEXT NOT NULL,
    r_sum INTEGER,
    r_count INTEGER,
    rating INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
    );

CREATE TABLE ingredient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL
    );

CREATE TABLE recipe_ingredient (
--    recipe_id INTEGER REFERENCES recipe,
--    ingredient_id INTEGER REFERENCES ingredient
    recipe_id INTEGER,
    ingredient_id INTEGER,
    PRIMARY KEY(recipe_id, ingredient_id)
    );
