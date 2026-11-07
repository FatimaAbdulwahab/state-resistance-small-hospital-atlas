# Talk track

*What to say out loud about Project 4. Every number here comes from the dataset's stats file, so it matches the published data.*

## 60 seconds

Hospitals report certain infections to CDC, and CDC publishes, state by state, how often the bacteria behind them are resistant to key antibiotics. Medicare separately lists every certified hospital, with its size and whether it is rural. Nobody had put the two side by side.

I built an open atlas that does. It covers every state, D.C., and Puerto Rico from {first_year} to {latest_year}, for MRSA, carbapenem-resistant Enterobacterales, and vancomycin-resistant enterococci. In {latest_year}, just over half of the {hospitals_latest:,} general hospitals it counts have fewer than 100 beds, but they hold only about {pct_beds_in_small_latest_round} percent of beds. Those are community and critical access hospitals, with small laboratories, often far from specialists.

The atlas shows where those small hospitals sit in states where resistance is common. In {latest_year}, for example, {quad_mrsa} were in the top third of states both for MRSA resistance and for the share of hospitals that are small and rural.

It is free, with a permanent DOI and a public map, so state health departments, laboratory networks, and hospital associations can see where support for small-hospital laboratories would reach the most hospitals. I built it because I have worked in both an academic medical center lab and a community hospital lab.

## Two sentences

I built an open, citable atlas that puts CDC's state resistance rates for MRSA, CRE, and VRE next to Medicare counts of small and rural hospitals, 2011 to 2024. It shows where small hospitals, about half of all general hospitals, face the heaviest resistance burden.

## Three likely questions

**Does it show that small hospitals have more resistance?**
No. It is joined by state, not by hospital. It shows states where resistance is high *and* small hospitals are a large share of the network. CDC does not publish state resistance by hospital size.

**Can I use it to say resistance went up or down in my state?**
Not on its own. CDC cautions against drawing conclusions about change over time or comparing a state with the nation, because definitions, breakpoints, and reporting differ across years and states. The atlas repeats that caution on the map.

**Why are some states blank?**
CDC withholds a percent when fewer than 20 isolates were tested. That happens most in small, rural states. In older years CDC stored those blanks as 0 of 0; the atlas makes sure they are never read as 0% resistance.
