# A/B Test Endpoint & Analytics Pipeline Audit

**Date:** December 12, 2024  
**Repository:** far-storm-project  
**Team:** far-storm  
**Endpoint:** `/218b7ae/`

---

## Executive Summary

The A/B test implementation is **fully compliant** with all requirements. The endpoint is publicly accessible, correctly displays team member nicknames, implements proper variant assignment with session persistence, tracks both exposure and click events, and includes robust deduplication logic. A management command provides comprehensive reporting capabilities.

**Status:** ✅ **ALL REQUIREMENTS MET**

---

## 1. URL Path & Public Access

### Requirement: URL path is `/218b7ae/` and is publicly accessible (no auth)

**Status:** ✅ **PASS**

**Implementation:**
- **URL Configuration:** `config/urls.py:16`
  ```python
  path('218b7ae/', views.abtest_view, name='abtest'),
  ```
- **View Function:** `core/views.py:483-584` (`abtest_view`)
- **Authentication:** No `@login_required` decorator present
- **Access Control:** View is publicly accessible; no authentication checks

**Verification:**
- View function signature: `def abtest_view(request):` (no auth decorators)
- No authentication middleware blocking access
- Endpoint accessible to anonymous users

**Click Endpoint:**
- **URL:** `/218b7ae/click/` (`config/urls.py:17`)
- **View:** `core/views.py:587-670` (`abtest_click`)
- **Method:** POST-only endpoint for logging click events
- **Authentication:** No auth required (uses `@csrf_exempt` for POST)

---

## 2. Team Member Nicknames Display

### Requirement: Page displays ALL team member nicknames: stormy-deer, adorable-crow, super-giraffe

**Status:** ✅ **PASS**

**Implementation:**
- **View Code:** `core/views.py:558-563`
  ```python
  team_members = [
      "Chun-Hung Yeh ( stormy-deer )",
      "Celine (Qijing) Li ( adorable-crow )",
      "Denise Wu ( super-giraffe )",
  ]
  ```
- **Template:** `templates/core/abtest.html:13-18`
  ```html
  <h2 class="h5">Team members</h2>
  <ul>
    {% for member in team_members %}
      <li>{{ member }}</li>
    {% endfor %}
  </ul>
  ```

**Verification:**
- ✅ All three nicknames present: `stormy-deer`, `adorable-crow`, `super-giraffe`
- ✅ Names rendered in template via loop
- ✅ Displayed on page load (not dynamically loaded)

---

## 3. Button ID

### Requirement: There is a clickable button with `id="abtest"`

**Status:** ✅ **PASS**

**Implementation:**
- **Template:** `templates/core/abtest.html:21`
  ```html
  <button id="abtest" class="btn btn-primary">{{ variant }}</button>
  ```

**Verification:**
- ✅ Button has exact ID: `id="abtest"`
- ✅ Button is clickable (Bootstrap button class)
- ✅ JavaScript event listener attached: `templates/core/abtest.html:75`
  ```javascript
  document.getElementById("abtest").addEventListener("click", function() {
    // ... click handler logic
  });
  ```

---

## 4. Button Text Variants

### Requirement: Button text is exactly either "kudos" or "thanks"

**Status:** ✅ **PASS**

**Implementation:**
- **Variant Assignment:** `core/views.py:537-542`
  ```python
  variant = request.session.get(session_key_variant)
  if not variant:
      variant = random.choice(["kudos", "thanks"])
      request.session[session_key_variant] = variant
      request.session.modified = True
  ```
- **Template Rendering:** `templates/core/abtest.html:21`
  ```html
  <button id="abtest" class="btn btn-primary">{{ variant }}</button>
  ```

**Verification:**
- ✅ Variants are exactly "kudos" or "thanks" (hardcoded in `random.choice()`)
- ✅ Button text dynamically set from server-side variant
- ✅ No other text values possible

---

## 5. Variant Persistence & Stability

### Requirement: Variant assignment is persisted per user (session/cookie) and is stable on reload

**Status:** ✅ **PASS**

**Implementation:**
- **Session Key:** `core/views.py:506`
  ```python
  session_key_variant = f"abexp:{experiment_name}:variant"
  ```
- **Persistence Logic:** `core/views.py:538-542`
  ```python
  variant = request.session.get(session_key_variant)  # Retrieve from session
  if not variant:
      variant = random.choice(["kudos", "thanks"])     # Assign new variant
      request.session[session_key_variant] = variant   # Store in session
      request.session.modified = True                  # Mark session as modified
  ```
- **Session Engine:** Django's database-backed sessions (default configuration)

**Verification:**
- ✅ Variant stored in Django session (persisted via cookie `sessionid`)
- ✅ Same variant shown on page reload (retrieved from session)
- ✅ Session persists across requests within same browser session
- ✅ Cache headers prevent caching issues: `core/views.py:578-582`
  ```python
  response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
  response["Pragma"] = "no-cache"
  response["Expires"] = "0"
  response["Vary"] = "Cookie"
  ```

---

## 6. Exposure (View) Event Tracking

### Requirement: Tracking captures exposure (view) events

**Status:** ✅ **PASS**

**Implementation:**
- **Model:** `core/models.py:122-164` (`ABTestEvent` model)
- **Event Type:** `ABTestEvent.EVENT_TYPE_EXPOSURE = "exposure"`
- **Tracking Logic:** `core/views.py:544-556`
  ```python
  fire_ga_exposure = False
  if is_real_navigation and not request.session.get(session_key_exposed):
      ABTestEvent.objects.get_or_create(
          experiment_name=experiment_name,
          event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
          endpoint=endpoint,
          session_id=session_id,
          defaults={"variant": variant},
      )
      request.session[session_key_exposed] = True
      request.session.modified = True
      fire_ga_exposure = True
  ```

**Database Schema:**
- **Table:** `core_abtestevent`
- **Fields:** `experiment_name`, `variant`, `event_type`, `endpoint`, `session_id`, `created_at`, etc.
- **Indexes:** Composite indexes on `(experiment_name, variant, event_type)`, `(experiment_name, created_at)`, `(endpoint, event_type)`

**Client-Side Tracking:**
- **GA4 Event:** `templates/core/abtest.html:26-50`
  - Fires `gtag("event", "ab_exposure", payload)` only when `fire_ga_exposure` is True
  - Includes: `experiment_name`, `variant`, `endpoint`, `team`

**Verification:**
- ✅ Server-side exposure logged in database via `ABTestEvent`
- ✅ Client-side GA4 event fired on first exposure only
- ✅ Exposure logged only on real browser navigation (bot filtering applied)

---

## 7. Click Event Tracking

### Requirement: Tracking captures click events

**Status:** ✅ **PASS**

**Implementation:**
- **Event Type:** `ABTestEvent.EVENT_TYPE_CONVERSION = "conversion"`
- **Tracking Logic:** `core/views.py:653-660`
  ```python
  # Log Conversion (every click)
  ABTestEvent.objects.create(
      experiment_name=experiment_name,
      event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
      endpoint=endpoint,
      session_id=session_id,
      variant=variant,
  )
  ```
- **Client-Side Handler:** `templates/core/abtest.html:75-101`
  ```javascript
  document.getElementById("abtest").addEventListener("click", function() {
    // GA4 event
    if (typeof gtag === "function") {
      gtag("event", "ab_button_click", {...});
    }
    // Server-side logging
    fetch("/{{ endpoint_hash }}/click/", {
      method: "POST",
      headers: {"X-CSRFToken": csrftoken, ...},
    });
  });
  ```

**Backfill Logic:**
- **Exposure Backfill:** `core/views.py:632-651`
  - If click occurs before exposure is logged, backfills exposure event
  - Prevents conversions without corresponding exposures

**Verification:**
- ✅ Server-side conversion logged in database on every click
- ✅ Client-side GA4 event fired on click
- ✅ Variant retrieved from session (not from POST body)
- ✅ Exposure backfilled if missing

---

## 8. Deduplication Strategy

### Requirement: Dedupe strategy is correct (avoid double-counting exposures)

**Status:** ✅ **PASS**

**Multi-Layer Deduplication:**

**Layer 1: Session Flag**
- **Implementation:** `core/views.py:507, 546`
  ```python
  session_key_exposed = f"abexp:{experiment_name}:exposed:{endpoint}"
  # ...
  if is_real_navigation and not request.session.get(session_key_exposed):
      # Log exposure only if flag not set
      request.session[session_key_exposed] = True
  ```

**Layer 2: Database Uniqueness (get_or_create)**
- **Implementation:** `core/views.py:547-553`
  ```python
  ABTestEvent.objects.get_or_create(
      experiment_name=experiment_name,
      event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
      endpoint=endpoint,
      session_id=session_id,
      defaults={"variant": variant},
  )
  ```
- **Atomic Operation:** `get_or_create()` ensures database-level uniqueness
- **Uniqueness Key:** Combination of `(experiment_name, event_type, endpoint, session_id)`

**Layer 3: Bot Filtering**
- **Implementation:** `core/views.py:514-535`
  - User-Agent analysis (requires "Mozilla", excludes bot keywords)
  - Header validation (`Sec-Fetch-Mode: navigate`, `Accept: text/html`)
  - Prevents non-human traffic from generating exposures

**Click Deduplication:**
- **Not Required:** Click events are intentionally logged on every click (no deduplication)
- **Rationale:** Users may click multiple times; each click is a valid conversion event

**Verification:**
- ✅ Session flag prevents duplicate exposures within same session
- ✅ Database `get_or_create()` provides atomic protection against race conditions
- ✅ Bot filtering excludes non-human traffic
- ✅ Reloads do not generate additional exposure events

---

## 9. Reporting Command

### Requirement: Provide a command/report mechanism to determine which variant was preferred

**Status:** ✅ **PASS**

**Implementation:**
- **Command:** `python manage.py abtest_report`
- **File:** `core/management/commands/abtest_report.py`
- **Output Includes:**
  1. **Exposures by variant:** Count of `EVENT_TYPE_EXPOSURE` grouped by variant
  2. **Clicks by variant:** Count of `EVENT_TYPE_CONVERSION` grouped by variant
  3. **CTR (Conversion Rate) by variant:** `(conversions / exposures) * 100`
  4. **Winning variant:** Variant with highest conversion rate

**Command Code Reference:**
- **Exposures:** `core/management/commands/abtest_report.py:32-37`
  ```python
  exposure_counts = (
      events
      .filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE)
      .values('variant')
      .annotate(count=Count('id'))
  )
  ```
- **Conversions:** `core/management/commands/abtest_report.py:39-44`
  ```python
  conversion_counts = (
      events
      .filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION)
      .values('variant')
      .annotate(count=Count('id'))
  )
  ```
- **Conversion Rate:** `core/management/commands/abtest_report.py:77`
  ```python
  conversion_rate = (conversions / exposures * 100) if exposures > 0 else 0.0
  ```
- **Winner Determination:** `core/management/commands/abtest_report.py:98-113`
  ```python
  sorted_stats = sorted(variant_stats, key=lambda x: x['conversion_rate'], reverse=True)
  winner = sorted_stats[0]
  runner_up = sorted_stats[1]
  ```

**Example Output:**
```
=== A/B Test Summary Report ===
Generated: 2025-12-12 23:05:23 UTC
Experiment: button_label_kudos_vs_thanks
Endpoint: /218b7ae/
Total Events: 138

----------------------------------------------------------------------
Variant          Exposures       Conversions     Conversion Rate     
----------------------------------------------------------------------
kudos            50              10              20.00%              
thanks           60              18              30.00%              
----------------------------------------------------------------------

Winner: "thanks" (conversion rate: 30.00% vs 20.00%)

✓ Sample size: 110 total exposures (sufficient for basic analysis)
```

**Tests:**
- **Test File:** `core/tests/test_abtest_report_command.py`
- **Coverage:** Tests for both variants, winner logic, tie handling, low sample size warnings

---

## 10. Production Usage Documentation

### Running the Report in Production

**Command:**
```bash
python manage.py abtest_report
```

**On Render (Production):**
1. **Via Render Shell:**
   - Navigate to Render dashboard
   - Open your web service
   - Click "Shell" tab
   - Run: `python manage.py abtest_report`

2. **Via Local Connection:**
   - Connect to production database via SSH tunnel (if enabled)
   - Run command locally with production `DATABASE_URL`

**Safety Considerations:**
- ✅ **Read-Only:** Command only queries database; no modifications
- ✅ **No Side Effects:** Does not alter any data
- ✅ **Safe to Run:** Can be executed multiple times without impact
- ✅ **Filtered Query:** Only queries `ABTestEvent` table for specific experiment/endpoint
- ✅ **Efficient:** Uses Django ORM aggregations (no large data transfers)

**Environment Variables Required:**
- `DATABASE_URL` (already set in production)
- `DJANGO_SETTINGS_MODULE=config.settings` (default)

**Output:**
- Printed to stdout (console)
- Can be redirected to file: `python manage.py abtest_report > report.txt`

---

## Code Reference Map

| Component | File | Line Range |
|-----------|------|------------|
| URL Configuration | `config/urls.py` | 16-17 |
| A/B Test View | `core/views.py` | 483-584 |
| Click Handler | `core/views.py` | 587-670 |
| A/B Test Template | `templates/core/abtest.html` | 1-106 |
| ABTestEvent Model | `core/models.py` | 122-164 |
| Report Command | `core/management/commands/abtest_report.py` | 1-141 |
| Report Tests | `core/tests/test_abtest_report_command.py` | 1-245 |

---

## Verification Checklist

- ✅ URL path is `/218b7ae/` (exact match)
- ✅ Endpoint is publicly accessible (no authentication)
- ✅ All team member nicknames displayed: `stormy-deer`, `adorable-crow`, `super-giraffe`
- ✅ Button has `id="abtest"` (exact match)
- ✅ Button text is exactly "kudos" or "thanks"
- ✅ Variant assignment persisted in session (cookie-based)
- ✅ Variant stable on page reload
- ✅ Exposure events tracked (server-side + GA4)
- ✅ Click events tracked (server-side + GA4)
- ✅ Deduplication prevents double-counting exposures
- ✅ Reporting command provides exposures, clicks, CTR, and winner

---

## Conclusion

The A/B test endpoint and analytics pipeline implementation is **complete and compliant** with all requirements. The codebase demonstrates:

- **Correctness:** All functionality works as specified
- **Robustness:** Multi-layer deduplication and bot filtering
- **Reliability:** Session persistence and cache control headers
- **Observability:** Comprehensive reporting via management command
- **Maintainability:** Well-documented code with clear separation of concerns

**Ready for Production Use:** ✅

