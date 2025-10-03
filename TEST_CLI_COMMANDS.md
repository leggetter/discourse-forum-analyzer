# Manual CLI Testing Guide

This guide provides step-by-step commands to verify the LLM-driven category discovery implementation works correctly.

## Prerequisites

- You have already run `forum-analyzer collect` and have data in your database
- Python environment is set up with all dependencies

## Test Sequence

### Step 1: Clear Existing Problem Themes

Start fresh by clearing any existing themes:

```bash
python -c "
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from src.forum_analyzer.collector.models import ProblemTheme
from src.forum_analyzer.config.settings import get_settings

settings = get_settings()
engine = create_engine(settings.database.url)

with Session(engine) as session:
    result = session.execute(delete(ProblemTheme))
    session.commit()
    print(f'✓ Cleared {result.rowcount} problem themes')
"
```

You can also clear the analysis results if desired:

```bash
python -c "
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from src.forum_analyzer.collector.models import LLMAnalysis
from src.forum_analyzer.config.settings import get_settings

settings = get_settings()
engine = create_engine(settings.database.url)

with Session(engine) as session:
    result = session.execute(delete(LLMAnalysis))
    session.commit()
    print(f'✓ Cleared {result.rowcount} LLM analyses')
"
```

### Step 2: Test CLI Without Themes

Run llm-analyze when no themes exist. **This should display the helpful tip message:**

```bash
forum-analyzer llm-analyze --limit 1
```

**Expected Output:**
```
💡 Tip: Run 'forum-analyzer themes' first to discover categories from your data
   This will help the LLM use relevant categories instead of generic ones.
```

**What this verifies:**
- ✅ CLI detects absence of themes
- ✅ Helpful guidance is displayed to users
- ✅ LLM will use free-form categorization (no predefined categories)

### Step 3: Discover Categories from Data

Run the themes command to discover natural categories from your collected data:

```bash
forum-analyzer themes --min-topics 3
```

**What happens:**
- Analyzes all collected topics
- Identifies common problem patterns
- Groups similar issues together
- Saves discovered themes to database

### Step 4: View Discovered Themes

Check what themes were discovered:

```bash
python -c "
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from src.forum_analyzer.collector.models import ProblemTheme
from src.forum_analyzer.config.settings import get_settings

settings = get_settings()
engine = create_engine(settings.database.url)

with Session(engine) as session:
    themes = session.execute(select(ProblemTheme)).scalars().all()
    print(f'\\nFound {len(themes)} themes:')
    for theme in themes:
        print(f'  - {theme.theme_name} ({theme.topic_count} topics)')
"
```

**Expected:** List of discovered theme names that represent actual problems in your forum

### Step 5: Test CLI With Themes Present

Run llm-analyze again. **This time the tip message should NOT appear:**

```bash
forum-analyzer llm-analyze --limit 1
```

**Expected:**
- NO tip message about running themes first
- Analysis proceeds using discovered categories
- Categories from themes are used in LLM prompts

**What this verifies:**
- ✅ CLI detects presence of themes
- ✅ No unnecessary tip message shown
- ✅ LLM will use discovered theme names as categories

### Step 6: Verify Categories Are Used (Optional)

To confirm the discovered categories are being passed to the LLM, you can add temporary debug logging:

```bash
python -c "
from src.forum_analyzer.analyzer.llm_analyzer import LLMAnalyzer
from src.forum_analyzer.config.settings import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

settings = get_settings()
analyzer = LLMAnalyzer(settings)
engine = create_engine(settings.database.url)

with Session(engine) as session:
    categories = analyzer._get_categories(session)
    if categories:
        print(f'\\n✓ LLM will use these categories:')
        for cat in categories:
            print(f'  - {cat}')
    else:
        print('\\n✓ LLM will use free-form categorization (no predefined categories)')
"
```

## Success Criteria

After running these tests, you should have verified:

1. ✅ **Without themes:** CLI shows helpful tip message
2. ✅ **Without themes:** `_get_categories()` returns `None` (enables free-form)
3. ✅ **Themes command:** Successfully discovers categories from actual data
4. ✅ **With themes:** CLI does NOT show tip message
5. ✅ **With themes:** `_get_categories()` returns list of discovered theme names
6. ✅ **Analysis:** Uses appropriate categorization based on theme presence

## Implementation Verified

The correct workflow is now in place:

```
collect → themes → llm-analyze → ask
```

Users no longer need to guess categories before analyzing unknown forums!