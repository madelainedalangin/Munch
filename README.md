# 🍔 Munch

**A federated social networking platform built for CMPUT 404 (Web Applications and Architecture) at the University of Alberta.**

Munch is a distributed blogging and social networking application inspired by [Diaspora](https://diasporafoundation.org/) and [ActivityPub](https://www.w3.org/TR/activitypub/). Authors on different nodes can follow each other, share entries, comment, and like content across a federated network.

# 🎥 Promotional Video

<p align="center">
  <video src="https://github.com/user-attachments/assets/18e86e0f-c76b-4485-bdfe-7928c8437e59" controls></video>
</p>

## 💡 The Problem

Traditional social media platforms are centralized. Your data, identity, and connections all live on a single server which is also owned by a single company. If that platform goes haywire, you would have no recourse. This design keeps users locked into one service, and there is no way to take your social media use elsewhere.

The web was designed to be interconnected and peer-to-peer. But most social networking today funnels through corporate gatekeeping. There is no technical reason why users on different platforms cannot interact with each other, follow each other, and share content freely across services.

**Munch addresses this by decentralizing the social network.** Each node operates independently with its own server and database, but nodes communicate with each other through a shared protocol. Authors own their identity on their own node while still being able to follow, like, and comment on content hosted anywhere in the network. No single point of failure, no single authority, and no vendor lock-in.

## 👥 Team Whitesmoke

| Name | GitHub |
|------|--------|
| Madelaine Dalangin | [@madelainedalangin](https://github.com/madelainedalangin) |
| Sam Francisco | [@delacrxz](https://github.com/delacrxz)|
| Xander Flores| [@x4nni](https://github.com/x4nni)|
| Aaryan Shetty| [@AaryanHazCompter](https://github.com/AaryanHazCompter)|
| Joshua Gomez | [@jbgomez9](https://github.com/jbgomez9)|

## ✨ Features

**Identity & Profiles**
- Author (User) registration with admin approval
- Editable profiles with name, bio, profile picture (via URL), and GitHub link
- Public profile pages displaying recent entries
- Automatic GitHub activity integration as public entries

**Entries**
- Create, edit, and delete entries
- Support for plain text, CommonMark (Markdown), and image entries
- Visibility controls: public, friends-only, and unlisted
- CommonMark entries can link to images for illustrated content
- Stream view with pagination, showing entries from followed authors

**Social Interactions**
- Follow, unfollow, and friend other authors (local and remote)
- Approve or deny follow requests
- Like entries and comments
- Comment on entries with full pagination support

**Federation 🌐**
- Distributed inbox model for sharing entries, likes, comments, and follow requests across nodes
- Node-to-node authentication via HTTP Basic Auth
- Federated with external teams: peachpuff, lavenderblush, and jd-node
- Each team member deploys their own independent node using shared code

**User Interface**
- Clean, responsive UI built with vanilla JavaScript and a Django template
- Loading screen overlay and animated landing page
- Follow button state machine (Follow, Pending, Following, Unfollow)
- Entry visibility indicators with emoji tags
- Styled with Google Fonts (Fredoka One, Nunito)

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django, Django REST Framework |
| Database | PostgreSQL (Heroku), SQLite (local) |
| Frontend | Vanilla JavaScript, Django Templates, HTML/CSS |
| Static Files | Whitenoise |
| Deployment | Heroku |

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- pip
- PostgreSQL (for production) or SQLite (for local development)
- A Heroku account (for deployment)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/madelainedalangin/Munch.git
   cd Munch
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Visit `http://127.0.0.1:8000/` in your browser.

### Deployment (Heroku)

Each team member deploys their own node:

```bash
git push heroku <branch>:main
git push heroku main
```

Heroku automatically runs migrations on each deploy. The app uses Whitenoise for serving static files in production.

## Testing

Run the full test suite:

```bash
python manage.py test munch
```

The project includes 113+ passing tests covering all user stories at the API and model level.

## 🤝 Federation

Munch uses an inbox-based federation model. The inbox is not a UI feature or a page that users interact with. It is a server-to-server endpoint that nodes use behind the scenes to push entries, likes, comments, and follow requests to one another. When a user creates a public entry, their node sends it to the inbox endpoints of all followers' nodes, including remote ones. Friends only entries are only seen between users who follow each other, regardless of their node origin.

**Connected Teams:**
- peachpuff
- lavenderblush
- jd-node

Remote nodes authenticate using HTTP Basic Auth. Node credentials are managed through the `Server` model and configured via the Django shell.

## 📄 Collaboration & External Sources

- Collaboration with other CMPUT 404 teams for federation cross-node compatibility.
- See Wiki for our API documentation.

## 📝 License

See [LICENSE](LICENSE) for details.
