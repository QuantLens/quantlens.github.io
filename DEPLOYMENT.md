# QuantLens — Deploy to a Free Subdomain Now, Custom Domain Later

This guide shows how to publish the `site/` folder to a free host in minutes and attach a custom domain when you’re ready.

Pick one host below. All options support a free subdomain today and a custom domain later.

---

## Option A — GitHub Pages (free, CI-based)

Best if your code is on GitHub and you want a simple CI deployment.

Prereqs:

- A GitHub repo (your code is already structured with `site/` and a workflow).

Steps:

1) Push your repo to GitHub under the QuantLens org (e.g., `QuantLens/quantlens-site`).
2) In GitHub → Settings → Pages, set Source to “GitHub Actions”.
3) Our workflow `.github/workflows/gh-pages.yml` will publish `site/` automatically on push to `main` or `master`.
4) Visit the Pages URL from the Actions run summary (often `https://<user>.github.io/<repo>/`).

Base path:

- If your site is at `https://<user>.github.io/<repo>/`, uncomment `<base href="/<repo>/">` in each HTML head.
- If using a root/custom domain, leave the base tag commented.

Robots & sitemap:

- Staging: `site/robots.txt` blocks indexing. Keep it while testing.
- Launch: Replace placeholders in `site/_partials/head-meta.html` and `site/sitemap.xml` with your real URL, flip robots to allow, and add a `Sitemap:` line.

Custom domain:

1) Buy a domain (or use one you own).
2) In GitHub → Settings → Pages → Custom domain, enter `www.yourdomain.com`.
3) Add a CNAME in your DNS to `<user>.github.io`. GitHub will manage the TLS cert. Optionally add an `A` record for apex via GitHub’s IPs.
4) Add a `CNAME` file under `site/` with `www.yourdomain.com` (optional but recommended).

---

## Option B — Netlify (free subdomain: `*.netlify.app`)

Fastest to try locally or from Git.

Deploy now via drag-and-drop:

1) Build (not needed here) — your static site already lives in `site/`.
2) Go to app.netlify.com → Sites → Add new site → Deploy manually.
3) Drag the `site/` folder into the dropzone.
4) You’ll get `https://<random>.netlify.app`. Later, set a custom subdomain or custom domain.

Git deploy:

- Connect your repo and set “Base directory” to `/` and “Publish directory” to `site`.
- `netlify.toml` already points to `site`.

Custom domain:

- In Netlify → Domain settings → Add domain. Add your domain and follow DNS prompts (CNAME/ANAME). Netlify provisions TLS.

---

## Option C — Vercel (free subdomain: `*.vercel.app`)

1) Import your repo at vercel.com/new.
2) Framework preset: “Other”. Output directory: `site`.
3) Deploy.

Custom domain:

- Project → Settings → Domains → Add. Vercel provides DNS guidance and TLS.

Base path:

- If you end up at a subpath, use the `<base>` tag. On a root domain or `*.vercel.app`, usually unneeded.

---

## Option D — Cloudflare Pages (free subdomain: `*.pages.dev`)

1) In dash.cloudflare.com → Pages → Create a project → Connect to Git.
2) Build command: none. Build output directory: `site`.
3) Deploy.

Custom domain:

- Pages → Custom domains → Add domain. Use Cloudflare DNS. TLS is automatic.

---

## Launch Checklist

Before going public:

- Decide final URL and remove placeholders:
  - `site/_partials/head-meta.html`: canonical, og:url, og:image, favicon.
  - `site/sitemap.xml`: replace YOUR-USER/YOUR-REPO with your URL paths.
- Update robots.txt to allow indexing and add:
  - `Sitemap: https://yourdomain.com/sitemap.xml`
- Optional polish:
  - Add `site/assets/og-cover.png` and `site/assets/favicon.ico`.
  - Add analytics (only in production).
  - If hosting as a project site (`/<repo>/`), set `<base href="/<repo>/">` across pages.

Done! You can switch hosts later without changing your content — just re-point DNS and update the canonical URLs.
