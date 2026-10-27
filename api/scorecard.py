import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


API_URL = 'https://api.data.gov/ed/collegescorecard/v1/schools'
CACHE_KEY = 'college_scorecard_schools_v1'
CACHE_TTL_SECONDS = 12 * 60 * 60
PAGE_SIZE = 100
MAX_PAGES = 100
FIELDS = ','.join((
    'id',
    'school.name',
    'school.city',
    'school.state',
    'school.locale',
    'school.ownership',
    'school.operating',
    'latest.student.size',
    'latest.cost.tuition.in_state',
    'latest.cost.tuition.out_of_state',
    'latest.cost.avg_net_price.public',
    'latest.cost.avg_net_price.private',
    'latest.admissions.admission_rate.overall',
))


class ScorecardError(Exception):
    """Raised when College Scorecard data cannot be retrieved or parsed."""


def _request_page(api_key, page):
    query = urlencode({
        'api_key': api_key,
        'fields': FIELDS,
        'school.operating': 1,
        'per_page': PAGE_SIZE,
        'page': page,
    })
    request = Request(f'{API_URL}?{query}', headers={'User-Agent': 'Unify/1.0'})
    try:
        with urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        raise ScorecardError(
            f'College Scorecard returned HTTP {error.code}. Check the API key and try again.'
        ) from error
    except (URLError, TimeoutError) as error:
        raise ScorecardError('College Scorecard could not be reached. Try again later.') from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ScorecardError('College Scorecard returned an unreadable response.') from error

    if not isinstance(data, dict) or not isinstance(data.get('results'), list):
        raise ScorecardError('College Scorecard returned an unexpected response.')
    return data['results'], data.get('metadata', {})


def get_scorecard_schools():
    api_key = getattr(settings, 'SCORECARD_API_KEY', '')
    if not api_key:
        return None

    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached

    schools = []
    for page in range(MAX_PAGES):
        records, metadata = _request_page(api_key, page)
        schools.extend(records)
        total = metadata.get('total')
        if not records or (isinstance(total, int) and len(schools) >= total):
            break
    else:
        raise ScorecardError('College Scorecard returned more pages than the service allows.')

    cache.set(CACHE_KEY, schools, CACHE_TTL_SECONDS)
    return schools


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def _campus_setting(locale):
    if not isinstance(locale, (str, int)):
        return None
    locale_prefix = str(locale)[:1]
    if locale_prefix == '1':
        return 'urban'
    if locale_prefix == '2':
        return 'suburban'
    if locale_prefix in {'3', '4'}:
        return 'rural'
    return None


def normalize_school(record):
    ownership = _number(record.get('school.ownership'))
    public_net_price = _number(record.get('latest.cost.avg_net_price.public'))
    private_net_price = _number(record.get('latest.cost.avg_net_price.private'))
    net_price = public_net_price if ownership == 1 else private_net_price

    name = record.get('school.name')
    if not isinstance(name, str) or not name.strip():
        return None

    city = record.get('school.city')
    state = record.get('school.state')
    location_parts = [value.strip() for value in (city, state) if isinstance(value, str) and value.strip()]
    return {
        'id': record.get('id'),
        'name': name.strip(),
        'location': ', '.join(location_parts),
        'setting': _campus_setting(record.get('school.locale')),
        'student_size': _number(record.get('latest.student.size')),
        'net_price': net_price,
        'tuition_in_state': _number(record.get('latest.cost.tuition.in_state')),
        'tuition_out_state': _number(record.get('latest.cost.tuition.out_of_state')),
        'admit_rate': _number(record.get('latest.admissions.admission_rate.overall')),
    }
