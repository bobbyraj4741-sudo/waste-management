# Module 1 - Industry Context (one-page concept note)

## What the dataset is

The **2024 Waste Data Interrogator** (Environment Agency, England) records, for
~6,000 permitted waste sites, every load of waste **received** at a site and
every load **removed** from a site during calendar year 2024. Each row is one
(facility, waste code, counterparty, fate) record with a tonnage.

## How waste moves (producer -> facility -> treatment/disposal)

```
 Producer / origin           Regulated facility              Onward destination
 (household, business,   ->   (transfer, treatment,     ->   (recovery, landfill,
  construction site)           landfill, incineration)         incineration, another site)
      "received"                    (the node)                      "removed"
```

A **producer** generates waste. It is collected and delivered to a **regulated
facility** (this is a *received* movement). The facility then does something with
it and sends it onward (a *removed* movement) to a **fate**:

- **Recovery** - recycling, reprocessing, energy-from-waste with recovery
  (EU **R-codes**). Good for circularity.
- **Disposal** - landfill or plain incineration (EU **D-codes**). Poor
  circularity; this is what we want to reduce.
- **Transfer** - waste is bulked and passed on without treatment.
- **Treatment** - physical/chemical processing before onward movement.

## Key definitions (Module 1 completion check)

- **Waste site**: a facility with an Environment Agency permit that handles waste.
- **Waste received**: waste arriving at a permitted site from an origin.
- **Waste removed**: waste leaving a permitted site to a destination.
- **Recovery**: putting waste back to beneficial use (recycling / energy).
- **Disposal**: getting rid of waste with no recovery value (landfill /
  incineration).

## Why we model it as a network

Descriptive statistics (total waste, % landfill) tell us *how much* waste there
is. Modelling the data as a **directed weighted flow network** - facilities and
places as nodes, waste movements as weighted edges - lets us ask *how waste
moves*: where it accumulates, which facilities are load-bearing hubs, where
recovery fails, and which sites behave unusually.

## Important data limitation

The counterparty of each movement is recorded as a **place / Waste Planning
Authority**, not as a counterparty facility permit. We therefore cannot link
facility A directly to facility B. The flow graph is built between facilities
and places (place -> facility for received, facility -> place for removed). True
facility-to-facility producer links are commercially confidential and outside
this public dataset.
