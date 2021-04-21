# RPSA

## Locations

**Location**

Attributes:

* title (string)
* latitude (float)
* longitude (float)
* description (string)
* category (string)

## Schema

```sql
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    title TEXT,
    latitude FLOAT,
    longitude FLOAT,
    description TEXT,
    category TEXT);
```

## Users

**User**

Attributes:

* firstname (string)
* lastname (string)
* email (string)
* password (string)

## Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    firstname TEXT,
    lastname TEXT,
    email TEXT,
    password TEXT);
```

## REST Endpoints

Name                           | Method | Path
-------------------------------|--------|------------------
Retrieve location collection | GET    | /locations
Retrieve location member     | GET    | /locations/*\<id\>*
Create location member       | POST   | /locations
Update location member       | PUT    | /locations/*\<id\>*
Delete location member       | DELETE | /locations/*\<id\>*
Retrieve session             | GET    | /sessions
Create session               | POST   | /sessions
Delete session               | DELETE | /sessions
Create user                  | POST   | /users

Used default bcrypt for password hashing.
