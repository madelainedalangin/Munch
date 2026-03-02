# AUTHORS API

### GET /munch/api/authors

**When:** Use this to view the list of registered profiles.  
**How:** Send a GET request to the URL.  
**Why**: This is the primary method to see all profiles.  

### Example Request

```txt
GET /munch/api/authors/
```

## Example Response

```json
[
    {
        "type": "author",
        "id": "http://127.0.0.1:8000/munch/api/authors/fc99ecab-1274-4f58-887a-a61214372763",
        "host": "http://127.0.0.1:8000/munch/api/",
        "displayName": "adminjoshua",
        "github": null,
        "profileImage": null,
        "web": "http://127.0.0.1:8000/munch/authors/fc99ecab-1274-4f58-887a-a61214372763"
    },
    {
        "type": "author",
        "id": "http://127.0.0.1:8000/munch/api/authors/721fe442-a7fc-43b9-b27a-da168b73d395",
        "host": "http://127.0.0.1:8000/munch/api/",
        "displayName": "testerjoshua",
        "github": "https://github.com/testerjoshua",
        "profileImage": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRlVTWL4dqk9ZokaiRQe0kdV3_dNvkB7A3xTw&s",
        "web": "http://127.0.0.1:8000/munch/authors/721fe442-a7fc-43b9-b27a-da168b73d395"
    }
]
```

## Example Empty Response
```json
[]
```

This is for when there are no authors.

## Response Fields

- `type` (string): Always "author"
  - Example: "author"
- `id` (string): Full URL of the author
  - Example: "http://127.0.0.1:8000/munch/api/authors/721fe442-a7fc-43b9-b27a-da168b73d395"
- `host` (string): The server URL where the author is hosted
  - Example: "http://127.0.0.1:8000/munch/api/"
- `displayName` (string): Author's chosen public name
  - Example: "testerjoshua"
- `github` (string or null): Link to author's github profile
  - Example: "[author](https://github.com/testerjoshua)"
  - Example: `null`
- `profileImage` (string or null): URL to author's chosen picture
  - Example: "author"
  - Example: `null`
- `web` (string): URL to author's profile page
  - Example: "http://127.0.0.1:8000/munch/authors/721fe442-a7fc-43b9-b27a-da168b73d395"
