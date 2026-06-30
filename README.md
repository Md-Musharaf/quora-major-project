# Quora Clone

A full-featured Quora-inspired question-and-answer platform built with Django.

The project supports user authentication, public profiles, questions, answers, topics, nested comments, voting, following, Spaces, image uploads, and global database-backed search.

---

## Live Demo

The application is deployed on Render from the `main` branch.

**Live website:** [https://quora-major-project.onrender.com/](https://quora-major-project.onrender.com/)

---

## Features

### Authentication and Profiles

- Custom Django user model
- Email-based registration and login
- Automatic profile creation
- Profile picture, display name, bio, profession, location, and website
- Public profile pages
- Profile editing
- Cloudinary-backed media and static-file storage
- Followers and following system
- Profile activity, question, answer, follower, following, and received-upvote statistics

### Questions and Answers

- Create, view, edit, and delete questions
- Author-only edit and delete permissions
- Add optional images to questions
- Replace or remove existing question images
- Post, edit, and delete answers
- Display answer counts
- Question detail pages

### Topics

- Select existing topics while creating or editing a question
- Create new comma-separated topics
- Case-insensitive topic reuse
- Duplicate topic prevention
- Maximum of five topics per question
- Topic pages and topic-based question discovery

### Voting

- Upvote and remove upvotes from questions
- Upvote and remove upvotes from answers
- Duplicate-vote prevention with database constraints
- Active upvote state in the interface
- Efficient vote-count and user-vote annotations

### Comments and Replies

- Comments under answers
- Unlimited nested replies using a self-referencing comment model
- Recursive comment rendering
- Author-only edit and delete controls
- Safe redirect handling after comment actions
- Efficient comment loading with `select_related` and `Prefetch`

### Spaces

- Create and browse Quora-style Spaces
- Space detail pages
- Cover images and Space information
- Space navigation from the home page
- Space-specific content organization

### Search

- Global search for questions, users, and topics
- Search questions by title, description, and topic name
- Search users by display name, profession, and email
- Search topics by name and description
- Result counts for every search section
- Global no-results state
- Empty result sections are hidden automatically

### User Interface

- Responsive Quora-inspired interface
- Tailwind CSS styling
- Dark-mode support
- Global navigation bar
- Responsive home feed
- Question image previews
- Clean question, answer, profile, topic, and Space pages

---

## Technology Stack

### Backend

- Python
- Django
- Django ORM

### Frontend

- Django Templates
- HTML
- Tailwind CSS
- JavaScript

### Storage and Deployment

- Cloudinary
- `django-cloudinary-storage`
- `dj-database-url`
- Render-compatible Django configuration

---

## Main Django Applications

The project is organized into separate Django applications based on responsibility:

```text
config/          Project settings, URLs, WSGI, and ASGI configuration
users/           Custom user model, profiles, authentication, and follow system
questions/       Questions, answers, forms, views, and topic-saving services
topics/          Topic models and topic pages
interactions/    Question and answer voting
comments/        Comments and recursive replies
spaces/          Quora-style Spaces
templates/       Shared and application templates
static/          CSS, JavaScript, and static assets
media/           Local development uploads when Cloudinary is unavailable
```

The exact directory structure may differ slightly as the project continues to grow.

---

## Prerequisites

Install the following before running the project:

- Python 3.12 or a compatible Python 3 version
- Git
- A Cloudinary account for production media storage

---

## Local Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd quora-major-project
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the environment file

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=sqlite:///db.sqlite3

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
CLOUDINARY_URL=
```

Use the exact environment-variable names configured in your `settings.py` if they differ from the example above.

---

## Prepare the Django Application

### 1. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create an administrator

```bash
python manage.py createsuperuser
```

### 3. Start the Django development server

```bash
python manage.py runserver
```

Open the project in your browser:

```text
http://127.0.0.1:8000/
```

---

## Cloudinary Storage

The project conditionally uses Cloudinary when Cloudinary credentials are available.

When Cloudinary is configured, Django uses:

```python
cloudinary_storage.storage.MediaCloudinaryStorage
```

for uploaded media and:

```python
cloudinary_storage.storage.StaticCloudinaryStorage
```

for static files.

When Cloudinary credentials are unavailable, the project falls back to Django's local filesystem storage for development.

Do not commit Cloudinary credentials to Git.

---

## Database Constraints and Security

The project includes several safeguards:

- Unique vote constraints prevent duplicate question and answer votes
- Follow constraints prevent duplicate follows
- Self-following is blocked
- Question topics are normalized and deduplicated
- Author-only editing and deletion are enforced
- Authentication is required for protected actions
- State-changing actions use POST requests
- CSRF protection is enabled
- Redirect destinations are validated before use
- Environment variables are used for secrets and service credentials

---

## Useful Django Commands

Run the development server:

```bash
python manage.py runserver
```

Create migrations:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Open the Django shell:

```bash
python manage.py shell
```

Run Django checks:

```bash
python manage.py check
```

Collect static files:

```bash
python manage.py collectstatic --noinput
```

Create a superuser:

```bash
python manage.py createsuperuser
```

Run tests:

```bash
python manage.py test
```

---

## Deployment Notes

The project is currently deployed on Render from the `main` branch.

**Production URL:** [https://quora-major-project.onrender.com/](https://quora-major-project.onrender.com/)

The project can be deployed to Render as a standard Django application.

A typical production setup requires:

- A Django web service
- A PostgreSQL database
- Cloudinary credentials
- Production environment variables
- `DEBUG=False`
- A secure `SECRET_KEY`
- Correct `ALLOWED_HOSTS`
- Static-file collection during deployment

Example web start command:

```bash
gunicorn config.wsgi:application
```

Example build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

---

## Suggested Environment Variables for Production

```env
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=

DATABASE_URL=

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
CLOUDINARY_URL=
```

Never commit the production `.env` file.

---

## Troubleshooting

### Django cannot start

Run:

```bash
python manage.py check
```

Then confirm that:

- The virtual environment is active
- All dependencies are installed
- The `.env` file exists
- Required environment variables are available
- Migrations have been applied

### Database errors appear

Run:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Uploaded images are not loading

Check:

- Cloudinary environment variables
- Django `STORAGES` configuration
- Media configuration for local development
- Template use of the image field's `.url`
- Whether the uploaded file exists in Cloudinary or local media storage

### Search results are missing

Confirm that the search view checks the correct fields and uses `distinct()` where joins may create duplicate question results.

Also verify that the search form sends the query parameter expected by the view.

---

## Future Improvements

Possible future additions include:

- Notifications
- Bookmarks
- Space membership and moderation
- Rich-text question and answer editors
- Search filters and pagination
- Email verification and password reset
- Content reporting
- User blocking
- REST API support
- Automated test coverage
- Docker support
- Continuous integration and deployment

---

## Contributing

1. Create a new branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make and test your changes.

3. Commit the changes:

   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

4. Push the branch:

   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a pull request.

---

## Author

**Md Musharaf**

- GitHub: [md-musharaf](https://quora-major-project.onrender.com/)
- Email: `mdraza1615@gmail.com`

---

## License

Add the license you want to use for this project. For an open-source educational project, the MIT License is a common option.