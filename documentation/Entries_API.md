# ENTRIES API

### GET /munch/api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}

**When:** Use this post, delete, or get an entry 
**How:** Send a GET,POST,DELETE request while logged in.  
**Why**: This is the primary method to manage entries by their serial number 

**Authentication:** Required for friends-only entries. Local entries must be authenticated locally as the author.

### Example GET Request

```txt
GET /munch/api/authors/d23d571b-deeb-4f2c-99be-f01bba40434b/entries/eed6485b-293d-4fea-9d04-4c0298057ac6/
```

### Example Response


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

### Example DELETE Request
```txt
DELETE /munch/api/authors/d23d571b-deeb-4f2c-99be-f01bba40434b/entries/741c4503-2e58-439c-b798-8ca3f0e97029/
```

### Example DELETE Response
```json
{
    "detail": "Entry already deleted."
}  
```

### Example PUT Request

```txt
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

### Example PUT Response

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
Note that response matches with the post request, meaning that the entry was modified. 


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



