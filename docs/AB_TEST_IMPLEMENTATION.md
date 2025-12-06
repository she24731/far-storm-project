# A/B Test Implementation Documentation

## Overview

This document explains the A/B test implementation for the button label experiment (`button_label_kudos_vs_thanks`) on the `/218b7ae/` endpoint.

---

## Experiment Details

- **Experiment Name:** `button_label_kudos_vs_thanks`
- **Endpoint:** `/218b7ae/`
- **Variants:**
  - **Variant A:** "kudos"
  - **Variant B:** "thanks"
- **Split:** 50/50 random assignment
- **Persistence:** Cookie-based (30-day expiration)

---

## Where the A/B Logic Lives

### 1. Django View (`core/views.py`)

**Function:** `abtest_view(request)`

- Handles variant assignment (random 50/50 split)
- Manages cookie persistence (`ab_variant` cookie, 30-day expiration)
- Logs server-side exposure events to PostgreSQL
- Supports debug forcing via URL parameter

**Key Code Location:**
```python
# Lines 403-496 in core/views.py
def abtest_view(request):
    # Variant assignment logic
    # Cookie persistence
    # Server-side logging
```

### 2. Template (`templates/core/abtest.html`)

- Renders the button with variant text
- Sends Google Analytics events (`ab_exposure` and `ab_button_click`)
- Handles client-side click tracking

### 3. Click Logging Endpoint (`core/views.py`)

**Function:** `abtest_click(request)`

- **URL:** `/218b7ae/click/`
- Logs button clicks (conversions) server-side
- Called via AJAX from the template

### 4. Database Model (`core/models.py`)

**Model:** `ABTestEvent`

Stores all A/B test events (exposures and conversions) in PostgreSQL.

**Fields:**
- `experiment_name`: Experiment identifier
- `variant`: 'kudos' or 'thanks'
- `event_type`: 'exposure' or 'conversion'
- `endpoint`: '/218b7ae/'
- `user_id`: User ID if authenticated (nullable)
- `session_id`: Session identifier (from cookie or IP hash)
- `created_at`: Timestamp
- `is_forced`: True if variant was forced via `?force_variant` parameter

---

## Usage Guide

### Forcing Variants (Manual QA)

To force a specific variant for testing, add a query parameter to the URL:

- **Force Variant A ("kudos"):**
  ```
  https://yale-newcomer-survival-guide.onrender.com/218b7ae/?force_variant=a
  ```

- **Force Variant B ("thanks"):**
  ```
  https://yale-newcomer-survival-guide.onrender.com/218b7ae/?force_variant=b
  ```

**Note:** Forced variants are logged but marked with `is_forced=True`, and can be excluded from analysis using the `--exclude-forced` flag.

### Logging Events

Events are logged automatically:

1. **Exposure Events:**
   - Logged server-side when the page loads
   - Also sent to Google Analytics as `ab_exposure` event

2. **Conversion Events:**
   - Logged server-side when the button is clicked
   - Also sent to Google Analytics as `ab_button_click` event

### Analyzing Results

#### Check Traffic Split

Verify that traffic is being split roughly 50/50 between variants:

```bash
python manage.py ab_check_traffic_split --experiment=button_label_kudos_vs_thanks
```

**Options:**
- `--event-type`: `exposure`, `conversion`, or `all` (default: `exposure`)
- `--exclude-forced`: Exclude forced variants from analysis

**Output includes:**
- Total events per variant
- Percentage distribution
- Sample ratio mismatch detection (flags if split is < 40% or > 60%)
- Click-through rates (if analyzing exposures)

#### Statistical Analysis

Run the full statistical analysis:

```bash
python manage.py ab_analyze_button_label --experiment=button_label_kudos_vs_thanks
```

**Options:**
- `--exclude-forced`: Exclude forced variants
- `--confidence-level`: Confidence level for intervals (default: 0.95)

**Output includes:**
1. **Hypotheses Section:**
   - Null hypothesis (H₀)
   - Alternative hypothesis (H₁)

2. **Numerical Results:**
   - Exposures, conversions, and conversion rates per variant
   - Effect size (absolute and relative)
   - Z-score and p-value
   - 95% confidence interval

3. **Executive Summary:**
   - Plain English interpretation
   - Statistical significance assessment
   - Recommendation for deployment

---

## Google Analytics Events

### Event 1: `ab_exposure`

**Triggered:** On page load

**Parameters:**
- `experiment`: `'button_label_kudos_vs_thanks'`
- `variant`: `'kudos'` or `'thanks'`
- `endpoint`: `'/218b7ae/'`
- `event_category`: `'abtest'`

### Event 2: `ab_button_click`

**Triggered:** On button click

**Parameters:**
- `experiment`: `'button_label_kudos_vs_thanks'`
- `variant`: `'kudos'` or `'thanks'`
- `endpoint`: `'/218b7ae/'`
- `event_category`: `'abtest'`
- `event_label`: Variant name
- `page_title`: Document title

---

## Database Schema

The `ABTestEvent` table structure:

```sql
ab_events (
    id SERIAL PRIMARY KEY,
    experiment_name VARCHAR(100) NOT NULL,
    variant VARCHAR(20) NOT NULL,
    event_type VARCHAR(20) NOT NULL,  -- 'exposure' or 'conversion'
    endpoint VARCHAR(200) NOT NULL DEFAULT '/218b7ae/',
    user_id VARCHAR(100) NULL,
    session_id VARCHAR(100) NOT NULL,
    ip_address INET NULL,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    is_forced BOOLEAN DEFAULT FALSE
)
```

**Indexes:**
- `experiment_name`, `variant`, `event_type`
- `experiment_name`, `created_at`
- `endpoint`, `event_type`
- `user_id`, `session_id` (individual indexes)

---

## Handling Edge Cases

### Insufficient Data

Both analysis commands handle cases where:
- No events have been collected yet
- Only one variant has data
- Sample sizes are too small

In these cases, the commands print friendly error messages and recommendations.

### Failed Event Logging

Server-side event logging is wrapped in try-except blocks to prevent page errors if logging fails. Events are logged asynchronously and failures are silently ignored to maintain user experience.

---

## Migration Notes

If you're deploying this for the first time:

1. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

2. **Verify the table:**
   ```bash
   python manage.py dbshell
   ```
   Then check: `\d core_abtestevent` (PostgreSQL)

---

## Testing Checklist

Before deploying to production:

- [ ] Verify variant assignment works (visit endpoint multiple times)
- [ ] Test forced variants (`?force_variant=a` and `?force_variant=b`)
- [ ] Confirm server-side events are logged (check database)
- [ ] Verify GA events appear in Google Analytics (Real-Time view)
- [ ] Test click tracking (click button, verify conversion event)
- [ ] Run traffic split analysis (`ab_check_traffic_split`)
- [ ] Run statistical analysis (`ab_analyze_button_label`)
- [ ] Test with insufficient data (commands should handle gracefully)

---

## Troubleshooting

### Events Not Appearing in Database

1. Check that migrations have been run: `python manage.py migrate`
2. Verify the view is logging events (check logs for exceptions)
3. Confirm database connection is working

### GA Events Not Firing

1. Check browser console for JavaScript errors
2. Verify GA snippet is loaded in `base.html`
3. Use GA DebugView or Real-Time reports to verify events

### Analysis Commands Show No Data

1. Ensure events have been logged (check database directly)
2. Verify experiment name matches exactly: `button_label_kudos_vs_thanks`
3. Check that both variants have been shown (not just one)

---

## Links

- **Production A/B Test:** https://yale-newcomer-survival-guide.onrender.com/218b7ae/
- **Staging A/B Test:** https://yale-newcomer-survival-guide-staging.onrender.com/218b7ae/
- **Google Analytics:** https://analytics.google.com/

