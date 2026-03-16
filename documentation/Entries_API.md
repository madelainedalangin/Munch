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

#### Request example

```txt
GET /munch/api/authors/d23d571b-deeb-4f2c-99be-f01bba40434b/entries/eed6485b-293d-4fea-9d04-4c0298057ac6/
```

#### Response example

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

---

### URL Pattern
```txt
PUT /munch/api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/
```

### Description
Updates the entry specified by AUTHOR_SERIAL and ENTRY_SERIAL.

### Authentication
Local entries must be authenticated locally as the author

### User Stories:

##### * "As an author, I want to edit my entries locally, so that I'm not stuck with a typo on a popular entry."

#### Request Body Example

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

#### Response Example

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

### User Stories:

##### * "As an author, other authors cannot modify my entries, so that I don't get impersonated."

#### Request Example (From a user different from the author attempting to modify author's entry)
```json
{
    "type": "entry",
    "title": "meow commonmark",
    "id": "http://127.0.0.1:8000/munch/api/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27/entries/c59eb813-7788-4b35-97ff-71e9600f31af",
    "web": "http://127.0.0.1:8000/munch/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27/entries/c59eb813-7788-4b35-97ff-71e9600f31af",
    "description": "this is meow with commonmark",
    "contentType": "text/markdown",
    "content": "This is a photo of a cat\r\n\r\n![cat photo](https://www.cats.org.uk/media/13139/220325case013.jpg)",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/munch/api/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27",
        "host": "http://127.0.0.1:8000/munch/api/",
        "displayName": "x",
        "github": null,
        "profileImage": null,
        "web": "http://127.0.0.1:8000/munch/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27",
        "description": null
    },
    "published": "2026-03-16T01:25:49.444686-06:00",
    "visibility": "PUBLIC"
}
```

#### Response Example
```json
HTTP 403 Forbidden
{
    "detail": "Only the author can update this entry."
}
```

---

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

#### Response Example

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

---

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

#### Request example

```text
GET /munch/api/authors/37a31c59-e1b4-4573-a82f-f7c763602229/entries/
```

#### Response example

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

### User Stories:

##### * "As an author, I want to make entries, so I can share my thoughts and pictures with other local authors."
##### * "As an author, I want to make entries, so I can share my thoughts and pictures with other local authors."

#### Request Body example (content type is plain text)

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

#### Response example

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

### User Stories:
##### * "As an author, entries I make can be in CommonMark, so I can give my entries some basic formatting."


#### Request Body example (content type is markdown)

```json
{
    "type": "entry",
    "title": "Markdown",
    "id": "http://127.0.0.1:8000/munch/api/authors/19c3fc3c-9d91-4c5b-a2bd-c20c6fe85923/entries/f1f1f31c-e6ee-4dc6-9590-82aaeb2a5062",
    "web": "http://127.0.0.1:8000/munch/authors/19c3fc3c-9d91-4c5b-a2bd-c20c6fe85923/entries/f1f1f31c-e6ee-4dc6-9590-82aaeb2a5062",
    "description": "This will be in markdown",
    "contentType": "text/markdown",
    "content": "# Entry Title\r\n\r\nThis is a normal paragraph introducing the topic.\r\n\r\n## Important Note\r\n\r\nThis sentence has **bold text** for emphasis.\r\n\r\nThis sentence has *italic text* for lighter emphasis.\r\n\r\nThis sentence has ***bold and italic*** text.\r\n\r\nYou can also include `inline code` for technical terms.\r\n\r\n- First point\r\n- Second point\r\n- Third point\r\n\r\n> This is a blockquote for highlighted commentary or reflection.",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/munch/api/authors/19c3fc3c-9d91-4c5b-a2bd-c20c6fe85923",
        "host": "http://127.0.0.1:8000/munch/api/",
        "displayName": "x",
        "github": null,
        "profileImage": null,
        "web": "http://127.0.0.1:8000/munch/authors/19c3fc3c-9d91-4c5b-a2bd-c20c6fe85923",
        "description": null
    },
    "published": "2026-03-16T00:08:09.343261-06:00",
    "visibility": "PUBLIC"
}
```

#### Response example

```json
HTTP 201 Created
{
    "type": "entry",
    "title": "Markdown",
    "id": "http://127.0.0.1:8000/munch/api/authors/19c3fc3c-9d91-4c5b-a2bd-c20c6fe85923/entries/f1f1f31c-e6ee-4dc6-9590-82aaeb2a5062",
    "web": "http://127.0.0.1:8000/munch/authors/19c3fc3c-9d91-4c5b-a2bd-c20c6fe85923/entries/f1f1f31c-e6ee-4dc6-9590-82aaeb2a5062",
    "description": "This will be in markdown",
    "contentType": "text/markdown",
    "content": "# Entry Title\r\n\r\nThis is a normal paragraph introducing the topic.\r\n\r\n## Important Note\r\n\r\nThis sentence has **bold text** for emphasis.\r\n\r\nThis sentence has *italic text* for lighter emphasis.\r\n\r\nThis sentence has ***bold and italic*** text.\r\n\r\nYou can also include `inline code` for technical terms.\r\n\r\n- First point\r\n- Second point\r\n- Third point\r\n\r\n> This is a blockquote for highlighted commentary or reflection.",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/munch/api/authors/19c3fc3c-9d91-4c5b-a2bd-c20c6fe85923",
        "host": "http://127.0.0.1:8000/munch/api/",
        "displayName": "x",
        "github": null,
        "profileImage": null,
        "web": "http://127.0.0.1:8000/munch/authors/19c3fc3c-9d91-4c5b-a2bd-c20c6fe85923",
        "description": null
    },
    "published": "2026-03-16T00:08:09.343261-06:00",
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

---

# Image Entries

## Get Image by Serial

### URL Pattern
```text
GET /munch/api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/image/
```

### Description
Obtain the selected image entry converted to binary. On success, returns the binary image file. Returns 404 if it is not an image

### User Stories: 
#### * "As an author, entries I create can be images, so that I can share pictures and drawings."*

#### Request Example
``` text
GET /munch/api/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27/entries/03b36db2-983f-4b47-837c-91a7e3f2c88d/image/
```

#### Response Example (Success)
```json
HTTP 200 OK
Content-Type: image/png
(binary image data)
```

---

## Get Image by FQID

### URL Pattern
```text
GET /munch/api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/image/
```

### Description
Obtain the selected image entry converted to binary. On success, returns the binary image file. Returns 404 if it is not an image

### User Stories: 
#### * "As an author, entries I create can be images, so that I can share pictures and drawings."*

#### Request Example
``` text
GET munch/api/entries/{ENTRY_FQID}/image/
```

#### Response Example
```json
HTTP 200 OK
Content-Type: image/png
(binary image data)
```

#### Response Example (Not Found)
```json
HTTP 404 Not Found
{
    "detail": "No Entry matches the given query."
}
```


### User Stories: 
#### * "As an author, entries I create that are in CommonMark can link to images, so that I can illustrate my entries."*

#### Request Body Example
```json
{
    "type": "entry",
    "title": "meow commonmark",
    "id": "http://127.0.0.1:8000/munch/api/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27/entries/7f23dfe1-b148-4f5e-9270-8f297655ed9c",
    "web": "http://127.0.0.1:8000/munch/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27/entries/7f23dfe1-b148-4f5e-9270-8f297655ed9c",
    "description": "this is meow with commonmark",
    "contentType": "text/markdown",
    "content": "This is a photo of a cat\r\n\r\n![cat photo](https://www.cats.org.uk/media/13139/220325case013.jpg)",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/munch/api/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27",
        "host": "http://127.0.0.1:8000/munch/api/",
        "displayName": "x",
        "github": null,
        "profileImage": null,
        "web": "http://127.0.0.1:8000/munch/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27",
        "description": null
    },
    "published": "2026-03-16T01:25:49.444686-06:00",
    "visibility": "PUBLIC"
}
```

#### Response Example (UI will display the image based on the link)
```json
HTTP 201 Created
{
    "type": "entry",
    "title": "meow commonmark",
    "id": "http://127.0.0.1:8000/munch/api/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27/entries/7f23dfe1-b148-4f5e-9270-8f297655ed9c",
    "web": "http://127.0.0.1:8000/munch/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27/entries/7f23dfe1-b148-4f5e-9270-8f297655ed9c",
    "description": "this is meow with commonmark",
    "contentType": "text/markdown",
    "content": "This is a photo of a cat\r\n\r\n![cat photo](https://www.cats.org.uk/media/13139/220325case013.jpg)",
    "author": {
        "type": "author",
        "id": "http://127.0.0.1:8000/munch/api/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27",
        "host": "http://127.0.0.1:8000/munch/api/",
        "displayName": "x",
        "github": null,
        "profileImage": null,
        "web": "http://127.0.0.1:8000/munch/authors/a1ca231c-42b4-4ebb-8a9e-a1f86da6ae27",
        "description": null
    },
    "published": "2026-03-16T01:25:49.444686-06:00",
    "visibility": "PUBLIC"
}
```

## Response Fields

This endpoint does not return a JSON entry object on success.

- `Content-Type` (string): The MIME type of the image, such as image/png or image/jpeg

## Visibility Rules

- `PUBLIC` image entries from anyone on the node appear. 
- `UNLISTED` image entries appear only from authors you follow. 
- `PRIVATE` image entries appear only from mutual follows (friends). 
- Your own entries always appear, except for the deleted ones. 
- `DELETED` image entries never appear. 


















