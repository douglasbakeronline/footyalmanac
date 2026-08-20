# Putting this online

The dashboard is a static file and the rebuild is one Python script, so you do not
need a server. Any static host will do; GitHub Pages is the least effort because
GitHub Actions also gives you the daily cron for free.

## GitHub Pages (recommended)

1. Create a repository and push these files, including `.github/workflows/deploy.yml`.
2. Repository **Settings -> Pages -> Build and deployment -> Source: GitHub Actions**.
3. **Actions** tab -> "Rebuild and publish" -> **Run workflow**.

Live at `https://<your-username>.github.io/<repo-name>/` within a couple of minutes.

The workflow rebuilds daily at 06:15 UTC, refuses to publish an empty build, and can
be triggered by hand after you edit `adjustments.json`.

Two things to know. GitHub deprioritises scheduled jobs under load, so the daily run
can be anywhere from a few minutes to an hour late; do not schedule it tight against
an early kick-off. And scheduled workflows are disabled automatically after 60 days
of no repository activity, so a repo you never touch will quietly stop updating.

## Alternatives

**Cloudflare Pages / Netlify / Vercel.** Same idea, better uptime, but the scheduler
is a separate paid or beta product on each. If you go this route, keep the GitHub
Action for the rebuild and let it commit `dashboard.html`, then have the host deploy
on push.

**A cheap VPS.** Use `refresh.sh` with real cron and serve the folder with nginx or
`python3 -m http.server`. More control, more to maintain. Worth it only once you are
paying for a live data feed and want to poll it more than once a day.

**A private link.** GitHub Pages is public. If you would rather it were not, Cloudflare
Pages with Cloudflare Access in front is the cheapest way to put a login on a static
site.

## Custom domain

Add a `CNAME` file to `_site` in the workflow with your domain, point a CNAME record
at `<your-username>.github.io`, then set the domain under Settings -> Pages. HTTPS is
issued automatically and takes a few minutes.

## Before you make it public

Two things worth doing, in this order.

**Score it in public.** `refresh.sh` archives every build. Publish a page showing how
last week's predictions actually did. A prediction site that never scores itself is
asking to be trusted on nothing, and yours has a real backtest behind it, so use it.

**Say what it is.** The footer already notes the model is worse than the betting
market. Keep that visible rather than buried. If the site is public in the UK and
reads as betting advice, you are in the territory the Gambling Commission cares
about; a clearly framed statistics tool is not, but the framing is what does the work.
Worth thirty minutes of proper reading before you put a domain on it.
