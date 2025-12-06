# Environment Variables Mapping

## Summary: Settings.py vs Render Configuration

### ✅ All Your Render Environment Variables Are Now Supported!

| Render Variable | Settings.py Reads | Status | Notes |
|----------------|-------------------|--------|-------|
| `DATABASE_URL` | `DATABASE_URL` | ✅ MATCH | Auto-provided by Render PostgreSQL |
| `DJANGO_SECRET_KEY` | `DJANGO_SECRET_KEY` | ✅ MATCH | Required for production |
| `DEBUG` | `DEBUG` or `DJANGO_DEBUG` | ✅ MATCH | Checks DJANGO_DEBUG first, then DEBUG |
| `DJANGO_ALLOWED_HOSTS` | `DJANGO_ALLOWED_HOSTS` | ✅ MATCH | Comma-separated list |
| `GA_MEASUREMENT_ID` | `GA_MEASUREMENT_ID` | ✅ MATCH | Defaults to current value if not set |
| `RENDER_EXTERNAL_HOSTNAME` | `RENDER_EXTERNAL_HOSTNAME` | ✅ AUTO | Auto-provided by Render, added to ALLOWED_HOSTS |

---

## Detailed Configuration

### 1. SECRET_KEY
```python
SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-dev-key-change-in-production-12345')
```
- **Reads:** `DJANGO_SECRET_KEY`
- **Your Render:** ✅ `DJANGO_SECRET_KEY`
- **Status:** ✅ PERFECT MATCH

### 2. DEBUG
```python
DEBUG = os.getenv("DJANGO_DEBUG", os.getenv("DEBUG", "False")).lower() == "true"
```
- **Reads:** `DJANGO_DEBUG` first, then `DEBUG` as fallback
- **Your Render:** ✅ `DEBUG`
- **Default:** `False` (production-safe)
- **Status:** ✅ SUPPORTED (checks both variables)

### 3. ALLOWED_HOSTS
```python
allowed_hosts_env = os.getenv("DJANGO_ALLOWED_HOSTS")
if allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]
else:
    ALLOWED_HOSTS = [
        '127.0.0.1',
        'localhost',
        'yale-newcomer-survival-guide.onrender.com',
    ]

# Auto-add RENDER_EXTERNAL_HOSTNAME
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
```
- **Reads:** `DJANGO_ALLOWED_HOSTS` (comma-separated), falls back to hardcoded list
- **Your Render:** ✅ `DJANGO_ALLOWED_HOSTS`
- **Auto-adds:** `RENDER_EXTERNAL_HOSTNAME` (provided by Render)
- **Default includes:** `127.0.0.1`, `localhost`, known Render URL
- **Status:** ✅ SUPPORTED + Auto-adds Render hostname

### 4. DATABASE_URL
```python
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        ...
    )
}
```
- **Reads:** `DATABASE_URL`
- **Your Render:** ✅ `DATABASE_URL`
- **Default:** SQLite (local development)
- **Status:** ✅ PERFECT MATCH

### 5. GA_MEASUREMENT_ID
```python
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "G-9XJWT2P5LE")
```
- **Reads:** `GA_MEASUREMENT_ID`
- **Your Render:** ✅ `GA_MEASUREMENT_ID`
- **Default:** `G-9XJWT2P5LE` (current value)
- **Status:** ✅ SUPPORTED + Available in templates via context processor

---

## Production Verification

### ✅ DEBUG in Production
- **Expected:** `False`
- **Actual:** ✅ Defaults to `False` when not set
- **Behavior:** Checks `DJANGO_DEBUG`, then `DEBUG`, defaults to `False`

### ✅ ALLOWED_HOSTS in Production
- **Includes localhost:** ✅ Yes (`127.0.0.1` and `localhost`)
- **Includes Render domains:** ✅ Yes
  - Hardcoded: `yale-newcomer-survival-guide.onrender.com`
  - Auto-added: Any value from `RENDER_EXTERNAL_HOSTNAME`
  - Configurable: Via `DJANGO_ALLOWED_HOSTS` env var
- **Behavior:**
  - If `DJANGO_ALLOWED_HOSTS` is set: Uses that (comma-separated)
  - Otherwise: Uses default list
  - Always: Adds `RENDER_EXTERNAL_HOSTNAME` if present

---

## Template Usage

The `GA_MEASUREMENT_ID` is now available in all templates via context processor:

```html
<!-- In templates/base.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id={{ GA_MEASUREMENT_ID }}"></script>
<script>
  gtag('config', '{{ GA_MEASUREMENT_ID }}');
</script>
```

Context processor: `core/context_processors.py`

---

## Files Modified

1. ✅ `config/settings.py` - Updated to support all your Render env vars
2. ✅ `templates/base.html` - Uses `{{ GA_MEASUREMENT_ID }}` from settings
3. ✅ `core/context_processors.py` - New file, makes GA_MEASUREMENT_ID available in templates

---

## Testing

All tests pass:
- ✅ Django system check: No issues
- ✅ A/B test tests: All 6 passing
- ✅ Settings import: Working correctly
- ✅ Context processor: GA_MEASUREMENT_ID available in templates

---

**Status:** ✅ ALL RENDER ENVIRONMENT VARIABLES ARE NOW SUPPORTED AND WORKING!
