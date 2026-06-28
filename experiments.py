import anthropic, time, json, os

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=API_KEY)
MODEL = "claude-opus-4-8"

results = {}

# ---------------------------------------------------------------------------
# Experiment 1: Research Gap Identification
# ---------------------------------------------------------------------------
corpus = """
Silas Lab (Gladstone Institutes) — recent publications and research focus:

1. Marino ND, Talaie A, et al, Silas S, Bondy-Denomy J. "Translation-dependent
   degradation of cas12 mRNA triggered by an anti-CRISPR." Nature, 2026.
   An anti-CRISPR protein triggers degradation of cas12 mRNA in a
   translation-dependent manner, revealing a phage strategy that disables
   CRISPR immunity not just at the protein level but at the transcript level.

2. Huiting E, Cao X, et al, Silas S, et al. "Bacteriophages inhibit and evade
   cGAS-like immune function in bacteria." Cell, 2025 (erratum of 2023 paper).
   Phages encode proteins that both inhibit and evade bacterial CBASS
   (cGAS/STING-like) antiviral signaling systems.

3. Silas S, Carion H, Makarova KS, et al, Bondy-Denomy J. "Anti-restriction
   functions of injected phage proteins revealed by peeling back layers of
   bacterial immunity." Nat Commun, 2025.
   Using successive transposon screens to strip away layers of bacterial
   defense one at a time, the authors find phage proteins injected at the
   start of infection that specifically counteract restriction-modification
   (R-M) systems, which are normally masked by redundant defenses in wild
   strains.

4. Silas S, Carion H, Makarova KS, et al, Bondy-Denomy J. "Activation of
   bacterial programmed cell death by phage inhibitors of host immunity."
   Mol Cell, 2025.
   Phage-encoded immune inhibitors (e.g., anti-CRISPRs, anti-restriction
   proteins) are themselves sensed by abortive-infection / programmed cell
   death (PCD) systems, which trigger suicide of the infected cell as a
   population-level antiviral strategy when they detect immune suppression
   is underway.

5. Kokontis C, Klein TA, Silas S, Bondy-Denomy J. "Multi-interface licensing
   of protein import into a phage nucleus." Nature, 2025.
   The phage nucleus (a proteinaceous compartment that shields phage DNA from
   DNA-targeting defenses like CRISPR and restriction enzymes) selectively
   imports specific phage proteins through a licensing mechanism involving
   multiple distinct protein-protein interfaces.

Lab research statement: The Silas Lab takes a systems biology approach to
phage-host interactions, focusing on small, fast-evolving, non-essential
phage genes ("accessory genes," AGs). They run phage-independent screens
(expressing AGs across many wild bacterial strains to find which AGs trigger
programmed cell death / abortive infection) and phage-dependent screens
(finding AGs with anti-defense, including broad-spectrum anti-defense,
phenotypes), often using transposon suppressor screens to peel apart
redundant layers of bacterial immunity strain-by-strain, and AP-MS to
identify host protein targets of anti-defense AGs. A central open hypothesis
is that AG loss-of-function may be the "intended" outcome of defenses that
sense AGs as PCD triggers, putting phages in a lose-lose bind: lose the AG's
useful immune-suppressive function, or risk triggering abortive infection.
"""

prompt1 = f"""{corpus}

Based on these five recent papers and the lab's overall research program,
identify 4-5 specific, high-value unresolved questions in the field of
phage-host immune arms races that this lab's accessory-gene (AG) screening
platform is uniquely positioned to answer. Be specific and mechanistic —
not generic ("more research is needed") but pointed at concrete experimental
gaps (e.g., specific molecular interactions, specific defense system
combinations, specific predictions that haven't been tested). For each gap,
note briefly what kind of AG screen or follow-up experiment could address it."""

print("Running Experiment 1: Research Gap Identification...")
t0 = time.time()
resp1 = client.messages.create(
    model=MODEL, max_tokens=1800,
    messages=[{"role": "user", "content": prompt1}],
)
elapsed1 = time.time() - t0
text1 = resp1.content[0].text
print(f"Done in {elapsed1:.1f}s")
results["experiment1"] = {"prompt": prompt1, "response": text1, "elapsed_s": elapsed1}

# ---------------------------------------------------------------------------
# Experiment 2: Iterative Hypothesis Refinement
# ---------------------------------------------------------------------------
turn1_prompt = """The Silas Lab (Marino et al., Nature 2026) found that a
phage-encoded anti-CRISPR protein triggers translation-dependent degradation
of cas12 mRNA in the bacterial host. This is surprising because most known
anti-CRISPRs act by directly binding and sterically blocking the Cas protein
itself, not by destroying its mRNA.

Propose an initial mechanistic hypothesis for how an anti-CRISPR protein
could trigger translation-dependent degradation of its target's own mRNA.
Keep it to 2-3 concrete molecular mechanisms, each in 2-3 sentences."""

print("Running Experiment 2, turn 1...")
t0 = time.time()
msg_hist = [{"role": "user", "content": turn1_prompt}]
resp_t1 = client.messages.create(model=MODEL, max_tokens=900, messages=msg_hist)
text_t1 = resp_t1.content[0].text
msg_hist.append({"role": "assistant", "content": text_t1})

turn2_prompt = """That's a reasonable starting point, but consider a
confound: cas12 mRNA degradation could simply be a generic consequence of
ribosome stalling or collision whenever a phage protein is overexpressed at
high levels during infection — i.e., a nonspecific stress response, not a
mechanism specifically evolved to target cas12 transcripts. How would you
distinguish "specific, evolved anti-CRISPR-driven cas12 mRNA decay" from
"nonspecific stress-induced mRNA decay that happens to affect cas12 among
many transcripts"? What experiment or control rules out the confound?"""

print("Running Experiment 2, turn 2...")
t0 = time.time()
msg_hist.append({"role": "user", "content": turn2_prompt})
resp_t2 = client.messages.create(model=MODEL, max_tokens=900, messages=msg_hist)
text_t2 = resp_t2.content[0].text
msg_hist.append({"role": "assistant", "content": text_t2})

turn3_prompt = """Good — now give one specific, falsifiable mechanistic
prediction that follows from the "specific, evolved" model but NOT from the
nonspecific stress model, framed so it could be tested with a targeted
ribosome-profiling or RNA-seq experiment in the lab's existing wild-strain
screening framework."""

print("Running Experiment 2, turn 3...")
msg_hist.append({"role": "user", "content": turn3_prompt})
resp_t3 = client.messages.create(model=MODEL, max_tokens=900, messages=msg_hist)
text_t3 = resp_t3.content[0].text
elapsed2 = time.time() - t0
print(f"Done in {elapsed2:.1f}s")

results["experiment2"] = {
    "turns": [
        {"role": "user", "content": turn1_prompt},
        {"role": "assistant", "content": text_t1},
        {"role": "user", "content": turn2_prompt},
        {"role": "assistant", "content": text_t2},
        {"role": "user", "content": turn3_prompt},
        {"role": "assistant", "content": text_t3},
    ],
    "elapsed_s": elapsed2,
}

with open("experiment_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("Saved experiment_results.json")
