# DocQR — Document download QR code app

A responsive Flask app that accepts document uploads, stores metadata in SQLite, and generates a QR code for each public download link.

## Features
- Mobile-first dark interface
- Upload PDF, Word, Excel, PowerPoint, TXT, CSV, JPG and PNG
- QR code generated for each uploaded file
- Public download route (no account required)
- SQLite metadata database
- Copy download link and download QR image

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open http://127.0.0.1:5000.

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp`.
The app reads environment variables from the shell; it does not automatically load `.env`. For local testing the defaults work without it.

## Deploy to Render

1. Push this folder to a GitHub repository.
2. In Render, choose **New + → Blueprint** and connect the repository.
3. Render reads `render.yaml`. Create the service and attach the persistent disk.
4. After deployment, open the service's Environment settings and set `PUBLIC_BASE_URL` to the exact public HTTPS URL, for example `https://your-service.onrender.com`.
5. Redeploy after setting the URL. Upload a test document and scan its QR code from a separate phone.

**Important:** SQLite and uploaded files are stored on the persistent disk at `/var/data`. A persistent disk is required so uploads and the database survive redeploys/restarts; check your hosting plan's disk availability and pricing. Do not deploy this configuration on an ephemeral filesystem for permanent document storage.

## Security and operational notes

- Anyone with a QR code or download URL can download that file. Do not upload confidential documents.
- The app limits uploads to 20 MB by default and checks file extensions. Set `MAX_UPLOAD_MB` to change the limit.
- For production, use HTTPS, set a strong `SECRET_KEY`, keep dependencies updated, and add authentication, malware scanning, rate limits, and retention/deletion controls if needed.
- Back up the SQLite database and uploaded files together.
- The app currently has no delete/admin feature.

## Environment variables

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask session signing key |
| `PUBLIC_BASE_URL` | Public HTTPS origin embedded in QR codes |
| `MAX_UPLOAD_MB` | Maximum upload size |
| `DATA_DIR` | Base data directory |
| `DATABASE_PATH` | SQLite database file |
| `UPLOAD_FOLDER` | Uploaded documents |
| `QR_FOLDER` | Generated QR PNGs |
