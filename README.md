# Unify

## College Match Quiz data

The quiz can rank U.S. colleges using the U.S. Department of Education's College Scorecard API. Create an API key from the [College Scorecard API documentation](https://collegescorecard.ed.gov/data/api/) and set it as an environment variable before starting Django. Keep the key private; do not commit it to the repository.

In PowerShell:

```powershell
$env:SCORECARD_API_KEY = "your-api-key"
py manage.py runserver
```

The API response is cached in memory for 12 hours. Scorecard institution data includes enrollment, campus location, tuition/net price, and admissions data. The current quiz scores on enrollment, location, and net price; program offerings, campus social life, housing, and transfer acceptance are not included in this API result and are not scored from Scorecard. Cost and enrollment are reported figures and should be confirmed with each institution.

Without `SCORECARD_API_KEY`, the quiz uses the local college database and labels results accordingly. If the configured Scorecard API is unavailable, the endpoint reports an error instead of silently switching to local data.