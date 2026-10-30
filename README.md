# Unify

## College Match Quiz data

The quiz and university directory can use the U.S. Department of Education's College Scorecard API. Create an API key from the [College Scorecard API documentation](https://collegescorecard.ed.gov/data/api/) and keep it private. Django reads `SCORECARD_API_KEY` from the process environment or the ignored local `.env` file.

Install the dependencies, copy the example to `.env`, enter the key in that file, then start Django in PowerShell:

```powershell
py -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
py manage.py runserver
```

The API response is cached in memory for 12 hours. Scorecard institution data includes enrollment, campus location, tuition/net price, and admissions data. The quiz scores on enrollment, location, and net price; program offerings, campus social life, housing, and transfer acceptance are not included in this API result and are not scored from Scorecard. Cost and enrollment are reported figures and should be confirmed with each institution.

The endpoints are `POST /api/match/` for quiz matches and `GET /api/colleges/` for the paginated university directory. The directory accepts `q`, `setting`, `max_price`, `page`, and `page_size` query parameters. Without a key, it clearly identifies results as local institution records.

Without `SCORECARD_API_KEY`, the quiz uses the local college database and labels results accordingly. If the configured Scorecard API is unavailable, the endpoint reports an error instead of silently switching to local data.