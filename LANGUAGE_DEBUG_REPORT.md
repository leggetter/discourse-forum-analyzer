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