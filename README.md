# Conversion Forkprint — Online Shopping Conversion Analytics

A course-oriented, upload-driven **Dash** analytics web app with **three Plotly charts** and **one bespoke D3 + React Dash component**. Designed for e-commerce conversion analysts using the [UCI Online Shoppers Purchasing Intention Dataset](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset).


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
3. Hover any Plotly chart for detailed information; the scatter chart is sampled for responsiveness and the displayed axes are clipped to the 99th-percentile duration range, although counts and other charts still use **all selected rows**.
4. Click a custom Forkprint glyph: its selected traffic-source/visitor-type combination filters **all three Plotly charts and KPI cards**, while the Forkprint continues to show the wider context. Click again or use **Clear fork selection**.
5. If a selection has no data, the charts display an explicit empty state.

## Four chart questions

| #   | Idiom                               | Question                                                                                                          | Interaction                                                      |
| --- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| 1   | Bar                                 | How do purchase rates compare by visitor type?                                                                    | Tooltips, shared filters                                         |
| 2   | Scatter                             | Is product-page engagement associated with exit rates, and how do purchase outcomes differ?                       | Hover, legend, shared filters                                    |
| 3   | Line                                | How does the observed conversion rate vary across recorded months?                                                | Hover, shared filters                                            |
| 4   | **Conversion Forkprint** (D3/React) | Which _traffic-source × visitor-type_ combinations show high purchase rates, and how much evidence supports each? | Click fork => updates other charts, tooltips, keyboard selection |

## Custom chart originality and limitations

- One row per traffic source; one column per visitor type (keys).
- A glyph is a _fork stem_ with two separate tips (marks).
- The upper teal branch deflects upward based on **purchase fraction** `r = purchases/sessions`: `4 + 26r` SVG units.
- The lower amber branch deflects downward based on **nonpurchase fraction** `1-r`: `4 + 26(1-r)` units.
- Shared stem thickness is proportional to **sqrt(number of sessions)**, preventing large groups from visually overwhelming small groups.
- Numerical conversion percentages and tooltips convey exact values; the visual glyph offers quick multivariate comparison.
- Selecting one fork creates a browser-to-Python `setProps` event, and Dash callbacks update three distinct standard charts.

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
