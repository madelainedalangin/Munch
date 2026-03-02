# STREAM API

### GET /munch/api/stream

**When:** Use this so that as a user, one can see their homefeed personalized to them based on their entries, friends' entries and public entries.  
**How:** Send a GET request while logged in.  
**Why**: This is the primary method to see all entries a user should know.  
**Authentication:** Required. Or else, it will redirect to login if a person is not logged in.  

### Example Request

```txt
GET /munch/api/stream/
```

## Example Response

```json
[
    {
      "type": "entry",
      "title": "First Entry Ever",
      "id": "http://127.0.0.1:8000/munch/api/authors/5eb62157-1cbe-4bfc-a8d4-f4b3233bc93e/entries/5b072938-c424-43a2-8df9-4c71dcb6af4a",
      "description": "Exciting",
      "contentType": "text/plain",
      "content": ":3",
      "author": {
          "type": "author",
          "id": "http://127.0.0.1:8000/munch/authors/5eb62157-1cbe-4bfc-a8d4-f4b3233bc93e",
          "host": "http://127.0.0.1:8000/",
          "displayName": "Madelaine",
          "github": null,
          "profileImage": "https://i.redd.it/olgkm4pzx2w31.jpg"
      },
      "published": "2026-03-01T09:12:54.769340+00:00",
      "visibility": "PUBLIC"
  }
]
```

## Example Empty Response
```json
[]
```

This is for when there are no entries or all entries are deleted.  

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
- `FRIENDS` entries appear only from mutual follows (friends). 
- Your own entries always appear except for the deleted ones. 
- `DELETED` entries never appear. 
- Sorted by newest published date first. 