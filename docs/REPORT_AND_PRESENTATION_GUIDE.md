# Final report and presentation preparation
**Live Application:** https://conversion-forkprint.onrender.com/

**GitHub Repository:** https://github.com/MohammedSaim-Quadri/online-shopping-conversion-analytics

## Strict deliverables in the uploaded course instructions

- Dash web app hosted publicly, with CSV upload, four interactive charts, at least two Dash callback-driven controls, and an interaction in one chart that updates another.
- A custom **Dash component**, authored independently in React/D3 (not a standard Plotly chart).
- Report **3–5 pages including references**, IEEE double-column conference format. Page 1: title, team member names, app URL, GitHub URL, abstract (3–5 sentences).
- GitHub repo with README, requirements, and dataset.
- Presentation **6–8 minutes**; every member speaks; live demo and backup screenshots or recording.

## Data abstraction (What)

| Attribute               | Data type            | Key/value role | Uses                             |
| ----------------------- | -------------------- | -------------- | -------------------------------- |
| Month                   | ordinal              | key            | line chart, filter               |
| VisitorType             | categorical          | key            | bar and fork glyph               |
| TrafficType             | categorical coded ID | key            | fork rows                        |
| Weekend                 | categorical/binary   | key            | filter                           |
| Revenue                 | categorical/binary   | value/outcome  | conversion numerator             |
| ProductRelated_Duration | quantitative         | value          | scatter x                        |
| ExitRates               | quantitative         | value          | scatter y                        |
| ProductRelated          | quantitative count   | value          | scatter tooltip                  |
| PageValues              | quantitative         | value          | ancillary tooltip                |
| Administrative_Duration | quantitative         | value          | available for future exploration |

UCI publishes 12,330 sessions and 18 attributes. Verify source value counts on the actual CSV before writing specific insight statements.

## Task abstraction (Why)

1. **Query → compare → features:** compare observed purchase rate by `VisitorType` for visitor-segment prioritization.
2. **Analyze → correlate → relationships:** examine `ProductRelated_Duration` versus `ExitRates`, distinguishing `Revenue` outcomes.
3. **Analyze → summarize → trends:** compare conversion by ordered `Month` (only represented months; no year-level inference).
4. **Search → compare → categorical combinations:** find `TrafficType × VisitorType` combinations with notable conversion fractions and inspect sample sizes.

Audience: **e-commerce conversion optimization analysts**. Decisions supported: which segments deserve more investigation, which traffic combinations differ, and whether browsing behavior appears associated with conversion. The design is exploratory and does not prove causal relationships.

## Visualization justification templates (customize with actual observed findings)

- **Visitor bars:** marks = bars, length = observed conversion percentage, nominal visitor labels on aligned vertical position. Reject pie chart because precisely comparing several close rates is harder without a common baseline.
- **Engagement scatter:** marks = individual session points
  (all filtered records are included using Plotly Scattergl);
  x = product-related browsing duration, y = exit rate,
  color = purchase outcome. A 99th-percentile duration zoom
  improves readability without excluding records from the
  underlying data or calculations.
- **Monthly line:** marks = points and lines across observed ordered months, vertical position = session conversion fraction. Reject pie chart because it loses order and tempts interpretation as parts of a whole; explicitly mention the dataset has no year information.
- **Forkprint (bespoke):** marks = paired diverging fork branches, stem, endpoint circles, text; rows = traffic-source IDs, columns = visitor types, upper tip deflection = purchase fraction, lower tip deflection = nonpurchase fraction, stem width = sqrt(session count). Reject ordinary heatmap: it encodes rate by color but sample size and two outcome complements are difficult to read together without a tooltip. Explain React + D3 SVG generation, `setProps` click selection, and Dash callback linkage.

## Controls: report justification sentences

- Visitor filter: “Which observed purchasing patterns remain within a particular visitor segment?”
- Month filter: “Do the within-sample segment patterns change when only certain recorded months are analyzed?”
- Day filter: “Do weekend sessions exhibit different associations from weekday sessions?”
- Fork click selection: “What do the standard charts reveal specifically about this traffic-source/visitor-type combination?”
- CSV upload: “Do these interpretations remain valid on another dataset with the same 18-column schema?”

## Example use case narrative

An analyst filters to a recorded month and weekend traffic, observes the visitor conversion bars, inspects scatter overlap, and selects a traffic/visitor Forkprint glyph. All three standard charts update to that cohort, while the bespoke glyph retains its comparative context. The analyst records a _hypothesis for further testing_, not a claim of causation.

## Presentation suggested breakdown

- 0:00–1:00 problem, source, audience
- 1:00–2:00 bars and temporal comparison
- 2:00–3:00 engagement scatter
- 3:00–4:30 explain and interact with original Forkprint
- 4:30–5:30 upload + cross-filter demonstration
- 5:30–6:30 findings (replace placeholders with verified findings)
- 6:30–7:30 constraints, team contributions, conclusion

**Do not fill in 'findings' from synthetic demonstration data.** Use the authentic UCI records and verify all percentages first.
