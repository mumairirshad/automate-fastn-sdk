"""Helper to refresh/obtain auth tokens for fastn-sdk (30 min tokens).

Supports:
  1. refresh_token grant (fast, if refresh token still valid)
  2. Automated device flow with ROPC login + consent (if refresh fails)
"""
import httpx, json, re, time
from datetime import datetime, timedelta, timezone

BASE = 'https://live.fastn.ai'
KEYCLOAK = f'{BASE}/auth/realms/fastn/protocol/openid-connect'
KEYCLOAK_BASE = f'{BASE}/auth/realms/fastn'
CLIENT_ID = 'fastn-sdk'
LOCAL_CONFIG = r'C:\Users\Umair\fastnSDK\.fastn\config.json'
CONFIG_PATH = LOCAL_CONFIG

# Credentials for automated device flow
USERNAME = 'automation@fastn.ai'
PASSWORD = 'automation'


def _save_tokens(tokens, config=None):
    """Save tokens to local config."""
    if config is None:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
    config['auth_token'] = tokens['access_token']
    config['refresh_token'] = tokens['refresh_token']
    config['token_expiry'] = (
        datetime.now(timezone.utc) + timedelta(seconds=tokens['expires_in'])
    ).isoformat()
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def refresh_token():
    """Refresh token via refresh_token grant. Returns True on success."""
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    rt = config.get('refresh_token', '')
    if not rt:
        return False

    resp = httpx.post(f'{KEYCLOAK}/token', data={
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'refresh_token': rt,
    })

    if resp.status_code == 200:
        _save_tokens(resp.json(), config)
        return True
    return False


def device_flow_login():
    """Automated device flow: start flow, login via HTTP, approve consent, get tokens."""
    def abs_url(url):
        return url if url.startswith('http') else BASE + url

    # Start device flow
    dr = httpx.post(f'{KEYCLOAK}/auth/device', data={
        'client_id': CLIENT_ID, 'scope': 'openid'
    })
    dd = dr.json()
    device_code = dd['device_code']
    user_code = dd['user_code']

    client = httpx.Client(follow_redirects=False, timeout=30)

    # Load device page -> login form
    r1 = client.get(f'{KEYCLOAK_BASE}/device', params={'user_code': user_code})
    r2 = client.get(abs_url(r1.headers['location']))

    # Submit login
    action = abs_url(re.search(r'action="([^"]+)"', r2.text).group(1).replace('&amp;', '&'))
    r3 = client.post(action, data={'username': USERNAME, 'password': PASSWORD})

    # Handle consent page
    r4 = client.get(abs_url(r3.headers['location']))
    form_match = re.search(r'action="([^"]*consent[^"]*)"', r4.text)
    code_match = re.search(r'name="code"\s+value="([^"]+)"', r4.text)
    if form_match and code_match:
        consent_url = abs_url(form_match.group(1).replace('&amp;', '&'))
        client.post(consent_url, data={'code': code_match.group(1), 'accept': 'Yes'})

    client.close()

    # Poll for token
    for _ in range(10):
        time.sleep(3)
        tr = httpx.post(f'{KEYCLOAK}/token', data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'client_id': CLIENT_ID,
            'device_code': device_code,
        })
        if tr.status_code == 200:
            _save_tokens(tr.json())
            return True
        err = tr.json().get('error', '')
        if err not in ('authorization_pending', 'slow_down'):
            return False
    return False


def ensure_fresh_token():
    """Try refresh first, fall back to full device flow login."""
    if refresh_token():
        return True
    return device_flow_login()


def set_project(project_id):
    """Update project_id in config."""
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    config['project_id'] = project_id
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


if __name__ == '__main__':
    if ensure_fresh_token():
        print('Token ready (30 min)')
    else:
        print('Auth FAILED')
