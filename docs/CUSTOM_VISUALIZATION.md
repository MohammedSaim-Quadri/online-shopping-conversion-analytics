# Conversion Forkprint — Custom D3 Visualization

## Purpose and audience

**Conversion Forkprint** is a proposed branching-glyph visual idiom developed for the **Online Shopping Conversion Analytics** Dash application. Its intended users are **e-commerce conversion optimization analysts** exploring how observed purchasing outcomes vary jointly by traffic source and visitor type, while accounting for the number of sessions in each group.

**Guiding question:** Which traffic-source × visitor-type combinations exhibit notable observed purchase conversion, and how many sessions support each rate?

**Live application:** https://conversion-forkprint.onrender.com/  
**Source repository:** https://github.com/MohammedSaim-Quadri/online-shopping-conversion-analytics

The app uses the UCI Online Shoppers Purchasing Intention dataset. Each record is a **shopping session**, not necessarily a unique customer; `Revenue` is the binary purchase-outcome indicator. The dataset contains 12,330 sessions and 1,908 purchasing sessions (15.47% overall conversion). The Forkprint uses `TrafficType`, `VisitorType`, and `Revenue`, with counts and rates computed from the currently selected data.

## Why a proposed custom idiom?

A conventional grouped bar chart would compare conversion percentages, but it would not naturally display the two complementary purchase outcomes and session volume in each mark. A heatmap could represent conversion through color, but sample size would usually require a separate annotation or tooltip. We therefore propose a **fork-shaped glyph** that combines outcome composition and group volume, repeated within a categorical matrix.

**Originality qualification:** This is a custom implementation and a proposed composite visual encoding. We **do not claim** that no similar glyph-based or branching visualization has ever existed. The written rubric requires a custom Dash component rather than a stock chart; the instructor's additional expectation of a genuinely new idiom should be confirmed with the instructor.

## Data abstraction (What)

| Attribute / derived value | Type | Key or value | Role |
|---|---|---|---|
| `TrafficType` | Categorical, coded identifier | Key | Traffic-source row |
| `VisitorType` | Categorical | Key | Fixed visitor-category column |
| `Revenue` | Binary categorical | Outcome value | Purchase indicator; summed within each group |
| Session count `n` | Quantitative, derived count | Value | Total sessions in the group; stem thickness |
| Purchases `p` | Quantitative, derived count | Value | Sessions where `Revenue = True` |
| Non-purchases `n - p` | Quantitative, derived count | Value | Complementary outcome count |
| Purchase fraction `r = p / n` | Quantitative, derived proportion | Value | Upper-branch deflection and label |
| Non-purchase fraction `1 - r` | Quantitative, derived proportion | Value | Lower-branch deflection |

Traffic-source IDs are **codes**, not human-readable marketing channel names; the visualization labels them `Source 1`, `Source 2`, etc. No ad-platform identities are inferred.

## Task abstraction (Why)

1. **Query → compare → distributions/features:** compare observed conversion fractions across `TrafficType × VisitorType` groups.
2. **Search → identify → outliers:** locate relatively high- or low-conversion groups, considering `r` and `n` together.
3. **Analyze → compare → features:** distinguish whether striking percentages occur in large or small cohorts using purchase/session counts.
4. **Query → filter → relationships:** select a cohort and inspect its browsing-duration, exit-rate, and month-level patterns in the other charts.

These tasks support **exploratory prioritization**, not causal decision making.

## Visual grammar (How)

Each **glyph** describes one observed combination of a traffic source and a visitor category.

| Marks and channels | Encoding |
|---|---|
| Row position | `TrafficType` (numeric order of the category codes) |
| Column position | `VisitorType`, in fixed order: Returning, New, Other |
| Slate horizontal stem | Group presence; stroke width encodes `sqrt(n)` |
| Teal upper curved arm | Purchasing sessions; vertical deflection proportional to `r` |
| Amber lower curved arm | Non-purchasing sessions; vertical deflection proportional to `1-r` |
| Endpoint circles | Endpoints of outcome arms |
| Text label | Conversion percentage (one decimal place) and `p/n` |
| `low n` annotation | Fewer than 30 sessions; caution marker, **not** a statistical significance test |
| Hover/focus and selection state | Group details and cross-chart filtering |

### Exact geometric rules implemented in D3

Let `n` be the group session count, `p` the count of purchasing sessions, and `r = p/n` for a group with `n > 0`.

- **Upper branch endpoint vertical offset:** `25 × r` SVG units above the common baseline. **Do not draw this branch if `p = 0`.**
- **Lower branch endpoint vertical offset:** `25 × (1-r)` SVG units below the baseline. **Do not draw this branch if `n-p = 0`.**
- **Stem stroke width:** D3 square-root scale with domain `[0, scaleMax]` and range `[1.3, 7]` SVG units. `scaleMax` is the maximum traffic-source/visitor-type group size computed from the **entire currently loaded dataset**, to keep stem widths comparable when dashboard filters change.
- **Outcome arm stroke width:** `max(1.6, 0.62 × stemStrokeWidth)` SVG units.
- **Fixed layout:** three visitor columns of 333 SVG units; rows 68 SVG units tall. Filtering hides absent glyphs rather than expanding the remaining columns. The plot container scrolls rather than rescaling glyph geometry to fit everything at once.

The percentages are calculated from observed sessions; a missing glyph indicates **no sessions for that combination in the current selection**, not zero conversion. A displayed `0.0%` accompanied by, for example, `0/9` means nine sessions occurred and none purchased. A 100% rate is similarly meaningful only in the context of its denominator.

### Why these channels?

Aligned rows and fixed category columns make groups easy to locate; vertical branch deflection makes the complementary purchase/non-purchase proportions visible. The stem adds an approximate volume cue so that a dramatic rate from a handful of sessions does not look equivalent to a rate supported by thousands of sessions. Exact numeric labels and tooltips compensate for the fact that branch angles are less precise than aligned bar lengths.

There is intentional **redundancy**: the two fractions always sum to one. The two arms communicate outcome composition, but users should rely on numeric labels when comparing small rate differences. The visual should not be interpreted as a flow of customers or as a causal transition from browsing to purchase.

## Implementation and interactivity

- **Python data preparation:** `data_utils.py` validates the UCI-compatible CSV and aggregates the selected records by `TrafficType` and `VisitorType` in `fork_data()`. Each data item carries `sessions`, `purchases`, `nonPurchases`, `rate`, and `scaleMax`.
- **Custom component:** `shopper_custom/forkprint.js` uses React for the component lifecycle and a container reference, while **D3.js directly constructs SVG** paths, circles, labels, and hit areas. It is registered as `shopper_custom.ConversionForkprint` for Dash.
- **Communication to Dash:** clicking a glyph, or activating it with **Enter/Space**, calls the component's `setProps({ selected: { traffic, visitor } })`; clicking the selected glyph again clears it. A separate **Clear fork selection** control is available.
- **Linked charts:** Dash callbacks use the selected pair to filter the bar chart, scatter plot, monthly conversion chart, and KPIs. The Forkprint keeps the broader context of the global dashboard filters so the selected cohort can still be compared with others.
- **Global controls:** visitor type, month, and day type update the plotted cohorts; a compatible CSV upload replaces the underlying data used for the visualizations.
- **Detail and accessibility:** glyphs support hover tooltips and keyboard activation with accessible labels. Fixed dimensions and scrolling improve stability but require horizontal navigation on narrow displays.

The app relies on a D3 script loaded from a CDN, so loading the custom component requires that the browser can retrieve D3. The React wrapper is an implementation choice for Dash integration; React was **not a separate requirement of the assignment**.

## Effectiveness, expressiveness, and limitations

**Effectiveness:** The glyphs jointly expose visitor category, traffic-source code, conversion fraction, and cohort volume, and selection links an interesting group to behavioral and monthly context. Rates and denominators are printed because branch deflection is not a highly precise comparison channel.

**Expressiveness:** Only observed groups receive glyphs. Zero-outcome branches are omitted, and the labels show the observed numerator/denominator. Filtering updates the actual grouped counts; rates are not fabricated for absent categories. The app signals groups under 30 sessions.

**Limitations and safeguards:**

1. The encoding is less familiar than ordinary bars or a heatmap and requires explanation.
2. Branch deflection and redundant complementary arms are not ideal for precise ranking; use the printed percentages for exact comparisons.
3. Stem thickness shows volume but is not a substitute for the numeric denominator; square-root scaling intentionally compresses extreme differences.
4. Small-sample rates may be unstable. `low n` is an interpretation warning, **not** a confidence interval or a significance threshold.
5. Traffic-source codes have no supplied semantic mapping to named acquisition platforms.
6. The source is observational, with session-level records; differences between groups do **not** prove that traffic source or visitor status causes conversion.
7. The component needs a browser-level test for loading, scrolling, tooltip behavior, keyboard access, and propagation of the selected cohort to other charts.

## Suggested demonstration

1. Open the dashboard with all visitors selected and point out the three fixed visitor columns and the traffic-source rows.
2. Compare an ordinary-sized group with a `low n` group; read out the numerator/denominator rather than only the percentage.
3. Show a **0%** group with no teal purchase branch, explaining that zero purchases is different from missing data.
4. Select a Forkprint glyph and show how the other three charts and KPIs change to that cohort.
5. Clear the selection and explain why the custom glyph supplements rather than replaces standard bar/scatter/line charts.

## Source and attribution

- Sakar, C. O., et al., “Real-time prediction of online shoppers' purchasing intention,” *Neural Computing and Applications* (2019).
- UCI Machine Learning Repository, **Online Shoppers Purchasing Intention Dataset**, DOI: https://doi.org/10.24432/C5F88Q. Dataset license: **CC BY 4.0**, as listed by UCI.
- Implementation: [`shopper_custom/forkprint.js`](../shopper_custom/forkprint.js), [`data_utils.py`](../data_utils.py), and [`app.py`](../app.py).

This document describes the project's custom visualization and its design rationale; it is not a claim of independent validation or clinical/business effectiveness.
