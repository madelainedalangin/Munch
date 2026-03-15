# ENTRIES API
## Entry by Author and Serial


### URL Pattern
```txt
GET /munch/api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/
```

### Description
Queries an entry using AUTHOR_SERIAL and ENTRY_SERIAL. Returns the selected entry. 

### Authentication
Required for friends-only entries. Local entries must be authenticated locally as the author

### Example

Request

```txt
GET /munch/api/authors/d23d571b-deeb-4f2c-99be-f01bba40434b/entries/eed6485b-293d-4fea-9d04-4c0298057ac6/
```

Response

```json
{
  "type":"entry",
  "title":"asdf",
  "id":"http://127.0.0.1:8000/munch/api/munch/api/authors/d23d571b-deeb-4f2c-99be-f01bba40434b/entries/eed6485b-293d-4fea-9d04-4c0298057ac6",
  "web":"http://127.0.0.1:8000/munch/api/munch/api/authors/d23d571b-deeb-4f2c-99be-f01bba40434b/entries/eed6485b-293d-4fea-9d04-4c0298057ac6",
  "description":"asdf",
  "contentType":"text/plain",
  "content":"asdf",
  "author":{"type":"author",
  "id":"http://127.0.0.1:8000/munch/api/authors/d23d571b-deeb-4f2c-99be-f01bba40434b",
  "host":"http://127.0.0.1:8000/munch/api/",
  "displayName":"a","github":null,
  "profileImage":null,
  "web":"http://127.0.0.1:8000/munch/authors/d23d571b-deeb-4f2c-99be-f01bba40434b"},
  "published":"2026-03-02T22:09:48.859808Z","visibility":"PUBLIC"}
```

### URL Pattern
```txt
DELETE /munch/api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/
```

### Description
Deletes the entry specified by AUTHOR_SERIAL and ENTRY_SERIAL. Updates the entry's display status to be DELETED.

### Authentication
Local entries must be authenticated locally as the author

### Example 

Request

```txt
DELETE /munch/api/authors/d23d571b-deeb-4f2c-99be-f01bba40434b/entries/741c4503-2e58-439c-b798-8ca3f0e97029/
```

Response

```json
{
    "detail": "Entry already deleted."
}  
```

### URL Pattern
```txt
PUT /munch/api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/
```

### Description
Updates the entry specified by AUTHOR_SERIAL and ENTRY_SERIAL.

### Authentication
Local entries must be authenticated locally as the author

### Example 

Request Body

```json
  {
      "type": "entry",
      "title": "asdfwa",
      "id": "http://127.0.0.1:8000/munch/api/munch/api/authors/84fccb0b-014f-4e30-978b-e95ad701971b/entries/7f545991-d2e9-4b21-bd79-adc6a0d399e1",
      "web": "http://127.0.0.1:8000/munch/api/munch/api/authors/84fccb0b-014f-4e30-978b-e95ad701971b/entries/7f545991-d2e9-4b21-bd79-adc6a0d399e1",
      "description": "asdfwe",
      "contentType": "text/plain",
      "content": "i am menace",
      "author": {
          "type": "author",
          "id": "http://127.0.0.1:8000/munch/api/authors/84fccb0b-014f-4e30-978b-e95ad701971b",
          "host": "http://127.0.0.1:8000/munch/api/",
          "displayName": "a",
          "github": null,
          "profileImage": null,
          "web": "http://127.0.0.1:8000/munch/authors/84fccb0b-014f-4e30-978b-e95ad701971b"
      },
      "published": "2026-03-02T22:39:25.013095Z",
      "visibility": "PUBLIC"
  }
```

Response

```json
 {
      "type": "entry",
      "title": "asdfwa",
      "id": "http://127.0.0.1:8000/munch/api/munch/api/authors/84fccb0b-014f-4e30-978b-e95ad701971b/entries/7f545991-d2e9-4b21-bd79-adc6a0d399e1",
      "web": "http://127.0.0.1:8000/munch/api/munch/api/authors/84fccb0b-014f-4e30-978b-e95ad701971b/entries/7f545991-d2e9-4b21-bd79-adc6a0d399e1",
      "description": "asdfwe",
      "contentType": "text/plain",
      "content": "i am menace",
      "author": {
          "type": "author",
          "id": "http://127.0.0.1:8000/munch/api/authors/84fccb0b-014f-4e30-978b-e95ad701971b",
          "host": "http://127.0.0.1:8000/munch/api/",
          "displayName": "a",
          "github": null,
          "profileImage": null,
          "web": "http://127.0.0.1:8000/munch/authors/84fccb0b-014f-4e30-978b-e95ad701971b"
      },
      "published": "2026-03-02T22:39:25.013095Z",
      "visibility": "PUBLIC"
  }
```
Note: that response matches the post request, meaning that the entry was updated with the request body 

## Entry by FQID

### URL Pattern
```text
GET munch/api/entries/{ENTRY_FQID}
```

### Description
Queries the entry specified by the Fully Qualified ID (FQID). Returns the selected entry.

### Authentication
Friends-only entries must be authenticated

### Example

Request

```text
GET /munch/api/entries/http://127.0.0.1:8000/munch/api/authors/32066895-122c-4d93-ad89-f754feaa4c66/entries/08884bf9-1c39-4977-b555-622927ced8eb/
```

Response

```json
HTTP 200 OK
{
    "type": "entry",
    "title": "afawfa",
    "id": "http://127.0.0.1:8000/munch/api/munch/api/authors/32066895-122c-4d93-ad89-f754feaa4c66/entries/08884bf9-1c39-4977-b555-622927ced8eb",
    "web": "http://127.0.0.1:8000/munch/api/munch/api/authors/32066895-122c-4d93-ad89-f754feaa4c66/entries/08884bf9-1c39-4977-b555-622927ced8eb",
    "description": "awefsfa",
    "contentType": "text/plain",
    "content": "weafweaff",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/munch/api/authors/32066895-122c-4d93-ad89-f754feaa4c66",
        "host": "http://127.0.0.1:8000/munch/api/",
        "displayName": "X",
        "github": null,
        "profileImage": null,
        "web": "http://127.0.0.1:8000/munch/authors/32066895-122c-4d93-ad89-f754feaa4c66",
        "description": ""
    },
    "published": "2026-03-15T05:26:54.641540Z",
    "visibility": "PUBLIC"
}
```

## Entry Creation
### URL Pattern
```
GET /munch/api/authors/{AUTHOR_SERIAL}/entries/
```
### Description
Obtains 5 most recent entries made by {AUTHOR_SERIAL} (paginated)

### Authentication
All entries must be authenticated locally as author or as a friend of author.
Public + unlisted entries must be authenticated locally as follower of author

### Example

Request

```text
GET /munch/api/authors/37a31c59-e1b4-4573-a82f-f7c763602229/entries/
```

Response

```json
HTTP 200 OK
[
    {
        "type": "entry",
        "title": "First Entry",
        "id": "http://127.0.0.1:8000/munch/api/authors/37a31c59-e1b4-4573-a82f-f7c763602229/entries/629d9077-e147-409b-ac0a-15c31c5f6320",
        "web": "http://127.0.0.1:8000/munch/authors/37a31c59-e1b4-4573-a82f-f7c763602229/entries/629d9077-e147-409b-ac0a-15c31c5f6320",
        "description": "First of Firsts",
        "contentType": "text/plain",
        "content": "This is the first entry",
        "author": {
            "type": "author",
            "id": "http://127.0.0.1:8000/munch/api/authors/37a31c59-e1b4-4573-a82f-f7c763602229",
            "host": "http://127.0.0.1:8000/munch/api/",
            "displayName": "X",
            "github": null,
            "profileImage": null,
            "web": "http://127.0.0.1:8000/munch/authors/37a31c59-e1b4-4573-a82f-f7c763602229",
            "description": null
        },
        "published": "2026-03-15T06:15:45.820660Z",
        "visibility": "PUBLIC"
    },
    {
        "type": "entry",
        "title": "Second Entry",
        "id": "http://127.0.0.1:8000/munch/api/authors/37a31c59-e1b4-4573-a82f-f7c763602229/entries/c082b4bf-f541-4b25-b021-e6cc0bda289b",
        "web": "http://127.0.0.1:8000/munch/authors/37a31c59-e1b4-4573-a82f-f7c763602229/entries/c082b4bf-f541-4b25-b021-e6cc0bda289b",
        "description": "Second after the first",
        "contentType": "text/plain",
        "content": "This is the second entry",
        "author": {
            "type": "author",
            "id": "http://127.0.0.1:8000/munch/api/authors/37a31c59-e1b4-4573-a82f-f7c763602229",
            "host": "http://127.0.0.1:8000/munch/api/",
            "displayName": "X",
            "github": null,
            "profileImage": null,
            "web": "http://127.0.0.1:8000/munch/authors/37a31c59-e1b4-4573-a82f-f7c763602229",
            "description": null
        },
        "published": "2026-03-15T06:15:45.820660Z",
        "visibility": "PUBLIC"
    }
]
```

### URL Pattern
```
POST /munch/api/authors/{AUTHOR_SERIAL}/entries/
```

### Description
Creates an entry under AUTHOR_SERIAL

### Authentication
Must be authenticated locally as the author


### Example

Request Body 

```json
{
    "type": "entry",
    "title": "Second Entry",
    "id": "http://127.0.0.1:8000/munch/api/authors/37a31c59-e1b4-4573-a82f-f7c763602229/entries/c082b4bf-f541-4b25-b021-e6cc0bda289b",
    "web": "http://127.0.0.1:8000/munch/authors/37a31c59-e1b4-4573-a82f-f7c763602229/entries/c082b4bf-f541-4b25-b021-e6cc0bda289b",
    "description": "Second after the first",
    "contentType": "text/plain",
    "content": "This is the second entry",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/munch/api/authors/37a31c59-e1b4-4573-a82f-f7c763602229",
        "host": "http://127.0.0.1:8000/munch/api/",
        "displayName": "X",
        "github": null,
        "profileImage": null,
        "web": "http://127.0.0.1:8000/munch/authors/37a31c59-e1b4-4573-a82f-f7c763602229",
        "description": null
    },
    "published": "2026-03-15T06:15:45.820660Z",
    "visibility": "PUBLIC"
}
```

Response

```json
HTTP 201 Created
{
    "type": "entry",
    "title": "Second Entry",
    "id": "http://127.0.0.1:8000/munch/api/authors/37a31c59-e1b4-4573-a82f-f7c763602229/entries/c082b4bf-f541-4b25-b021-e6cc0bda289b",
    "web": "http://127.0.0.1:8000/munch/authors/37a31c59-e1b4-4573-a82f-f7c763602229/entries/c082b4bf-f541-4b25-b021-e6cc0bda289b",
    "description": "Second after the first",
    "contentType": "text/plain",
    "content": "This is the second entry",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/munch/api/authors/37a31c59-e1b4-4573-a82f-f7c763602229",
        "host": "http://127.0.0.1:8000/munch/api/",
        "displayName": "X",
        "github": null,
        "profileImage": null,
        "web": "http://127.0.0.1:8000/munch/authors/37a31c59-e1b4-4573-a82f-f7c763602229",
        "description": null
    },
    "published": "2026-03-15T06:15:45.820660Z",
    "visibility": "PUBLIC"
}
```

## Response Fields

- `type` (string): Always "entry"
- `title` (string): Title of the entry
- `id` (string): Full URL of the entry
- `description` (string): Brief summary of the entry
- `contentType` (string): "text/plain" or "text/markdown"
- `content` (string): The actual entry body
- `author` (object): The author who wrote it
- `published` (string): ISO 8601 timestamp
- `visibility` (string): PUBLIC, FRIENDS, or UNLISTED

## Visibility Rules

- `PUBLIC` entries from anyone on the node appear. 
- `UNLISTED` entries appear only from authors you follow. 
- `PRIVATE` entries appear only from mutual follows (friends). 
- Your own entries always appear except for the deleted ones. 
- `DELETED` entries never appear. 



