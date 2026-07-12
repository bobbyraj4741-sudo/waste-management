# Module 6 - Top 20 Facilities by Betweenness Centrality

Betweenness is computed on a tonnage-weighted directed graph (heavy routes
treated as shorter). High-betweenness facilities sit on many efficient waste
paths - they act as **routing bottlenecks / regional hubs**: if they are
disrupted or inefficient, a lot of waste has to re-route.

| label                                                             | region          | site_category   |   in_degree |   out_degree |   w_in_tonnes |   w_out_tonnes |   betweenness |
|:------------------------------------------------------------------|:----------------|:----------------|------------:|-------------:|--------------:|---------------:|--------------:|
| Kemsley Paper Mill                                                | South East      | processing      |          99 |           11 |       898,753 |        202,023 |             0 |
| Cringle Dock Transfer Station                                     | London          | transfer        |           4 |            6 |       260,458 |        260,458 |             0 |
| The Midlands Urban Mine EPR/MP3430AM                              | East Midlands   | treatment       |          15 |           14 |       246,427 |        286,284 |             0 |
| Bankfield House - EPR/XP3492CL                                    | North West      | mrs             |         118 |           22 |       278,013 |        277,601 |             0 |
| A W M Valley Farm Road M R F                                      | Yorks & Humber  | treatment       |          10 |           24 |       357,357 |        356,992 |             0 |
| Willesden Euro Terminal                                           | London          | transfer        |           1 |            3 |     1,555,827 |      1,587,570 |             0 |
| Ling Hall Landfill                                                | West Midlands   | landfill        |          58 |           32 |       484,847 |        125,475 |             0 |
| Ferrybridge IBA Facility EPR/QP3034JW                             | Yorks & Humber  | treatment       |           5 |           44 |       282,984 |        329,698 |             0 |
| Ferrybridge 1 - EPR/SP3239FU                                      | Yorks & Humber  | incineration    |          41 |           16 |       653,362 |        150,849 |             0 |
| Powerday Waste Recycling & Recovery Centre EPR/PP3093EE           | London          | treatment       |           1 |            9 |       267,856 |        273,915 |             0 |
| Mersey Valley PC EPR/BS5541IN                                     | North West      | incineration    |           7 |           46 |     1,344,673 |      1,792,109 |             0 |
| Severn Road Resource Recovery Centre - Energy from Waste Facility | South West      | incineration    |          40 |           20 |       398,589 |        117,704 |             0 |
| West Thurrock Recycling And Transfer Station                      | East of England | transfer        |           1 |            6 |       122,967 |        122,134 |             0 |
| Saddlebow Paper Mill EPR/FP3132UE                                 | East of England | processing      |          38 |           27 |       488,329 |        227,725 |             0 |
| Alexandra Dock 1 - EPR/RP3794CG                                   | North West      | mrs             |           7 |            8 |       533,510 |        418,748 |             0 |
| Edmonton EcoPark                                                  | London          | incineration    |           9 |           10 |       128,539 |        127,122 |             0 |
| Rookery Pit Energy recovery Facility EPR/WP3234DY                 | East of England | incineration    |          41 |           18 |       533,347 |        135,697 |             0 |
| Bolton Road - EPR/AP3435VQ                                        | Yorks & Humber  | treatment       |           7 |           16 |       217,734 |        150,190 |             0 |
| Argent Oil Terminal EPR/JP3031RC                                  | North West      | treatment       |           8 |            6 |        65,655 |         56,340 |             0 |
| Bespoke Mobile Plant                                              | <NA>            | mobile plant    |           9 |           10 |       178,599 |        181,590 |             0 |

*Interpretation*: facilities combining high weighted in/out degree with high
betweenness are the network's load-bearing hubs (large transfer stations and
treatment sites that consolidate waste for a whole sub-region). They are the
first places where a recovery improvement propagates widely.
