# A/B Test Debug Verification Protocol

## Step 1: Pre-Deployment Checklist

### ✅ Debug Hooks Confirmed

**core/views.py (lines 458-461):**
```python
# TEMPORARY DEBUG LOGGING - Remove after debugging
print("A/B DEBUG — force_param:", force_param)
print("A/B DEBUG — cookie_variant:", cookie_variant)
print("A/B DEBUG — final variant:", variant)
```

**templates/core/abtest.html (lines 21-24):**
```html
{# TEMPORARY DEBUG BLOCK - Remove after confirming forced variant works #}
<pre id="debug" style="background: #f0f0f0; padding: 10px; border: 1px solid #ccc;">
variant="{{ variant }}"
</pre>
```

### ⚠️ Migrations Status

Two migrations are pending and must be run in production:
- `0003_abtestevent` - Creates ABTestEvent model
- `0004_alter_abtestevent_options_abtestevent_endpoint_and_more` - Adds endpoint and user_id fields

**Action Required:** Ensure migrations run during Render deployment or manually via Render shell.

---

## Step 2: Deployment Checklist

### Pre-Deployment

1. ✅ Commit all changes to git
2. ✅ Push to `main` branch (or your deployment branch)
3. ✅ Verify Render is configured to auto-deploy from this branch

### During Deployment

1. Monitor Render deployment logs
2. Verify migrations run successfully (check build logs for `python manage.py migrate`)
3. Note deployment completion time

### Post-Deployment Verification

1. Visit `/218b7ae/` in a new incognito window
2. **Visual confirmation:** You should see a gray box with `variant="..."` above the button
3. If the debug `<pre>` block is NOT visible, the deployment didn't take effect yet

---

## Step 3: Runtime Verification Protocol

### Test Setup

1. Open a **brand new incognito/private window** (clears cookies and cache)
2. Open browser DevTools (F12) → Network tab (optional, to monitor requests)

### Test Case 1: `force_variant=a`

**URL:** `https://yale-newcomer-survival-guide.onrender.com/218b7ae/?force_variant=a`

**Observe:**
1. **Button text:** Write down what text appears on the button: `________________`
2. **Debug block:** View Page Source (Ctrl+U / Cmd+Option+U), search for `<pre id="debug">`
   - Write down the variant value: `variant="________________"`
3. **Render logs:** Check Render service logs (Render dashboard → Logs)
   - Search for "A/B DEBUG" lines
   - Write down:
     - `force_param: ________________`
     - `cookie_variant: ________________`
     - `final variant: ________________`

**Expected Results:**
- Button text: `kudos`
- Debug block: `variant="kudos"`
- Logs: `force_param: a`, `cookie_variant: None` (or empty), `final variant: kudos`

---

### Test Case 2: `force_variant=b`

**URL:** `https://yale-newcomer-survival-guide.onrender.com/218b7ae/?force_variant=b`

**Observe:**
1. **Button text:** Write down what text appears on the button: `________________`
2. **Debug block:** View Page Source, search for `<pre id="debug">`
   - Write down the variant value: `variant="________________"`
3. **Render logs:** Check Render service logs
   - Search for "A/B DEBUG" lines
   - Write down:
     - `force_param: ________________`
     - `cookie_variant: ________________`
     - `final variant: ________________`

**Expected Results:**
- Button text: `thanks`
- Debug block: `variant="thanks"`
- Logs: `force_param: b`, `cookie_variant: None` (or empty), `final variant: thanks`

---

## Step 4: Result Interpretation Guide

After collecting the triples, compare them to identify the issue:

### Case 1: Template/Caching Issue
**Symptoms:**
- Logs show: `force_param: 'b'`, `final variant: 'thanks'`
- Debug `<pre>` shows: `variant="thanks"`
- Button displays: `"kudos"` ❌

**Diagnosis:** Template is rendering correctly, but button text is cached or overridden client-side (unlikely based on our JS search, but possible)

**Fix:** Check browser cache, CDN cache (if any), or template fragment caching

---

### Case 2: Backend Logic Bug
**Symptoms:**
- Logs show: `force_param: 'b'`
- Logs show: `final variant: 'kudos'` ❌ (should be 'thanks')
- Debug `<pre>` shows: `variant="kudos"` ❌
- Button displays: `"kudos"` ❌

**Diagnosis:** The `elif force_param == 'b':` branch is not executing, or variant is being overwritten after assignment

**Fix:** Review the if/elif/else logic in `abtest_view` (lines 444-456)

---

### Case 3: Query Parameter Parsing Issue
**Symptoms:**
- Logs show: `force_param: ''` or `force_param: None` ❌
- Logs show: `cookie_variant: 'kudos'` (or some value)
- Logs show: `final variant: 'kudos'` (from cookie, not from force)
- Debug `<pre>` shows: `variant="kudos"`
- Button displays: `"kudos"`

**Diagnosis:** `request.GET.get('force_variant')` is not reading the URL parameter correctly

**Possible Causes:**
- URL routing issue
- Middleware stripping query params
- URL encoding issue

**Fix:** 
1. Check `request.GET` dict directly: add `print("A/B DEBUG — all GET params:", dict(request.GET))`
2. Verify URL is correct (no encoding issues)
3. Check for middleware that might modify request.GET

---

### Case 4: System Working Correctly ✅
**Symptoms:**
- Test Case 1 (`force_variant=a`):
  - Button: `kudos` ✓
  - Debug block: `variant="kudos"` ✓
  - Logs: `force_param: 'a'`, `final variant: 'kudos'` ✓

- Test Case 2 (`force_variant=b`):
  - Button: `thanks` ✓
  - Debug block: `variant="thanks"` ✓
  - Logs: `force_param: 'b'`, `final variant: 'thanks'` ✓

**Diagnosis:** System is working correctly. Earlier issue was likely:
- Old deployment not yet updated
- Browser cache showing old version
- Cookie persistence from previous visit

**Action:** Proceed to cleanup (remove debug code) and add automated tests

---

## Step 5: Cleanup Plan

After confirming behavior, remove debug code:

### Remove Debug Logging

**File:** `core/views.py`

**Remove lines 458-461:**
```python
# TEMPORARY DEBUG LOGGING - Remove after debugging
print("A/B DEBUG — force_param:", force_param)
print("A/B DEBUG — cookie_variant:", cookie_variant)
print("A/B DEBUG — final variant:", variant)
```

**Keep the `cookie_variant` variable assignment** (line 442) as it improves code clarity.

### Remove Debug Block

**File:** `templates/core/abtest.html`

**Remove lines 21-24:**
```html
{# TEMPORARY DEBUG BLOCK - Remove after confirming forced variant works #}
<pre id="debug" style="background: #f0f0f0; padding: 10px; border: 1px solid #ccc;">
variant="{{ variant }}"
</pre>
```

### Commit Cleanup

After cleanup:
```bash
git add core/views.py templates/core/abtest.html
git commit -m "Remove A/B test debug code after verification"
git push origin main
```

---

## Troubleshooting Notes

### If Debug Block Not Visible After Deployment

1. **Check deployment completed:** Render dashboard → Deploys → Latest deploy status
2. **Hard refresh:** Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
3. **Clear browser cache completely**
4. **Check if template is cached:** Try visiting with `?nocache=123` appended
5. **Verify correct environment:** Ensure you're on production URL, not staging

### If Logs Don't Appear

1. **Check Render log stream:** Render dashboard → Your service → Logs tab
2. **Filter by "DEBUG":** Search for "A/B DEBUG"
3. **Verify print statements:** Check that code was deployed (view file in Render shell)
4. **Check log level:** Ensure stdout is being captured

### If Results Don't Match Expected

- Collect all three values (button, debug block, logs) for both test cases
- Share the exact values with the interpretation guide above
- This will pinpoint where the issue occurs in the flow

---

## Next Steps After Verification

Once behavior is confirmed:

1. ✅ Remove debug code (see Cleanup Plan above)
2. ✅ Add automated tests (next prompt)
3. ✅ Document expected behavior for team
4. ✅ Remove forced variant functionality if not needed for production (or keep as QA tool)

