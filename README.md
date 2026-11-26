# Conversion Forkprint — Online Shopping Conversion Analytics

A course-oriented, upload-driven **Dash** analytics web app with **three Plotly charts** and **one bespoke D3 + React Dash component**. Designed for e-commerce conversion analysts using the [UCI Online Shoppers Purchasing Intention Dataset](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset).

## Live Application

**Dashboard:** https://conversion-forkprint.onrender.com/

**GitHub Repository:** https://github.com/MohammedSaim-Quadri/online-shopping-conversion-analytics

The application is publicly hosted on Render. Users can explore the
bundled UCI dataset or upload a compatible CSV to regenerate the
visualizations.

Note: The Render free-tier service may take additional time to start
after a period of inactivity.


## Quick start — Windows PowerShell

```powershell
cd shopper_project
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:8050`. The authentic file is already in `data/`. You can also upload another compatible CSV through the app UI.

On macOS/Linux:

```bash
cd shopper_project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Requires:** Python 3.10–3.12 recommended, internet access to install requirements and retrieve D3 from the jsDelivr CDN. `requirements.txt` pins major versions but not exact patch versions; lock after testing on your host if you want reproducible deployment.

## Interactions

1. Upload a valid CSV with the 18 original UCI columns. All four visualizations and KPI values are recalculated from the uploaded rows.
2. Filter by visitor type, month, and day type; these are independent controls and trigger Python Dash callbacks.
3. Hover over Plotly charts for detailed information. The scatter
   chart includes all filtered sessions using Plotly Scattergl,
   without sampling. The default 99th-percentile duration zoom
   changes only the visible x-axis window; users can switch to
   Full range to inspect outliers. No sessions are removed from
   the underlying calculations.
4. Click a custom Forkprint glyph: its selected traffic-source/visitor-type combination filters **all three Plotly charts and KPI cards**, while the Forkprint continues to show the wider context. Click again or use **Clear fork selection**.
5. If a selection has no data, the charts display an explicit empty state.

## Four chart questions

| #   | Idiom                               | Question                                                                                                          | Interaction                                                      |
| --- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| 1   | Bar                                 | How do purchase rates compare by visitor type?                                                                    | Tooltips, shared filters                                         |
| 2   | Scatter                             | Is product-page engagement associated with exit rates, and how do purchase outcomes differ?                       | Hover, legend, shared filters                                    |
| 3   | Line                                | How does the observed conversion rate vary across recorded months?                                                | Hover, shared filters                                            |
| 4   | **Conversion Forkprint** (D3/React) | Which _traffic-source × visitor-type_ combinations show high purchase rates, and how much evidence supports each? | Click fork => updates other charts, tooltips, keyboard selection |

### Interpreting the Monthly Chart

The monthly chart displays conversion rates for months represented
in the selected data.

- Line breaks indicate months without recorded sessions.
- A value of 0% indicates that sessions occurred but none resulted
  in a purchase.
- Tooltips display the number of sessions, purchases, and observed
  conversion rate.
- Months with fewer than 30 sessions are flagged for cautious
  interpretation.

The dataset does not contain full calendar timestamps or years.
Therefore, this visualization represents month-aggregated
comparisons rather than a continuous multi-year time series.

## Custom chart originality and limitations

- Rows represent traffic sources (`TrafficType`), and fixed columns
  represent visitor categories (`VisitorType`).
- Each traffic-source/visitor-type combination is represented by a
  custom branching glyph.
- The upper teal branch deflects upward according to the
  purchase fraction `r = purchases / sessions`,
  using `25 × r` SVG units.
- The lower amber branch deflects downward according to the
  non-purchase fraction `1 - r`,
  using `25 × (1 - r)` SVG units.
- Branches are omitted when their corresponding outcome count
  is zero.
- Stem thickness uses square-root scaling, referenced against
  the maximum traffic-source/visitor-type group volume in the
  uploaded dataset, preserving comparability across filters.
- Exact purchase/session counts and conversion percentages
  are shown. Groups with fewer than 30 sessions are marked
  `low n`.
- Glyph columns have fixed dimensions, with scrolling available
  when needed.
- Clicking or keyboard-activating a glyph filters the other
  three Plotly charts and the dashboard KPIs.

This is a **proposed composite encoding**, not a globally verified claim that no previous researcher has ever used fork glyphs. It intentionally combines grouped comparison, bifurcation geometry, and a volume cue in a distinctive way. A potential issue is that proportional fork deflection may be less immediately familiar than a bar; the numerical labels and explicit legend are therefore necessary.

**No causal inference:** conversion is the sample proportion of sessions whose `Revenue` field is true, not a measured intervention effect. `PageValues` can be associated with revenue and should not be interpreted as an independent causal predictor. The source does not contain calendar years or a timestamp; a line across named months is **month-aggregate seasonal comparison**, not a longitudinal time-series trend.

## Data cleaning

- Validate the original 18 fields and reject incompatible upload schemas.
- Convert numeric measurements and encoded categorical IDs to their intended types; traffic IDs become strings for grouping.
- Parse Boolean `Revenue` and `Weekend` consistently (true/false and 0/1 supported).
- Normalize `Jun` to `June`; reject unrecognized month tokens.
- Reject missing/unparseable numeric data or invalid exit-rate and product-duration values, rather than quietly deleting rows.
- Calculate conversion as the exact ratio `purchasing_sessions / all_sessions` after active filters.
- **No train/test split** is needed: this is descriptive visualization, not predictive modeling.
- Browser and operating-system IDs are coded categories, not continuous measurements.

## Tests

```bash
python -m pytest -q
node --check shopper_custom/forkprint.js    # optional: if Node.js installed
```

The data tests verify schema validation, filter behavior, and preservation of total session/purchase counts in glyph aggregation.

## Deploy on Render

1. The official CSV is already in `data/`; preserve the CC BY 4.0 attribution when distributing.
2. Push this project to GitHub. Do not commit `.venv/` or API credentials.
3. Create a Render web service from the repository, or use `render.yaml` as a Blueprint.
4. Build command: `pip install -r requirements.txt`; start: `gunicorn app:server --bind 0.0.0.0:$PORT`.
5. Visit the actual public URL, verify all four charts and CSV upload, click a fork, then refresh from an anonymous browser before submitting. Free-tier hosting may sleep.

## Dataset citation

Sakar, C. O. et al., “Real-time prediction of online shoppers' purchasing intention,” _Neural Computing and Applications_ (2019). Dataset: UCI Machine Learning Repository, dataset 468, DOI: [10.24432/C5F88Q](https://doi.org/10.24432/C5F88Q), **CC BY 4.0** (as listed by UCI). Verify the precise bibliographic format required by your instructor.

## Blank browser page troubleshooting

If Flask starts but the page stays blank, open DevTools (F12) > Console. The custom JavaScript is registered via the `shopper_custom` package-level `_js_dist` so Dash can serve it through `/_dash-component-suites/`. If there is still an error, capture the first red Console entry and verify the D3 CDN loads (internet required). Run Ctrl+C then `python app.py` and Ctrl+F5 to clear stale JavaScript.
