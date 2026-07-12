# Data Quality Report - 2024 Waste Data Interrogator

## Row accounting
- Raw movement rows: **489,453**
- Clean movement rows: **489,399**
- Rows dropped (missing permit / tonnes, negative tonnes): **54**
- Exact duplicate rows in raw table: **100**
  (kept intentionally - identical multi-load records are legitimate repeat movements)

## Missing values in key fields (raw)
| Field | % missing |
|---|---|
| `permit` | 0.0% |
| `site_name` | 0.0% |
| `waste_code` | 0.0% |
| `counterparty` | 0.0% |
| `fate` | 0.0% |
| `tonnes` | 0.0% |

## Tonnes distribution (clean)
| Statistic | Tonnes |
|---|---|
| count | 489,399.00 |
| mean | 732.07 |
| std | 9,472.10 |
| min | 0.00 |
| 25% | 0.33 |
| 50% | 4.00 |
| 75% | 55.65 |
| 95% | 1,959.57 |
| 99% | 13,566.70 |
| max | 2,408,766.00 |

- Records with exactly 0 tonnes: **2.08%** (kept; represent permitted-but-nil movements)

## Categorical coverage (clean)
- Unique facilities (permits): **6,860**
- Unique waste codes: **765**
- Fate categories: incineration, landfill, long term storage, other fate, recovery, transfer (d), treatment
- Site categories: associate process, associated process, burial, combustion, incineration, landfill, mineral, mining, mobile plant, mrs, on/in land, processing, refining, storage, transfer, treatment, use of waste
