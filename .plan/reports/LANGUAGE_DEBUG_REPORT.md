# Language Mismatch Investigation Report

## Executive Summary

**ROOT CAUSE IDENTIFIED**: The API client is using the wrong base URL, causing automatic redirects to the Portuguese forum.

- ❌ **Current**: `https://community.shopify.com` → redirects to Portuguese (`/c/pt-br/18.json`)
- ✅ **Correct**: `https://community.shopify.dev` → serves English content

## Problem Description

The database contains Portuguese content despite expecting English "Webhooks and Events" forum data. The browser shows English content at the correct URL, but our API client was fetching Portuguese data.

## Investigation Results

### 1. API Endpoint Testing

**English Forum (community.shopify.dev):**
```
URL: https://community.shopify.dev/c/webhooks-and-events/18.json
Status: 200
Redirects: None
First Topic: "About the Webhooks and Events category"
Language: ENGLISH ✅
```

**Current API Client Base URL (community.shopify.com):**
```
URL: https://community.shopify.com/c/webhooks-and-events/18.json
Status: 200 (after redirect)
Redirects: YES - 301 redirect detected
  1. [301] https://community.shopify.com/c/webhooks-and-events/18.json
  Final: [200] https://community.shopify.com/c/pt-br/18.json
First Topic: "Cobrança indevida no meu cartão"
Language: PORTUGUESE ❌
```

### 2. Database Analysis

```sql
SELECT DISTINCT category_id FROM topics;
-- Result: [18]

SELECT id, title FROM topics LIMIT 3;
-- Results (Portuguese):
19901: Código para aumentar o tamanho da logotipo...
22129: NIF no formulário de morada de faturação
46133: provedor de pagamento e.rede
```

### 3. Header Testing

**Finding**: Accept-Language headers do NOT affect the response when using the correct domain.

- `community.shopify.dev` always returns English (regardless of headers)
- `community.shopify.com` automatically redirects to `/c/pt-br/` (Portuguese)

The redirect is **domain-based**, not header-based.

## Root Cause Analysis

### Location in Code

File: [`src/forum_analyzer/collector/api_client.py`](src/forum_analyzer/collector/api_client.py:46)

```python
class ForumAPIClient:
    """Async HTTP client for Shopify Developer Forum API."""

    BASE_URL = "https://community.shopify.com"  # ❌ WRONG - Portuguese forum
```

### Why This Happened

1. `community.shopify.com` appears to be a localized domain that redirects based on geo-location or default locale
2. It automatically redirects `/c/webhooks-and-events/18.json` to `/c/pt-br/18.json`
3. The English forum is hosted at `community.shopify.dev`, not `.com`
4. Category ID 18 exists in both forums but contains different language content

### Impact

- All collected data is in Portuguese
- Database contains 60 topics in Portuguese instead of English
- Analysis and reports will be in Portuguese
- Topic titles, excerpts, and content are all Portuguese

## Solution

### Required Fix

Change the base URL in [`api_client.py`](src/forum_analyzer/collector/api_client.py:46):

```python
# BEFORE (wrong)
BASE_URL = "https://community.shopify.com"

# AFTER (correct)
BASE_URL = "https://community.shopify.dev"
```

### Steps to Implement

1. **Update API Client**
   ```python
   # src/forum_analyzer/collector/api_client.py line 46
   BASE_URL = "https://community.shopify.dev"
   ```

2. **Clear Existing Data**
   ```bash
   # Remove Portuguese data
   rm data/database/forum.db
   rm data/checkpoints/checkpoint_18_category_page.json
   
   # Reinitialize database
   python scripts/init_db.py
   ```

3. **Re-collect Data**
   ```bash
   # Collect fresh English data
   python -m forum_analyzer.cli collect
   ```

### Verification

After the fix, verify with:

```python
import requests
url = "https://community.shopify.dev/c/webhooks-and-events/18.json"
response = requests.get(url)
data = response.json()
first_title = data['topic_list']['topics'][0]['title']
print(f"First topic: {first_title}")
# Expected: "About the Webhooks and Events category"
```

## Testing Evidence

All tests are available in:
- [`debug_language.py`](debug_language.py) - Comprehensive language detection tests
- [`test_base_url.py`](test_base_url.py) - Base URL redirect verification
- [`check_db_config.py`](check_db_config.py) - Database content analysis

## Recommendations

1. ✅ **Immediate**: Update `BASE_URL` to `community.shopify.dev`
2. ✅ **Immediate**: Clear Portuguese data and re-collect
3. 📝 **Future**: Add validation to verify language of collected data
4. 📝 **Future**: Add configuration option for forum locale if multi-language support is needed
5. 🔒 **Best Practice**: Add integration test to verify English content is being collected

## Conclusion

The issue was **not** with:
- API headers
- Category ID (18 is correct for both English and Portuguese)
- Endpoint format (`/c/webhooks-and-events/18.json`)
- Client configuration

The issue **was**:
- Wrong base domain (`community.shopify.com` instead of `community.shopify.dev`)
- Automatic redirect to Portuguese locale (`/c/pt-br/`)

**Fix**: Change one line in `api_client.py` from `.com` to `.dev`.

---

## Resolution (October 2, 2025)

### ✅ Fix Implemented

The base URL issue has been successfully resolved:

**Changes Made:**

1. **Updated API Client** ([`api_client.py`](src/forum_analyzer/collector/api_client.py))
   - Removed hardcoded `BASE_URL` class constant
   - Added `base_url` as constructor parameter with default `https://community.shopify.dev`
   - Updated `__aenter__` method to use instance variable

2. **Updated Settings** ([`settings.py`](src/forum_analyzer/config/settings.py))
   - Changed default `base_url` from `.com` to `.dev`

3. **Updated Orchestrator** ([`orchestrator.py`](src/forum_analyzer/collector/orchestrator.py))
   - Modified to pass `base_url` from settings to API client

4. **Configuration File** ([`config.yaml`](config/config.yaml))
   - Already contained correct URL: `https://community.shopify.dev`

### Verification Process

1. **Test Collection (2 pages)**
   - Collected 60 topics, 266 posts
   - Verified English content:
     - "About the Webhooks and Events category"
     - "Webhooks URLs are not updating with server-restarts"
     - "Question Regarding Webhook for Returns Created via returnCreateMutation"

2. **Full Collection Results**
   - **Total Topics:** 271
   - **Total Posts:** 1,201
   - **Total Users:** 324
   - **Date Range:** September 26, 2024 to October 1, 2025
   - **Database Size:** 1.62 MB
   - **Language:** English ✅

3. **Analysis Report Generated**
   - Top keywords: webhook, webhooks, app, shopify, update, product, orders, api
   - Problem categories: Webhook Delivery (73.1%), General Questions (18.8%), Payload Data (3.7%)
   - All content confirmed as English technical discussions

### Final Status

✅ **RESOLVED**: The system now correctly collects English content from `https://community.shopify.dev`
✅ **VERIFIED**: Database contains comprehensive English data from September 2024 to present
✅ **ANALYSIS**: Generated analysis report shows relevant English technical keywords and topics
✅ **DOCUMENTED**: All changes documented and configuration updated

The fix was successful and the forum analyzer is now collecting the correct English content from the Shopify Developer Forum.