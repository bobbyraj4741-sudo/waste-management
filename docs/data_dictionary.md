# Data Dictionary - 2024 Waste Data Interrogator (harmonised)

Source: Environment Agency, *2024 Waste Data Interrogator* (calendar year 2024),
Defra Data Services Platform. Two workbooks - **Wastes Received** and **Wastes
Removed** - are merged into one long table of *waste movements*, one row per
(facility, waste code, counterparty, fate) record.

A `direction` column distinguishes the two:
- `received` - a load of waste **arriving at** the regulated facility (the
  counterparty is the *origin* the waste came from).
- `removed`  - a load of waste **leaving** the regulated facility (the
  counterparty is the *destination* the waste was sent to).

| Column | Meaning |
|---|---|
| `direction` | `received` or `removed` (which workbook the row came from). |
| `permit` | Environment Agency permit number - unique id of the **regulated facility**. Used as the graph node key. |
| `site_name` | Human-readable facility name. |
| `operator` | Company operating the facility. |
| `permit_type` | Permit class, e.g. `A9 : Hazardous Waste Transfer Station`. |
| `site_category` | High-level site category: Transfer, Treatment, Landfill, Incineration, MRS, Storage, Processing, Mobile Plant, ... |
| `facility_type` | Finer facility type, e.g. CA Site, Metal Recycling, Physical-Chemical Treatment. |
| `facility_region` | Region the facility itself sits in (Facility RPA). |
| `facility_wpa` / `facility_district` | Waste Planning Authority / district of the facility. |
| `easting` / `northing` | British National Grid coordinates of the facility. |
| `post_code` | Facility post code. |
| `form` | Physical form of the waste (Solid / Liquid / ...). |
| `basic_waste_cat` | Broad category: Hhold/Ind/Com, Hazardous, Inert/C+D. |
| `ewc_chapter` / `ewc_sub_chapter` | European Waste Catalogue chapter / sub-chapter. |
| `ewc_waste_desc` | EWC textual description of the waste. |
| `waste_code` | Six-digit EWC waste code. |
| `counterparty` | The other end of the movement: **origin** place (received) or **destination** place (removed). NOTE: recorded as a *place name / WPA*, not a counterparty permit id. |
| `counterparty_wpa` / `counterparty_region` | WPA / region of that origin/destination. |
| `fate` | What happens to the waste: Recovery, Landfill, Incineration, Treatment, Transfer (D), Long term storage, Other Fate. Primary recovery-vs-disposal signal. |
| `r_and_d_code` | EU Waste Framework Directive operation code. `R..` = recovery operation, `D..` = disposal operation. |
| `tonnes` | Quantity of waste in tonnes for the record (edge weight). |
| `soc_category` / `soc_sub_category` | Standard Order Classification of the waste. |

## Glossary (Module 1 completion check)

- **Waste site**: a facility regulated by an Environment Agency permit that
  receives, stores, treats, or disposes of waste.
- **Waste received**: waste arriving at a permitted site from an origin.
- **Waste removed**: waste leaving a permitted site to a destination.
- **Recovery**: operations (R-codes) that put waste back to beneficial use -
  recycling, energy recovery, reprocessing. High recovery = good circularity.
- **Disposal**: operations (D-codes) with no recovery value - chiefly landfill
  and non-energy incineration. High disposal = poor circularity.
- **Transfer station**: a site that consolidates/bulks waste and sends it on
  without treating it; waste "passes through".

## Important modelling limitation

The `counterparty` field is a **place/region name, not a counterparty permit
id**. The dataset therefore does not let us link facility A directly to facility
B. The waste-flow graph is built as a **bipartite-style directed graph** between
regulated facilities (permits) and places (origins/destinations): places ->
facilities (received) and facilities -> places (removed). This is the honest
network the public data supports; producer-level facility-to-facility links are
commercially confidential and out of scope.
