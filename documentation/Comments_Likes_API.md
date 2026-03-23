# Comments and Likes API Documentation

## Comments API

### GET /api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/comments/

**Access:** local, remote

**When:** Use this to get a paginated list of all comments on a specific entry.

**How:** Send a GET request with the author's serial and the entry's serial.

**Why:** Allows users to see what others have said about an entry.

**Authentication:** Required for private and unlisted entries. Public entries can be accessed without authentication.

**Example Request**
```
GET /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/comments/
```

**Example Response**
```json
{
    "type": "comments",
    "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/comments/",
    "page_number": 1,
    "size": 5,
    "count": 2,
    "src": [
        {
            "type": "comment",
            "author": {
                "type": "author",
                "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
                "host": "http://127.0.0.1:8000/api/",
                "displayName": "madelaine",
                "github": "https://github.com/madelainedalangin",
                "profileImage": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSyqXzlelYVbGPw3dMKLOmqDwMLaOLe7Q-KRg&s",
                "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
                "description": ""
            },
            "comment": "TEST",
            "contentType": "text/plain",
            "published": "2026-03-16T01:17:22.738223-06:00",
            "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/85047bab-3ccc-40f4-b190-903f2186a9bf",
            "entry": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
            "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
            "likes": {
                "type": "likes",
                "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/85047bab-3ccc-40f4-b190-903f2186a9bf/likes",
                "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/",
                "page_number": 1,
                "size": 0,
                "count": 0,
                "src": []
            }
        },
        {
            "type": "comment",
            "author": {
                "type": "author",
                "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
                "host": "http://127.0.0.1:8000/api/",
                "displayName": "madelaine",
                "github": "https://github.com/madelainedalangin",
                "profileImage": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSyqXzlelYVbGPw3dMKLOmqDwMLaOLe7Q-KRg&s",
                "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
                "description": ""
            },
            "comment": "another one",
            "contentType": "text/plain",
            "published": "2026-03-16T01:18:52.508757-06:00",
            "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/1ff90034-3fa6-42c9-968e-fb04f112cbbd",
            "entry": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
            "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
            "likes": {
                "type": "likes",
                "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/1ff90034-3fa6-42c9-968e-fb04f112cbbd/likes",
                "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/",
                "page_number": 1,
                "size": 0,
                "count": 0,
                "src": []
            }
        }
    ]
}
```

**Response Fields**
- `type` (string): Always "comments"
- `web` (string): Frontend URL of the entry
- `id` (string): API URL of the comments endpoint
- `page_number` (integer): Current page number
- `size` (integer): Number of comments per page (default: 5)
- `count` (integer): Total number of comments
- `src` (array): List of comment objects

**Visibility Rules**
- `PUBLIC` entries: anyone can view comments
- `UNLISTED` entries: only followers can view comments
- `PRIVATE` entries: only friends (mutual followers) can view comments
- `DELETED` entries: returns 410

---

### GET /api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/comments/{COMMENT_FQID}/

**Access:** local, remote

**When:** Use this to get a single specific comment on an entry, identified by the comment's percent-encoded FQID.

**How:** Send a GET request with the entry author's serial, the entry's serial, and the comment's percent-encoded FQID.

**Why:** Allows remote nodes to retrieve a specific comment scoped under the entry's URL path, as required by the spec.

**Authentication:** Required for comments on private/unlisted entries.

**Additional Notes**
- The comment FQID must be percent-encoded in the URL.
- This routes to the same logic as `GET /api/commented/{COMMENT_FQID}/` but is scoped under the entry path for remote node compatibility.

**Example Request**
```
GET /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/comments/http%3A%2F%2F127.0.0.1%3A8000%2Fapi%2Fauthors%2F4bad05f0-481d-4b77-b601-2ea2c7cde423%2Fcommented%2F85047bab-3ccc-40f4-b190-903f2186a9bf/
```

**Example Response**
```json
{
    "type": "comment",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
        "host": "http://127.0.0.1:8000/api/",
        "displayName": "Madelaine",
        "github": null,
        "profileImage": null
    },
    "comment": "TEST",
    "contentType": "text/plain",
    "published": "2026-03-16T01:17:22.738223-06:00",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/85047bab-3ccc-40f4-b190-903f2186a9bf",
    "entry": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
    "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
}
```

**Error Responses**
- `403 Forbidden`: Entry is private and user is not a friend
- `404 Not Found`: Comment or entry does not exist
- `410 Gone`: Entry has been deleted

---

### GET /api/entries/{ENTRY_FQID}/comments/

**Access:** local, remote

**When:** Use this to get comments on an entry using the entry's full FQID.

**How:** Send a GET request with the entry's percent-encoded FQID.

**Why:** Allows remote nodes to retrieve comments using the entry's full URL identifier.

**Authentication:** Required for private and unlisted entries.

**Example Request**
```
GET /api/entries/http%3A%2F%2F127.0.0.1%3A8000%2Fapi%2Fauthors%2F4bad05f0-481d-4b77-b601-2ea2c7cde423%2Fentries%2F1546e0a2-8293-43b1-b78f-e2258dbb8e7d/comments/
```

**Example Response**
```json
{
    "type": "comments",
    "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/comments/",
    "page_number": 1,
    "size": 5,
    "count": 1,
    "src": [
        {
            "type": "comment",
            "author": { "..." : "..." },
            "comment": "Thanks for sharing!",
            "contentType": "text/plain",
            "published": "2026-03-15T21:00:00+00:00",
            "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/def67890-0000-0000-0000-000000000001",
            "entry": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
            "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
        }
    ]
}
```

---

### GET /api/authors/{AUTHOR_SERIAL}/commented/

**Access:** local, remote

**When:** Use this to get all comments made by a specific author.

**How:** Send a GET request with the author's serial.

**Why:** Allows retrieval of everything an author has commented on.

**Authentication:** Required. Remote nodes only receive comments on PUBLIC and UNLISTED entries.

**Example Request**
```
GET /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/
```

**Example Response**
```json
{
    "type": "comments",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/",
    "page_number": 1,
    "size": 5,
    "count": 1,
    "src": [
        {
            "type": "comment",
            "author": {
                "type": "author",
                "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
                "host": "http://127.0.0.1:8000/api/",
                "displayName": "Madelaine",
                "github": null,
                "profileImage": null
            },
            "comment": "I totally agree with you!",
            "contentType": "text/plain",
            "published": "2026-03-15T21:00:00+00:00",
            "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/def67890-0000-0000-0000-000000000001",
            "entry": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
            "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
        }
    ]
}
```

---

### POST /api/authors/{AUTHOR_SERIAL}/commented/

**Access:** local only

**When:** Use this to post a new comment on an entry.

**How:** Send a POST request with the entry FQID and comment text.

**Why:** Allows authors to comment on entries they can access.

**Authentication:** Required.

**Example Request**
```
POST /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/
Content-Type: application/json

{
    "entry": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
    "comment": "Great post!"
}
```

**Example Response (201 Created)**
```json
{
    "type": "comment",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
        "host": "http://127.0.0.1:8000/api/",
        "displayName": "Madelaine",
        "github": null,
        "profileImage": null
    },
    "comment": "Yumm can't wait to use this recipe tonight!",
    "contentType": "text/plain",
    "published": "2026-03-15T21:00:00+00:00",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/def67890-0000-0000-0000-000000000001",
    "entry": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
    "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
}
```

**Error Responses**
- `400 Bad Request`: Missing entry or comment field
- `403 Forbidden`: Entry is private and user is not a friend
- `404 Not Found`: Entry does not exist
- `410 Gone`: Entry has been deleted

**Additional Notes**
- After a comment is created, it is automatically forwarded to the entry author's inbox.

---

### GET /api/authors/{AUTHOR_SERIAL}/commented/{COMMENT_SERIAL}/

**Access:** local, remote

**When:** Use this to get a single comment by the author's serial and comment's serial.

**How:** Send a GET request with the comment author's serial and the comment's serial.

**Why:** Allows retrieval of a specific comment.

**Authentication:** Required for comments on private/unlisted entries.

**Example Request**
```
GET /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/def67890-0000-0000-0000-000000000001/
```

**Example Response**
```json
{
    "type": "comment",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
        "host": "http://127.0.0.1:8000/api/",
        "displayName": "Madelaine",
        "github": null,
        "profileImage": null
    },
    "comment": "this is awesome!",
    "contentType": "text/plain",
    "published": "2026-03-15T21:00:00+00:00",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/def67890-0000-0000-0000-000000000001",
    "entry": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
    "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
}
```

---

### GET /api/commented/{COMMENT_FQID}/

**Access:** local, remote

**When:** Use this to get a single comment by its full FQID.

**How:** Send a GET request with the comment's percent-encoded FQID.

**Why:** Allows retrieval of a specific comment using its full URL.

**Authentication:** Required for comments on private/unlisted entries.

**Example Request**
```
GET /api/commented/http%3A%2F%2F127.0.0.1%3A8000%2Fapi%2Fauthors%2Fabc12345%2Fcommented%2Fdef67890/
```

**Example Response**
```json
{
    "type": "comment",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
        "host": "http://127.0.0.1:8000/api/",
        "displayName": "Madelaine",
        "github": null,
        "profileImage": null
    },
    "comment": "you got this!",
    "contentType": "text/plain",
    "published": "2026-03-15T21:00:00+00:00",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/commented/def67890-0000-0000-0000-000000000001",
    "entry": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d",
    "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
}
```

---

## Likes API

### GET /api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/likes/

**Access:** local, remote

**When:** Use this to get all likes on a specific entry.

**How:** Send a GET request with the author's serial and entry's serial.

**Why:** Allows users to see how many people liked an entry.

**Authentication:** Required for private/unlisted entries.

**Example Request**
```
GET /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/likes/
```

**Example Response**
```json
{
    "type": "likes",
    "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/likes/",
    "page_number": 1,
    "size": 5,
    "count": 1,
    "src": [
        {
            "type": "like",
            "author": {
                "type": "author",
                "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
                "host": "http://127.0.0.1:8000/api/",
                "displayName": "Madelaine",
                "github": null,
                "profileImage": null
            },
            "published": "2026-03-15T21:00:00+00:00",
            "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/liked/ghi11111-0000-0000-0000-000000000001",
            "object": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
        }
    ],
    "user_liked": false
}
```

**Response Fields**
- `type` (string): Always "likes"
- `web` (string): Frontend URL of the entry
- `id` (string): API URL of the likes endpoint
- `page_number` (integer): Current page number
- `size` (integer): Number of likes per page (default: 5)
- `count` (integer): Total number of likes
- `src` (array): List of like objects
- `user_liked` (boolean): Whether the currently authenticated user has liked this entry
  - Example: `false`

**Visibility Rules**
- `PUBLIC` entries: anyone can view likes
- `UNLISTED` entries: only followers can view likes
- `PRIVATE` entries: only friends (mutual followers) can view likes
- `DELETED` entries: returns 410

---

### GET /api/entries/{ENTRY_FQID}/likes/

**Access:** local only

**When:** Use this to get all likes on an entry using the entry's full FQID.

**How:** Send a GET request with the entry's percent-encoded FQID.

**Why:** Allows retrieval of likes using the entry's full URL identifier.

**Authentication:** Required.

**Example Request**
```
GET /api/entries/http%3A%2F%2F127.0.0.1%3A8000%2Fapi%2Fauthors%2F4bad05f0-481d-4b77-b601-2ea2c7cde423%2Fentries%2F1546e0a2-8293-43b1-b78f-e2258dbb8e7d/likes/
```

**Example Response**
```json
{
    "type": "likes",
    "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/likes/",
    "page_number": 1,
    "size": 5,
    "count": 0,
    "src": []
}
```

---

### GET /api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/comments/{COMMENT_FQID}/likes/

**Access:** local, remote

**When:** Use this to get all likes on a specific comment.

**How:** Send a GET request with the author's serial, entry's serial, and comment's percent-encoded FQID.

**Why:** Allows users to see how many people liked a comment.

**Authentication:** Required for comments on private/unlisted entries.

**Example Request**
```
GET /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/comments/def67890-0000-0000-0000-000000000001/likes/
```

**Example Response**
```json
{
    "type": "likes",
    "web": "http://127.0.0.1:8000/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/comments/def67890-0000-0000-0000-000000000001/",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d/comments/def67890-0000-0000-0000-000000000001/likes/",
    "page_number": 1,
    "size": 5,
    "count": 0,
    "src": []
}
```

---

### GET /api/authors/{AUTHOR_SERIAL}/liked/

**Access:** local, remote

**When:** Use this to get all likes made by a specific author.

**How:** Send a GET request with the author's serial or FQID.

**Why:** Allows retrieval of everything an author has liked.

**Authentication:** Required.

**Example Request**
```
GET /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/liked/
```

**Example Response**
```json
{
    "type": "likes",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/liked/",
    "page_number": 1,
    "size": 5,
    "count": 1,
    "src": [
        {
            "type": "like",
            "author": {
                "type": "author",
                "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
                "host": "http://127.0.0.1:8000/api/",
                "displayName": "Madelaine",
                "github": null,
                "profileImage": null
            },
            "published": "2026-03-15T21:00:00+00:00",
            "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/liked/ghi11111-0000-0000-0000-000000000001",
            "object": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
        }
    ]
}
```

---

### POST /api/authors/{AUTHOR_SERIAL}/liked/

**Access:** local, remote

**When:** Use this to like an entry or comment.

**How:** Send a POST request with the FQID of the entry or comment to like.

**Why:** Allows authors to express appreciation for entries and comments.

**Authentication:** Required.

**Example Request**
```
POST /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/liked/
Content-Type: application/json

{
    "object": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
}
```

**Example Response (201 Created)**
```json
{
    "type": "like",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
        "host": "http://127.0.0.1:8000/api/",
        "displayName": "Madelaine",
        "github": null,
        "profileImage": null
    },
    "published": "2026-03-15T21:00:00+00:00",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/liked/ghi11111-0000-0000-0000-000000000001",
    "object": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
}
```

**Error Responses**
- `400 Bad Request`: Missing object field, or already liked
- `404 Not Found`: Author does not exist

**Additional Notes**
- After a like is created, it is automatically forwarded to the inbox of the entry or comment author.
- Liking the same object twice returns 400.

---

### DELETE /api/authors/{AUTHOR_SERIAL}/liked/

**Access:** local only

> **Note:** This endpoint is a custom extension not defined in the project spec. It is provided for a better user experience.

**When:** Use this to unlike an entry or comment.

**How:** Send a DELETE request with the FQID of the entry or comment to unlike.

**Why:** Allows authors to remove their like from an entry or comment.

**Authentication:** Required.

**Example Request**
```
DELETE /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/liked/
Content-Type: application/json

{
    "object": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
}
```

**Example Response (204 No Content)**
```json
{
    "detail": "Like successfully deleted"
}
```

**Error Responses**
- `404 Not Found`: Like does not exist

---

### GET /api/authors/{AUTHOR_SERIAL}/liked/{LIKE_SERIAL}/

**Access:** local, remote

**When:** Use this to get a single like by its serial.

**How:** Send a GET request with the author's serial and like's serial.

**Why:** Allows retrieval of a specific like object.

**Example Request**
```
GET /api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/liked/ghi11111-0000-0000-0000-000000000001/
```

**Example Response**
```json
{
    "type": "like",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423",
        "host": "http://127.0.0.1:8000/api/",
        "displayName": "Madelaine",
        "github": null,
        "profileImage": null
    },
    "published": "2026-03-15T21:00:00+00:00",
    "id": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/liked/ghi11111-0000-0000-0000-000000000001",
    "object": "http://127.0.0.1:8000/api/authors/4bad05f0-481d-4b77-b601-2ea2c7cde423/entries/1546e0a2-8293-43b1-b78f-e2258dbb8e7d"
}
```

---

### GET /api/liked/{LIKE_FQID}/

**Access:** local only

**When:** Use this to get a single like by its FQID.

**How:** Send a GET request with the like's percent-encoded FQID.

**Why:** Allows retrieval of a specific like using its full URL.

**Example Request**
```
GET /api/liked/http%3A%2F%2F127.0.0.1%3A8000%2Fapi%2Fauthors%2Fabc12345%2Fliked%2Fghi11111/
```