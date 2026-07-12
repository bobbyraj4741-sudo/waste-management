# Presenter's Guide — *Hiding in the Network: Uncovering England's Circularity Failures with Graph AI*

A slide-by-slide script for presenting `Graph_AI_Waste_Intelligence.pdf` (12
slides). Each slide has: **what's on screen**, a **word-for-word-ready talk
track** (the ▶ paragraphs — say these more or less verbatim), **transition** to
the next slide, and **timing**. Total target: **12–15 minutes** + 5 min Q&A.

> **One-line thesis to hold in your head the whole time:** *We turned a passive
> government compliance spreadsheet into an active "strike list" of the few
> facilities and regions that, if fixed, disproportionately improve England's
> recycling — using only network science and lightweight, reproducible AI.*

**Pacing cheat-sheet**

| Slide | Title | Time |
|---|---|---|
| 1 | Title | 0:45 |
| 2 | The Scale | 1:15 |
| 3 | Structural Limitation | 1:30 |
| 4 | Constructing the Network | 1:15 |
| 5 | Load-Bearing Hubs | 1:30 |
| 6 | Behavioral Clustering | 1:15 |
| 7 | Dual-Engine Anomaly Detection | 1:45 |
| 8 | Top Outliers | 1:15 |
| 9 | AI Flags → Operational Intelligence | 1:15 |
| 10 | Circularity Leaks | 1:15 |
| 11 | Five Interventions | 1:15 |
| 12 | Close | 0:45 |

---

## Slide 1 — Title: "Hiding in the Network"

**On screen:** Title, subtitle "Turning the 2024 Waste Data Interrogator from a
passive compliance record into an active intelligence strike list," and
"A reproducible workflow using unsupervised network embeddings."

▶ "Every year the Environment Agency publishes the Waste Data Interrogator — a
huge compliance record of every tonne of waste received and removed by England's
permitted facilities. It's used mostly for reporting: *how much* waste, *what*
percentage recycled. Our question was different: **can we treat this same data as
a network and find where recycling is quietly failing?**"

▶ "The short answer is yes. Using graph analysis and lightweight, fully
reproducible AI — no black-box deep learning — we turn a passive record into an
*active strike list* of the specific facilities, regions, and waste streams worth
intervening on. That's what I'll walk you through."

**Transition:** "First, the scale of what we're dealing with."

**Timing:** 45s. Don't linger — this is the hook.

---

## Slide 2 — The Scale of England's Industrial Waste System

**On screen:** 3 big numbers — **6,860** regulated facilities, **489,399**
tracked movements, **358,273,157** tonnes recorded in 2024. Below: a bar of
**119.3M tonnes of removed waste** split **59.4% Recovered / 23.7% Outright
Disposal / 5.8% Transferred**.

▶ "The system is enormous: nearly **6,900 facilities**, close to **half a
million** individual waste movements, and **358 million tonnes** logged in 2024
alone."

▶ "Now the headline circularity number. Of the **119 million tonnes of waste
*removed*** from facilities — that's the waste leaving to its final destination —
**59% is recovered**, which is good. But **nearly a quarter, 23.7%, still goes to
outright disposal** — landfill or plain incineration. That gap is the problem
we're chasing."

▶ "Here's the key move, in the caption: descriptive statistics tell you *how
much* waste exists. They can't tell you *where* recovery fails or *why*. For
that, you have to model the data as a **directed flow network** — and watch where
waste accumulates."

**Transition:** "But before we build that network, there's one honest limitation
you need to understand — it shapes everything."

**Timing:** 1:15. Land the 23.7% — it's the villain of the story.

**Watch out:** 358M total vs 119.3M removed. If asked: the 358M counts *both*
received and removed movements (waste is counted as it enters and as it leaves);
119.3M is the *removed* side, which is where "fate" (recovery vs disposal) is
recorded.

---

## Slide 3 — The Structural Limitation: We Cannot See Producer-to-Producer

**On screen:** Producer (locked/greyed) → **Place** (anchor icon, "Waste
Planning Authority, e.g. Kent — The Observable Anchor") → **Permitted Facility**
(hexagon, "Specific Permit ID"). Orange caption: network is bipartite; true
facility-to-facility flows are structurally hidden.

▶ "This is the most important caveat in the whole project, and we put it up front
deliberately. When a facility reports a movement, the *counterparty* is recorded
as a **place** — a Waste Planning Authority like 'Kent' — **not** as another
facility's permit ID."

▶ "So we can see 'Facility X sent waste to Kent,' but not 'Facility X sent waste
to Facility Y.' True producer-to-producer links are commercially confidential and
out of scope. That means our network is **bipartite**: waste flows from
**facilities to places**, and from **places to facilities**. Places are the
observable anchor between them."

▶ "We're not hiding this — we designed around it. Everything that follows is the
*honest* network the public data actually supports. And as you'll see, it's more
than enough to find the failures."

**Transition:** "So here's what that network looks like when you build it."

**Timing:** 1:30. This slide buys you credibility — don't rush the honesty.

---

## Slide 4 — Constructing the 2024 Waste Flow Network

**On screen:** Stats box — **7,284 nodes** (6,860 facilities + 424 places),
**115,913 edges** (weighted by tonnes), **average degree 31.83**, **100% single
connected component**. Large network visualization. Insight: it's one
tightly-linked circulatory system where a bottleneck forces waste to reroute.

▶ "We built a directed, weighted graph: **7,284 nodes** — the facilities plus the
places — joined by nearly **116,000 edges**, each weighted by the tonnes that
flowed along it. On average every node connects to about **32 others**."

▶ "The single most striking structural fact: the network is **one hundred percent
a single connected component**. There are no islands. England's regulated waste
is *not* a collection of isolated local problems — it's **one tightly-linked
circulatory system**."

▶ "That has a real consequence: a bottleneck in one region doesn't stay local. It
forces waste to reroute across the whole system. Which means the *right* few
interventions can ripple nationally — a theme we'll return to at the end."

**Transition:** "If it's one connected system, the obvious question is: which
nodes hold it together? That's where centrality comes in."

**Timing:** 1:15.

---

## Slide 5 — Identifying Load-Bearing Routing Hubs

**On screen:** Left — a "dumbbell" diagram: two dense clusters joined by one
central orange node labelled "High Betweenness Centrality: the system's bridge."
Right — two real examples: **Willesden Euro Terminal (London)** 1.55M received /
1.58M removed; **Mersey Valley PC (North West)** 1.34M received / 1.79M removed.
Caption: not just high-volume — structural pillars.

▶ "To find the critical nodes we use **betweenness centrality** — a measure of
how often a node sits *on the path between* other nodes. A node with high
betweenness is a **bridge**: waste has to pass through it to get where it's
going."

▶ "The diagram makes it visual — that orange node in the middle is the only link
between two whole halves of the system. Remove it and the two sides can't reach
each other."

▶ "In our data, sites like the **Willesden Euro Terminal** in London and **Mersey
Valley** in the North West are exactly these bridges — each handling well over a
million tonnes in *and* out. The crucial point is in the caption: **these aren't
just big sites, they're structural pillars.** If one is disrupted, massive
volumes of regional waste are forced to reroute — with cost and emissions
consequences."

**Transition:** "Centrality tells us *where the pillars are*. Next we asked a
different question: how does each facility actually *behave*?"

**Timing:** 1:30.

---

## Slide 6 — Unsupervised Behavioral Clustering (KMeans)

**On screen:** A table of 6 clusters with bar-gauges for Throughput, Recovery
Rate, Disposal Rate, Diversity:
- **Diverse Recovery Facilities** (n=2,323) — high recovery, high diversity
- **Near-Pure Recovery** (n=1,803) — very high recovery, low disposal
- **Hazardous-Waste Specialists** (n=1,013)
- **High-Volume Transfer Hubs** (n=323) — huge throughput, low recovery
- **General Treatment / Mixed** (n=324)
- **Disposal-Dependent** (n=1,074) — very high disposal
Caption: we now have a behavioral baseline for every facility.

▶ "We let an **unsupervised** algorithm — KMeans — group all 6,860 facilities by
*behaviour*, not by their official category. No labels, no supervision; the
algorithm finds the natural groupings from features like volume, recovery rate,
and waste diversity."

▶ "Six clean archetypes fell out. Most facilities are healthy: over **4,000** sit
in the two recovery-oriented clusters. But note the two we care about — the **323
high-volume transfer hubs** that move enormous tonnage with *low* recovery, and
the **1,074 disposal-dependent sites** where waste mostly ends up in the ground."

▶ "Why does this matter? Because now every facility has a **behavioural
baseline** — a 'normal' for its type. And the moment you have a baseline, you can
ask the AI its next question: **which facilities break their own pattern?**"

**Transition:** "That's anomaly detection — and this is the technical heart of
the project."

**Timing:** 1:15. Don't read all six rows aloud — name the two problem clusters.

---

## Slide 7 — Dual-Engine Graph AI Anomaly Detection

**On screen:** Flow diagram. Left engine: **Tabular Features** (volume,
fractions, entropy) → **Isolation Forest**. Right engine: **Network Topology** →
**DeepWalk Matrix Factorization** (Random Walk → PPMI → Truncated SVD) →
**Isolation Forest**. Both feed a central **Combined Anomaly Score**. Caption: we
measure structural weirdness without heavy deep-learning frameworks.

▶ "We detect anomalies with **two independent engines**, then combine them — so a
facility has to be weird in *at least one* well-understood way to get flagged."

▶ "**Engine one** looks at the *numbers*: volume, recovery and disposal
fractions, waste-diversity entropy. An **Isolation Forest** — an algorithm that
flags points which are easy to separate from the crowd — scores each facility's
tabular weirdness."

▶ "**Engine two** looks at *position in the network*. This is where we did
something deliberately elegant. The standard tools for graph embeddings —
node2vec, gensim, PyTorch-Geometric — wouldn't build on our Python version. So
instead of forcing a heavy dependency, we implemented **DeepWalk from scratch as
matrix factorization**: take **random walks** across the graph, count which nodes
co-occur, convert that to a **PPMI** matrix, and compress it with **truncated
SVD** into a 32-number fingerprint per node. That's mathematically the same idea
as DeepWalk — it's a known result — but using only NumPy and scikit-learn."

▶ "The payoff, in the caption: **we measure genuine structural network weirdness
without any heavy deep-learning framework** — so the whole thing is lightweight
and fully reproducible. The two scores are combined into one ranked list."

**Transition:** "So who tops that list? Meet the outliers."

**Timing:** 1:45 — your most technical slide. If the audience is non-technical,
compress the DeepWalk detail to: *"we gave every facility a fingerprint based on
its position in the network, built from scratch so it's lightweight and
reproducible."*

---

## Slide 8 — The Top Mathematical Outliers

**On screen:** 3 cards.
- **Stoke Bardolph Sewage Treatment Works** (East Midlands), cluster *Diverse
  Recovery*, score **5.027** — trigger: 493k tonnes throughput with **0% recovery
  and 0% disposal recorded**.
- **Shield Environmental** (South West), cluster *Hazardous specialists*, score
  **4.905** — trigger: **100% disposal** despite being in a highly-recovered
  hazardous cluster.
- **The New Forest Waste Transfer Station** (South East), cluster *High-volume
  transfer hubs*, score **5.045** — trigger: high transfer intensity + unusually
  diverse counterparties.

▶ "These are the top of the strike list, and each is interesting for a *different*
reason."

▶ "**Stoke Bardolph** pushes nearly half a million tonnes but records **zero
recovery and zero disposal** — a fate that's literally unaccounted for. That's
almost certainly a **data gap**, and it matters because it distorts the regional
recovery statistics everyone relies on."

▶ "**Shield Environmental** sits in a cluster of hazardous sites that mostly
recover — yet it sends **100% to disposal**. It breaks its own peer group. That's
a prime candidate for a diversion review."

▶ "And **The New Forest transfer station** shows unusually diverse counterparties
for a transfer hub — the structural fingerprint flagged it, not the raw numbers."

▶ "The point: the AI isn't just finding *big* sites. It's finding sites that
*violate the expected pattern* — which is exactly where human attention is worth
spending."

**Transition:** "But a score alone isn't useful to an operator. The real value is
translating each flag into an *action*."

**Timing:** 1:15. Lead with Stoke Bardolph — the 0%/0% is the most vivid.

---

## Slide 9 — Translating AI Flags into Operational Intelligence

**On screen:** 3-column table — **The AI Flag → Network Context → Human Action**:
- Node Embedding Outlier (Stoke Bardolph & Sutton Courtenay) → massive throughput,
  zero recorded fate → **data gap / storage-only; manual review before trusting
  regional stats**.
- Multivariate Feature Outlier (Shield Environmental) → hazardous-dominant, total
  landfill reliance → **prime candidate for diversion to recovery sites**.
- High Centrality + 0% Recovery (Willesden Euro Terminal) → dominant regional
  pass-through → **structural bottleneck; efficiencies here cascade nationally**.

▶ "This is the slide that turns statistics into decisions. Each *type* of AI flag
maps to a specific *network meaning*, which maps to a specific *human action*."

▶ "A **node-embedding outlier** with no recorded fate means a data gap or a
storage-only site — the action is *verify it before you trust the regional
numbers*. A **feature outlier** with total landfill reliance is a *diversion
candidate*. And a **high-centrality pass-through with zero recovery** is a
*structural bottleneck* — and because the network is fully connected, fixing it
cascades nationally."

▶ "So the AI never makes the decision. It hands a human a ranked, *explained*
worklist. That's the difference between a black box and an intelligence tool."

**Transition:** "Zooming out from individual facilities — where are the systemic
leaks?"

**Timing:** 1:15.

---

## Slide 10 — Targeting the Circularity Leaks

**On screen:** Left "The Stream Leak" — donut chart, **EWC Chapter 17
(Construction & Demolition)**: 18.4M tonnes moved, **highest transfer-share
(18.6%)** of any major category; waste bulked and moved repeatedly without value
recovered. Right "The Facility Leaks" — **Tyttenhanger Landfill** 772,770 t (100%
disposal), **Knowsley Rail Transfer** 735,400 t (100% disposal), **Gibson Lane**
804,736 t (85% disposal).

▶ "There are two kinds of leak. First, a **stream leak**: **Construction &
Demolition waste — EWC Chapter 17**. Over 18 million tonnes, and it has the
**highest transfer share of any major category** — meaning it gets bulked up and
shuffled between transfer stations repeatedly *without value ever being
recovered*. It just circulates."

▶ "Second, **facility leaks**: specific high-volume sites running at or near
**100% disposal**. Tyttenhanger and Knowsley Rail each bury over 700,000 tonnes
with essentially no recovery; Gibson Lane, 85%. These are concentrated, nameable
targets."

▶ "So we now have both a *what* — the C&D stream — and a *where* — these specific
disposal heavyweights."

**Transition:** "Which lets us make concrete recommendations rather than vague
ones."

**Timing:** 1:15.

---

## Slide 11 — Five Interventions to Rewire the Circuit

**On screen:** Map of England (East Midlands highlighted) with 5 interventions:
1. **Inject Recovery in the East Midlands** — highest disposal rate (31.2% of
   10.2M tonnes).
2. **Segregate C&D Waste at Source** — break the EWC Chapter 17 transfer loop.
3. **Review the Disposal Heavyweights** — mandate recovery audits for Knowsley
   Rail, Tyttenhanger.
4. **Shorten the High-Transfer Paths** — reroute waste past multiple transfer
   hubs directly to recovery endpoints.
5. **Audit the 'No-Fate' Anomalies** — resolve data gaps at hubs like Stoke
   Bardolph to secure accurate national recovery targets.

▶ "Five concrete interventions, each tied to something we've shown."

▶ "One — **inject recovery capacity in the East Midlands**, which has the
nation's highest disposal rate. Two — **segregate Construction & Demolition waste
at source** to break that transfer loop. Three — **mandate recovery audits** for
the disposal heavyweights we just named. Four — **shorten the high-transfer
paths**, routing waste past redundant hubs straight to recovery. And five —
**audit the no-fate anomalies** like Stoke Bardolph, so our national recovery
statistics are actually trustworthy."

▶ "Notice none of these say 'overhaul the whole system.' They're surgical."

**Transition:** "And that's the whole argument in one line."

**Timing:** 1:15. Don't over-explain each — the audience can read them.

---

## Slide 12 — Close: Anomalies are Strategic Opportunities

**On screen:** Central node radiating rings. Green quote: *"Graph AI proves that
we don't need to overhaul 6,860 facilities to fix England's circular economy."*
Then: by overlaying top anomalies onto highest-disposal regions we isolate the
exact bottlenecks; targeting a handful of outliers disproportionately moves
national sustainability. Bold: **FROM PASSIVE COMPLIANCE TO ACTIVE
INTELLIGENCE.**

▶ "Here's the takeaway. **We don't need to overhaul all 6,860 facilities to fix
England's circular economy.** Because the system is one connected network, a
handful of well-chosen interventions — the mathematical outliers sitting in the
highest-disposal regions — move the needle disproportionately."

▶ "That's the whole shift: **from passive compliance to active intelligence.** The
same dataset that used to just *report* the problem now tells us exactly where to
*act*. And because the entire pipeline is lightweight and reproducible, anyone can
re-run it on next year's data. Thank you — I'm happy to take questions."

**Timing:** 45s. End on "from passive compliance to active intelligence" — let it
sit, then invite questions.

---

# Expected Questions & Detailed Answers

Grouped by theme. Each answer is written to be delivered as-is; the **bracketed
tags** tell you the fallback if pressed further.

## A. Data & methodology validity

**Q1. Your network is bipartite — facilities only connect through places. Doesn't
that cripple the analysis?**
> It constrains it honestly, but it doesn't cripple it. We can't trace facility-A
> to facility-B directly, so we don't claim to. What the place-anchored network
> *does* preserve is every facility's full in/out flow profile, its position
> relative to regional hubs, and its behaviour versus peers — which is all we need
> for centrality, clustering, and anomaly detection. The betweenness hubs and the
> outliers we surface are real regardless of the bipartite structure. If
> producer-to-producer data ever became available, it would *add* resolution, not
> overturn these findings. [If pressed: the 100%-connected-component result and
> the hub identification are both properties that survive the bipartite
> projection.]

**Q2. Isolation Forest and KMeans are pretty classical. Why call this "AI," and
why not use a Graph Neural Network?**
> Two honest reasons. First, GNN tooling (PyTorch-Geometric) and node2vec/gensim
> didn't build in our environment, so rather than ship something non-reproducible
> we implemented DeepWalk *as matrix factorization* — random walk → PPMI →
> truncated SVD — which is a proven mathematical equivalent of the embedding a
> GNN-adjacent method would learn. Second, for an *unsupervised, unlabeled*
> anomaly task on ~7,000 nodes, a GNN would add training complexity and opacity
> without a labeled target to justify it. The value here is the *combination* —
> tabular weirdness plus structural weirdness — not model sophistication for its
> own sake. Everything is explainable and re-runnable on a laptop. [If pressed on
> "is it really AI": it's unsupervised machine learning and network representation
> learning — the label matters less than that no human hand-picked the outliers.]

**Q3. How do you know the anomalies are real problems and not just noise or data
entry errors?**
> We don't assume they're problems — we rank them for *human review*, which is the
> whole point of slide 9. In fact several top flags (Stoke Bardolph's 0%/0% fate)
> are almost certainly **data-quality issues**, and that's a genuinely valuable
> finding: those gaps distort national recovery statistics. Others (Shield
> Environmental at 100% disposal inside a recovery cluster) are behavioural
> outliers worth an operational look. The AI's job is to shrink 6,860 facilities
> to a handful worth a human's time — not to pass final judgment. [If pressed:
> requiring a facility to be flagged by *either* engine, combined with cluster
> context, filters a lot of pure noise.]

**Q4. Why contamination = 3%? Isn't that arbitrary?**
> It's a deliberate, conservative choice: 3% keeps the flagged set small enough to
> be a genuine *worklist* rather than a firehose. It's a ranking threshold, not a
> claim that "exactly 3% of facilities are bad." The combined score is continuous,
> so a reviewer can go deeper or shallower down the ranked list as resources
> allow. [If pressed: we could expose it as a tunable parameter for the operator.]

**Q5. The two anomaly scores are on different scales — how do you combine them
fairly?**
> Each score is standardized to a z-score — mean zero, unit variance — before
> they're summed, so neither engine dominates just because of its raw range. A
> facility rises to the top only if it's genuinely unusual on the combined,
> normalized signal. [If pressed: facilities missing an embedding score are
> mean-imputed so they aren't unfairly penalized or rewarded.]

## B. Numbers & interpretation

**Q6. You say 358 million tonnes but 119 million removed — which is it?**
> Both, measuring different things. **358M** is the total across *all* movements —
> waste is logged both when it's *received* at a facility and when it's *removed*,
> so there's legitimate double-counting as material flows through the chain.
> **119.3M** is specifically the *removed* side, and that's where the "fate" —
> recovery versus disposal — is recorded. So all our recovery/disposal percentages
> are computed against the 119M removed figure, which is the correct denominator.

**Q7. 59% recovery sounds decent. Why is 23.7% disposal a crisis?**
> It's not framed as a crisis — it's framed as a *targetable gap*. 23.7% of 119
> million tonnes is roughly **28 million tonnes** going to landfill or plain
> incineration every year. Even a few percentage points diverted is millions of
> tonnes and material value recovered. And crucially, that disposal isn't evenly
> spread — it concentrates in specific regions (East Midlands, 31%) and specific
> sites (the 100%-disposal heavyweights), which is exactly what makes it
> addressable rather than diffuse. [If pressed: national average hides regional
> failure — that's the core argument for the network view.]

**Q8. Betweenness on 7,000 nodes is expensive — did you approximate it?**
> Yes, and transparently: exact betweenness on a graph this size is costly, so we
> use the standard **sampled approximation** — computing shortest-path
> contributions from a random sample of source nodes (k≈600) rather than all of
> them. The ranking of top hubs is stable under that sampling, and we fix the
> random seed so the result is reproducible. The named hubs — Willesden, Mersey
> Valley — are robustly at the top. [If pressed: we could run exact betweenness
> offline to confirm, but the sample already gives a stable top-20.]

**Q9. EWC Chapter 17 has "only" 18.6% transfer share — why is that the headline
stream leak?**
> Because it's the *highest* transfer share of any major category, on a huge base
> — 18.4 million tonnes. Transfer means the waste is bulked and passed along
> *without recovery happening*. So a high transfer share on a high-volume stream
> means millions of tonnes of construction and demolition material circulating
> between handlers, repeatedly, without value being extracted — that's precisely a
> circularity leak, even if the percentage sounds modest. [If pressed: C&D is also
> highly recoverable in principle — aggregates, metals — so the lost opportunity
> is large.]

## C. Actionability & impact

**Q10. Are these recommendations actually feasible, or just analytically neat?**
> They're deliberately surgical, not utopian. "Inject recovery capacity in the
> East Midlands" and "mandate recovery audits for named high-disposal sites" are
> policy/operational levers a regulator or operator already has. We're not
> proposing to rebuild the system — the closing slide's whole point is that
> *because the network is connected, a handful of targeted moves cascade
> nationally*. The analysis tells you the highest-leverage few; feasibility and
> cost-benefit are the operator's next step, which our ranked, explained output is
> designed to feed. [If pressed: we can't cost the interventions from this data
> alone — that's a stated limitation.]

**Q11. If a facility shows 0% recovery and 0% disposal, isn't that just missing
data, not an insight?**
> It is missing data — and that *is* the insight. If a site pushing 493,000 tonnes
> has no recorded fate, then every regional and national recovery statistic that
> includes it is wrong by up to that amount. Flagging it (intervention 5, "audit
> the no-fate anomalies") is a prerequisite for trusting *any* recovery target.
> So the AI surfacing data gaps is a feature, not a failure. [If pressed: it may
> also be a genuinely storage-only site — either way it needs human confirmation
> before its numbers are used.]

**Q12. Could this be used to unfairly target or penalize specific named
facilities?**
> Important concern, and the framing on slide 9 is deliberate: every flag maps to
> *"manual review"* or *"audit,"* never to an automated penalty. An anomaly is a
> reason to *look*, not a verdict. Many flags turn out to be data gaps or
> legitimate specialization. We'd position this as a triage tool for regulators
> and operators, with a human always in the loop before any action. [If pressed:
> the method is about efficient allocation of scarce inspection attention, not
> enforcement automation.]

## D. Reproducibility & scope

**Q13. Can this be re-run on 2025 data or extended to other countries?**
> Yes — that's a core design goal. The pipeline is lightweight (NumPy,
> scikit-learn, networkx — no GPU, no heavy frameworks) and fully scripted, so
> pointing it at next year's Waste Data Interrogator is essentially a re-run. Any
> country publishing facility-level received/removed waste records with a fate
> field could use the same approach; the only thing that changes is the column
> mapping. [If pressed: the fate taxonomy (R/D codes) is EU-derived, so European
> datasets would map most directly.]

**Q14. What are the biggest limitations you'd want us to keep in mind?**
> Four, and we state them openly: (1) **no producer-to-producer visibility** — the
> bipartite constraint from slide 3; (2) **no distance or cost data**, so
> "inefficiency" is measured by fate and network position, not transport emissions
> or economics; (3) **fate-data gaps** at some high-volume sites, which we flag
> rather than resolve; and (4) **anomaly ≠ wrongdoing** — flags are for review. None
> of these undermine the core findings, but they bound what we claim. [If pressed:
> adding geographic coordinates would unlock genuine routing-efficiency analysis —
> a clear next step.]

**Q15. What would you do with more time or more data?**
> Three things: overlay **geographic/distance data** to quantify the transport
> cost of the high-transfer paths (intervention 4); bring in **time-series** across
> multiple years to distinguish persistent structural failures from one-off
> reporting quirks; and if it were ever available, **producer-level links** to
> close the bipartite gap. But I'd stress the current pipeline already produces an
> actionable strike list — those are enhancements, not fixes. [If pressed: a
> lightweight dashboard over the ranked list would make it directly usable by
> regulators.]

---

## Quick-fire fallback lines (if you blank)

- **"What's the one takeaway?"** → *"England's waste is one connected network, so
  fixing a handful of mathematically-flagged outliers moves national recycling
  more than broad, untargeted policy."*
- **"Is the AI trustworthy?"** → *"It never decides — it ranks and explains, then a
  human reviews. Everything is reproducible on a laptop."*
- **"Why should I care?"** → *"28 million tonnes a year go to disposal, and it's
  concentrated in nameable regions and sites we can point to today."*
