import requests
from django.utils.dateparse import parse_datetime
from .models import Author, Entry

def sync_github_activity(author):
    if not author.github: 
        return
    
    # Extract username safely
    username = author.github.strip("/").split("/")[-1]
    response = requests.get(f"https://api.github.com/users/{username}/events/public")
    
    if response.status_code == 200:
        events = response.json()
        for event in events[:10]: # Increased to 10 for better coverage
            # Convert GitHub's ISO string to a Django-friendly datetime object
            event_date = parse_datetime(event.get('created_at'))
            
            # Use github_id as the unique key to prevent duplicates
            obj, created = Entry.objects.get_or_create(
                github_id=event['id'],
                defaults={
                    'author': author,
                    'title': f"GitHub {event['type'].replace('Event', '')}",
                    'content': f"Activity in {event['repo']['name']}",
                    'visibility': 'PUBLIC',
                    'contentType': 'text/plain',
                    'published': event_date  # Critical for correct timeline!
                }
            )