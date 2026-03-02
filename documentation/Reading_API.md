# STREAM API

## GET /munch/api/stream

**When:** Use this so that as a user, one can see their homefeed personalized to them based on their entries, friends' entries and public entries.  
**How:** Send a GET request while logged in.  
**Why**: This is the primary method to see all entries a user should know.  
**Authentication:** Required. Or else, it will redirect to login if a person is not logged in.  

## Example Request

```txt
GET /munch/api/stream/
```

## Example Response

```json
[
    {
      "type": "entry",
      "title": "Hello Munch!",
      "id": "http://127.0.0.1:8000/munch/api/authors/5eb62157-1cbe-4bfc-a8d4-f4b3233bc93e/entries/5b072938-c424-43a2-8df9-4c71dcb6af4a",
      "description": "greeting entry",
      "contentType": "text/plain",
      "content": "Hello! Can't wait to meet new people :)",
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
  - Example: "entry"
- `title` (string): Title of the entry 
  - Example: "Looking for the best Donair Pizza in the city"
- `id` (string): Full URL of the entry  
  - Example: "http://127.0.0.1:8000/munch/api/authors/5eb62157-1cbe-4bfc-a8d4-f4b3233bc93e/entries/5b072938-c424-43a2-8df9-4c71dcb6af4a"
- `description` (string): Brief summary of the entry  
  - Example: "Question / Recommendations"
- `contentType` (string): "text/plain" or "text/markdown"  
  - Example: "text/plain"
- `content` (string): The actual entry body  
  - Example: "Can anyone recommend me the best place to get a Donair pizza around Edmonton south? Thanks"
- `author` (object): The author who wrote it
  - See author fields below
- `published` (string): ISO 8601 timestamp
  - Example: "2026-03-01T09:12:54.769340+00:00"
- `visibility` (string): PUBLIC, FRIENDS, or UNLISTED
  - Example: "PUBLIC" 
 
## Author Fields

- `type` (string): Always "author"
  - Example: "author"
- `id` (string): Full URL of the author
  - Example: "http://127.0.0.1:8000/munch/api/authors/5eb62157-1cbe-4bfc-a8d4-f4b3233bc93e"
- `host` (string): The author's node URL
  - Example: "http://127.0.0.1:8000/"
- `displayName` (string): The author's display name
  - Example: "Madelaine"
- `github` (string or null): URL to the author's GitHub profile
  - Example: "http://github.com/madelainedalangin"
  - Example: `null`
- `profileImage` (string): URL to the author's profile picture
  - Example: "https://i.redd.it/olgkm4pzx2w31.jpg"

## Visibility Rules

- `PUBLIC` entries from anyone on the node appear. 
- `UNLISTED` entries appear only from authors you follow. 
- `PRIVATE` entries appear only from mutual follows (friends). 
- Your own entries always appear except for the deleted ones. 
- `DELETED` entries never appear. 
- Sorted by newest published date first. 

## Additional Notes
- Authentication is required. Unauthenticated requests redirect to login (302).
- Pagination not yet implemented.
- Sorted by newest published date first.
  - Edited entries after publishing keep their original published date