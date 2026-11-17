# CloudMercury website

One-page website for CloudMercury (digital marketing, software & SaaS development, web and email hosting) with a
custom management dashboard to edit everything on the site.

## Website dashboard

Go to **/dashboard/** (or **/admin/**, which opens the same dashboard) and sign in. Sign-in is protected by Cloudflare Turnstile and two-factor authentication.

From the dashboard you can:

* **Messages** – read, search, add notes to and delete contact-form messages.
* **Header & hero** – headline, intro, buttons, the website picture and the technology strip.
* **About & numbers** – about text, the short points and the numbers box (150+ clients, …).
* **Services** – add, edit, reorder, hide or delete service cards; badges such as "Launching soon".
* **How we work**, **Why choose us**, **FAQ** – steps, reasons, industries and questions.
* **Contact & banner** – contact details, form texts, where new messages are emailed, the call-to-action banner.
* **Footer & social** – footer text and social links.
* **Logo & colours** – upload logos and tab icon, change brand colours.
* **Google & SEO** – page title, description and Google Tag Manager ID.

Changes appear on the website straight away.

### Who can sign in

Only **staff** users can open the dashboard, and they must turn on two-factor the first time. Public sign-up is off.
Create a user with:

```bash
python manage.py createsuperuser
```

Forgot the password? `python manage.py changepassword <username>`.
Lost the phone with the authenticator app? Use a backup code, or reset two-factor with:
`python manage.py shell -c "from accounts.models import Profile; Profile.objects.filter(user__username='NAME').update(totp_enabled=False)"`

Django's built-in admin is still available at **/django-admin/** for superusers (linked at the bottom of the
dashboard menu as "Advanced").

## Run locally

```bash
source denv/bin/activate
cp .env.example .env        # then fill in values
python manage.py migrate
python manage.py runserver
```

Tests: `python manage.py test accounts cms`

## Production

* **Database:** set `DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DBNAME` in `.env`
  (or `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`).
  With neither set, the site uses the local SQLite file `db.sqlite3`.
  Special characters in the password must be URL-encoded in `DATABASE_URL` (for example `@` becomes `%40`).
* **Static files:** served by WhiteNoise. Run `python manage.py collectstatic` on each deploy
  (the Dockerfile does this for you).
* **Docker:** `docker build -t cloudmercury .` then
  `docker run --env-file .env -p 8001:8001 -v cloudmercury-media:/app/backend/media cloudmercury`.
  Migrations run automatically when the container starts. Keep the `media` volume so uploaded logos survive updates.
* Set `DJANGO_DEBUG=False` and a long random `DJANGO_SECRET_KEY` in production.

Install requirements with `pip install -r requirements.txt` (Django, WhiteNoise, psycopg for Postgres, gunicorn).

## Cloudflare Turnstile

The site uses Cloudflare's **test keys** until you add real ones in `.env` (`TURNSTILE_SITE_KEY`,
`TURNSTILE_SECRET_KEY`). Create them in the Cloudflare dashboard under Turnstile.

## Uploaded files

Logos uploaded in the dashboard are stored in `media/`. Keep that folder when you deploy or rebuild the server.

## Turned-off features

The client portal (hosting, projects, billing for customers) is built in the `dashboard` app but switched off.
See the commented line in `core/urls.py` to turn it on when hosting launches.
