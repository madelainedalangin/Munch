import requests
from django.utils.dateparse import parse_datetime
from .models import Author, Entry

# The following function from Google, Gemini, "Sync Github Activity", 03-16-2026
def sync_github_activity(author):
    if not author.github: 
        print("No GitHub URL found.")
        return
    
    username = author.github.strip("/").split("/")[-1]
    api_url = f"https://api.github.com/users/{username}/events/public"
    print(f"Fetching from {api_url}")
    
    response = requests.get(api_url)
    print(f"GitHub Response Status: {response.status_code}")
    
    if response.status_code == 200:
        events = response.json()
        print(f"Found {len(events)} events.")
        
        for event in events[:10]:
            event_date = parse_datetime(event.get('created_at'))
            
            # Using your current get_or_create logic
            obj, created = Entry.objects.get_or_create(
                github_id=event['id'],
                defaults={
                    'author': author,
                    'title': f"GitHub {event['type'].replace('Event', '')}",
                    'content': f"Activity in {event['repo']['name']}",
                    'visibility': 'PUBLIC',
                    'contentType': 'text/plain',
                    'published': event_date,
                    'url': f"https://github.com/{event['repo']['name']}/activity/{event['id']}"
                }
            )
            if created:
                print(f"Created new entry for event {event['id']}")
            else:
                print(f"Event {event['id']} already exists in DB.")
    