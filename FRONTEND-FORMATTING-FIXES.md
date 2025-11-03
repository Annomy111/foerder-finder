# Frontend Formatting Issues & Fixes

## Issues Identified

### 1. Raw Text Display (FundingDetailPage.jsx:232-236)
**Problem:** `cleaned_text` displayed as raw text with `whitespace-pre-wrap`
- Shows unformatted markdown
- Potential duplicate content
- No proper spacing/formatting

### 2. Hardcoded Content (FundingDetailPage.jsx:243-283)
**Problem:** Example content instead of real database data
- "Was wird gefördert?" - hardcoded list
- "Was wird nicht gefördert?" - hardcoded list
- Should use `eligible_costs` and other DB fields

### 3. No JSON Parsing
**Problem:** Database JSON fields not parsed or displayed
- `eligibility` (eligibility_criteria)
- `target_groups`
- `evaluation_criteria`
- `requirements`
- `eligible_costs`
- `application_process`

### 4. Missing Data Display
**Problem:** Rich structured data from scraper not shown
- Contact person
- Decision timeline
- Funding period
- Application URL

## Solutions

### Fix 1: Add JSON Field Parsing Utility
Create helper to parse JSON string fields from API

### Fix 2: Replace Hardcoded Content
Use actual database fields with fallbacks

### Fix 3: Add Markdown/Text Formatting
- Limit description length
- Add line breaks
- Format lists properly
- Remove duplicate sections

### Fix 4: Improve Card Preview (FundingListPage.jsx:372-374)
- Limit cleaned_text preview to 200 chars
- Add ellipsis
- Show structured fields instead

### Fix 5: Add Structured Data Display
Show all rich fields from database:
- Eligibility criteria (list)
- Target groups (list)
- Requirements (list)
- Eligible costs (list)
- Evaluation criteria (list)
- Application process (formatted text)

## Implementation Priority

1. **HIGH**: Fix raw text display and add JSON parsing
2. **HIGH**: Replace hardcoded content with database fields
3. **MEDIUM**: Improve text formatting and spacing
4. **LOW**: Add markdown rendering library (optional)

## Files to Modify

1. `/frontend/src/pages/FundingDetailPage.jsx` - Main fixes
2. `/frontend/src/pages/FundingListPage.jsx` - Card preview
3. `/frontend/src/services/api.js` - Add field parsing (optional)
