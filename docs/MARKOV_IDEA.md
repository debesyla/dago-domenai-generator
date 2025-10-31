Perfect — with 145k real domains you have an excellent corpus to *train* a Markov / n-gram generator so it produces realistic-looking domain labels. Below I give a practical, ready-to-run recipe + two Python scripts:

* **`train_and_save_markov.py`** — trains an n-gram model from your `domains_145k.txt` and saves the model counts to disk (JSON / pickle).
* **`generate_from_markov.py`** — loads the model, samples new labels, computes a log-likelihood score for each generated label, writes outputs, and shows options for dedup & filtering.

I also explain design choices (order, cleaning, scoring) and scaling tips (dedupe, disk-backed, Bloom filter).

---

## 1) Prepare your corpus

Save your 145k list as `domains_145k.txt`, one domain per line (can include TLD). We'll extract only the SLD (label) and clean it:

* Lowercase
* Remove `.lt` or other TLDs if present
* Keep only `[a-z0-9-]` (but prefer to avoid `-` start/finish)
* Skip labels shorter than 2 or longer than 63

---

## 2) Training script (order 3 recommended)

Order 3 (trigrams) is a good balance for pronounceable domain-like tokens. This script builds transition counts and saves the model as a pickle.

`train_and_save_markov.py`

```python
#!/usr/bin/env python3
"""
Train an order-N Markov model (character-level) on your domains list.
Input: domains_145k.txt (one domain per line)
Output: model saved to markov_model.pkl
"""
import re
import pickle
from collections import defaultdict, Counter
from pathlib import Path

INPUT = "domains_145k.txt"
MODEL_OUT = "markov_model.pkl"
ORDER = 3  # try 3 or 4

label_re = re.compile(r'[^a-z0-9-]')  # allowed chars

def clean_label(raw):
    s = raw.strip().lower()
    # drop tld if present like "example.lt" or "www.example.lt"
    s = s.split('.')  # keep the leftmost label
    if not s:
        return None
    label = s[0]
    # remove unwanted chars
    label = label_re.sub('', label)
    # skip starting/ending with '-'
    if not label or label[0]=='-' or label[-1]=='-':
        return None
    if len(label) < 2 or len(label) > 63:
        return None
    return label

def train(order=3):
    model = defaultdict(Counter)  # key -> Counter(next_char)
    total_keys = Counter()
    with open(INPUT, 'r', encoding='utf-8') as f:
        for line in f:
            label = clean_label(line)
            if not label:
                continue
            seq = '^' * order + label + '$'   # start/end tokens
            for i in range(len(seq) - order):
                k = seq[i:i+order]
                nxt = seq[i+order]
                model[k][nxt] += 1
                total_keys[k] += 1
    return dict(model), dict(total_keys)

if __name__ == "__main__":
    print("Training Markov model (order=%d) from %s..." % (ORDER, INPUT))
    model, totals = train(order=ORDER)
    print("States:", len(model))
    with open(MODEL_OUT, 'wb') as fo:
        pickle.dump({"order": ORDER, "model": model, "totals": totals}, fo)
    print("Saved model to", MODEL_OUT)
```

Run:

```bash
python train_and_save_markov.py
```

---

## 3) Generator + scoring script

This loads the model, samples with weighted choices, computes a **log-likelihood score** (how likely a generated label is under the model), and writes results.

`generate_from_markov.py`

```python
#!/usr/bin/env python3
import pickle, random, math
from collections import defaultdict
from pathlib import Path

MODEL_IN = "markov_model.pkl"
OUT_FILE = "generated_markov.txt"
N_TO_GENERATE = 1_000_000  # adjust
MAX_LEN = 24
MIN_LEN = 3

def load_model(path=MODEL_IN):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data['order'], data['model'], data['totals']

def weighted_choice(counter):
    # counter: dict-like {char: count}
    items = list(counter.items())
    total = sum(c for _,c in items)
    r = random.randint(1, total)
    s = 0
    for ch, c in items:
        s += c
        if r <= s:
            return ch
    return items[-1][0]

def sample_once(order, model, max_len=MAX_LEN):
    key = '^' * order
    out = ''
    logprob = 0.0
    while True:
        nxt_counter = model.get(key)
        if not nxt_counter:
            break
        nxt = weighted_choice(nxt_counter)
        # compute probability for scoring
        total = sum(nxt_counter.values())
        p = nxt_counter[nxt] / total
        logprob += math.log(p)
        if nxt == '$' or len(out) >= max_len:
            break
        out += nxt
        key = (key + nxt)[-order:]
    return out, logprob

def main():
    order, model, totals = load_model()
    print(f"Loaded model order={order} states={len(model)}")
    out_path = Path(OUT_FILE)
    seen = set()   # for small runs; for very large, use on-disk dedupe
    with out_path.open('w', encoding='utf-8') as fo:
        generated = 0
        attempts = 0
        while generated < N_TO_GENERATE and attempts < N_TO_GENERATE * 5:
            label, logp = sample_once(order, model)
            attempts += 1
            if not label or len(label) < MIN_LEN:
                continue
            # filter rules: only a-z0-9, no leading/trailing -, etc assumed by training
            if label in seen:
                continue
            seen.add(label)
            fo.write(f"{label}.lt\t{logp:.6f}\n")
            generated += 1
            if generated % 10000 == 0:
                print("Generated", generated)
    print("Done. Saved", generated, "labels to", out_path)

if __name__ == "__main__":
    main()
```

Run:

```bash
python generate_from_markov.py
```

Output lines look like:

```
bestshop.lt    -12.345678
gogomart99.lt  -14.234567
...
```

Lower (more negative) `logp` means less likely under the model. Use this to **rank** your generated candidates: higher logp = more like the training corpus.

---

## 4) Practical considerations & improvements

**Order (n):**

* `order=2` → more random; `order=3` → good mix; `order=4` → more conservative / closer to training examples.
* Try 3 and 4 and compare sample diversity.

**Smoothing / unknown state handling:**

* The simple model above returns nothing for unseen states; that's OK because training corpus of 145k will cover many states.
* For heavy smoothing you can add a small uniform probability to unseen transitions.

**Deterministic scoring for ranking:**

* Use `log-likelihood` (sum of log probs) divided by length to normalize: `score = logp / len(label)` — this gives per-char log-probability.

**Dedupe & scale:**

* The above uses an in-memory `seen` set — fine for up to a few million unique labels (if memory permits).
* For 10M dedupe use:

  * External `sort | uniq` after generation (stream to file then sort),
  * Or use `sqlite` with `INSERT OR IGNORE` on a table with an index,
  * Or a Bloom filter (e.g., `pybloom_live`) for approximate dedupe if memory constrained.

**Filtering / blacklist:**

* Remove profane words, trademarks, very short labels, labels starting with digits (if you dislike), or labels with invalid patterns.
* Apply pronounceability: you can use the model log-prob as a proxy — high logp = pronounceable / likely.

**Seeding & diversity:**

* You can seed generation with a specific prefix by starting the key as `'^'*(order-1) + 'pr'` or provide a temperature-like control by randomly choosing less-likely transitions occasionally.

**Combining methods:**

* Mix Markov output with affix combinators, mutations and numeric suffix templates to create a richer candidate set.
* Score everything with the Markov log-likelihood — use it to prioritize scanning.

---

## 5) Quick debugging / validation suggestions

* Generate a small sample (10k) first and manually inspect for quality.
* Check distribution of lengths and character classes; adjust min/max length accordingly.
* Compare generated tokens against your 145k set to ensure you're not outputting only near-duplicates.

---

## 6) If you want a single combined script

I can produce a single script that:

* Loads `domains_145k.txt`
* Trains order 3 or 4
* Generates `M` candidates
* Streams to disk
* Optionally uses sqlite or pybloom_live for memory-efficient dedupe
* Scores and outputs the top `K`

Tell me which extras you want (order, target count, dedupe method: `set|sqlite|bloom`, and if you want normalized per-char score), and I’ll drop the combined script in the next message.