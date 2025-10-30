#!/usr/bin/env python3
# CUPP-X Ultimate by Bucky
# Dark Tkinter GUI, English only.
# Full, corrected version (symbol probabilities, leet, unlimited target count)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import itertools
import os
import random
from datetime import datetime

# -------------------------
# CONFIG / CHAR SETS
# -------------------------
LEET_MAP = str.maketrans("aeiostl", "4310571")
SYMBOL_CHARS = list(r"""!@#$%^&*()-_=+[]{};:'",.<>/?\|`~""")
SEPARATORS = ["", ".", "_", "-"]
COMMON_PREFIXES = ["", "the", "my", "mr", "ms", "dr"]
COMMON_SUFFIXES = ["", "1", "12", "123", "1234", "2020", "2021", "2022", "2023", "2024", "2025", "007"]

DEFAULT_WORD_CAP = 10000   # fallback if user input invalid

# -------------------------
# HELPERS
# -------------------------
def clean_token(tok):
    if tok is None:
        return ""
    return "".join(ch for ch in str(tok) if ch.isalnum()).lower()

def digit_only(s):
    return "".join(ch for ch in str(s) if ch.isdigit())

def split_csv_field(s):
    if not s:
        return []
    return [part.strip() for part in s.split(",") if part.strip()]

def years_from_age(age_str):
    ys = []
    try:
        if not age_str:
            return ys
        age = int(str(age_str).strip())
        cy = datetime.now().year
        by = cy - age
        ys.append(str(by))
        ys.append(str(by)[-2:])
    except Exception:
        pass
    return ys

def expand_profile_tokens(profile):
    tokens = set()
    def add(v):
        if not v:
            return
        if isinstance(v, list):
            for it in v:
                s = clean_token(it)
                if s: tokens.add(s)
        else:
            s = clean_token(v)
            if s: tokens.add(s)
    add(profile.get("first_name"))
    add(profile.get("last_name"))
    add(profile.get("partner"))
    add(profile.get("pet"))
    add(profile.get("company"))
    add(profile.get("nicknames", []))
    add(profile.get("keywords", []))
    add(profile.get("years", []))
    email = profile.get("email")
    if email:
        local = email.split("@", 1)[0]
        localc = clean_token(local)
        if localc:
            tokens.add(localc)
    fn = clean_token(profile.get("first_name","") or "")
    ln = clean_token(profile.get("last_name","") or "")
    if fn and ln:
        tokens.add(fn + ln)
        tokens.add(fn + "." + ln)
        tokens.add(fn[0] + ln)
        tokens.add(fn + ln[0])
    return sorted(tokens)

# -------------------------
# BASE PERMUTATIONS WITHOUT SYMBOLS
# -------------------------
def base_permutations(tokens, birth_years=None, phones=None, use_separators=True):
    out = set()
    years = birth_years or []
    phones = phones or []

    for t in tokens:
        out.add(t)
        for pre in COMMON_PREFIXES:
            for suf in COMMON_SUFFIXES:
                cand = f"{pre}{t}{suf}".strip()
                if cand:
                    out.add(cand)
        for y in years:
            out.add(f"{t}{y}")
            out.add(f"{t}{y[-2:]}")

    for t in tokens:
        for p in phones:
            if not p:
                continue
            last4 = p[-4:] if len(p) >= 4 else p
            last3 = p[-3:] if len(p) >= 3 else p
            first3 = p[:3] if len(p) >= 3 else p
            variants = [p, last4, last3, first3]
            for v in variants:
                out.add(f"{t}{v}")
                out.add(f"{v}{t}")
                if use_separators:
                    for s in SEPARATORS:
                        out.add(f"{t}{s}{v}")
                        out.add(f"{v}{s}{t}")

    for a, b in itertools.permutations(tokens, 2):
        if use_separators:
            for sep in SEPARATORS:
                for suf in COMMON_SUFFIXES:
                    out.add(f"{a}{sep}{b}{suf}".strip())
        else:
            out.add(f"{a}{b}")

    for p in phones:
        last4 = p[-4:] if len(p) >= 4 else p
        out.add(p)
        out.add(last4)
        for y in years:
            out.add(f"{p}{y}")
            out.add(f"{last4}{y}")

    return sorted([o for o in out if o])

# -------------------------
# LEET VARIANTS
# -------------------------
def leet_variants(word):
    w = str(word)
    le = w.translate(LEET_MAP)
    return le if le and le != w else None

# -------------------------
# SYMBOL INJECTION (probabilistic)
# -------------------------
def parse_prob_weights(text, max_symbols):
    """
    parse a CSV of weights (weights for 0..max_symbols).
    if invalid or length mismatch, return None => caller will use uniform default.
    """
    if not text:
        return None
    parts = [p.strip() for p in text.split(",") if p.strip() != ""]
    try:
        nums = [float(p) for p in parts]
    except Exception:
        return None
    if len(nums) != max_symbols + 1:
        return None
    # if all zeros or sum zero -> invalid
    if all(n == 0 for n in nums):
        return None
    return nums

def inject_symbols_by_probability(word, max_symbols, symbol_chars, rng, prob_weights=None):
    """
    Return a set of variants for a single word.
    Each variant is created by:
      - sampling k from 0..max_symbols using prob_weights (or uniform)
      - if k==0, variant may be the original word
      - if k>0, insert k symbols at random insertion positions
    We produce a sampled set (not exhaustive) to avoid explosion.
    """
    variants = set()
    L = len(word)
    if L == 0:
        return variants

    # default weights
    if not prob_weights or len(prob_weights) != max_symbols + 1:
        prob_weights = [1.0] * (max_symbols + 1)
    total = sum(prob_weights)
    if total <= 0:
        prob_weights = [1.0] * (max_symbols + 1)
        total = sum(prob_weights)
    weights = [w / total for w in prob_weights]

    tries = max(8, min(200, max_symbols * 12))
    for _ in range(tries):
        k = rng.choices(range(0, max_symbols + 1), weights=weights, k=1)[0]
        if k == 0:
            variants.add(word)
            continue
        syms = [rng.choice(symbol_chars) for _ in range(k)]
        # choose k insertion indices among 0..L inclusive, allowing duplicates
        insert_positions = [rng.randint(0, L) for _ in range(k)]
        pos_map = {}
        for pos, s in zip(insert_positions, syms):
            pos_map.setdefault(pos, []).append(s)
        pieces = []
        for i in range(0, L + 1):
            if i in pos_map:
                pieces.append("".join(pos_map[i]))
            if i < L:
                pieces.append(word[i])
        candidate = "".join(pieces)
        variants.add(candidate)
        if len(variants) >= 300:
            break
    return variants

# -------------------------
# FINAL WORDLIST GENERATOR
# -------------------------
def generate_final_wordlist(profile, use_leet=True, use_symbols=False, max_symbols=2,
                            target_count=5000, random_seed=None, symbol_prob_weights=None):
    rng = random.Random(random_seed or random.randint(1, 1_000_000_000))

    tokens = expand_profile_tokens(profile)
    phones = []
    if profile.get("phone"):
        mainp = digit_only(profile.get("phone"))
        if mainp:
            phones.append(mainp)
    for pn in profile.get("add_numbers", []) or []:
        pcd = digit_only(pn)
        if pcd:
            phones.append(pcd)
    phones = sorted(set(phones))

    years = list(sorted(set([y for y in profile.get("years", []) if str(y).strip().isdigit()] + years_from_age(profile.get("age")))))
    base = base_permutations(tokens, birth_years=years, phones=phones, use_separators=True)
    if not base:
        base = tokens[:]

    result = []
    seen = set()
    order = list(base)
    rng.shuffle(order)

    def push_candidate(c):
        cc = clean_token(c)
        if not cc:
            return False
        if cc in seen:
            return False
        seen.add(cc)
        result.append(cc)
        return True

    # 1) base seeds
    for cand in order:
        if target_count and len(result) >= target_count:
            break
        push_candidate(cand)

    # 2) leet variants
    if use_leet:
        for cand in order:
            if target_count and len(result) >= target_count:
                break
            lv = leet_variants(cand)
            if lv:
                push_candidate(lv)

    # 3) combine pairs (sampled)
    if not target_count or len(result) < target_count:
        pairs = []
        for a, b in itertools.permutations(order, 2):
            pairs.append(f"{a}{b}")
            if len(pairs) >= 20000:
                break
        rng.shuffle(pairs)
        for cand in pairs:
            if target_count and len(result) >= target_count:
                break
            push_candidate(cand)

    # 4) phone derived
    if phones and (not target_count or len(result) < target_count):
        for p in phones:
            if target_count and len(result) >= target_count: break
            push_candidate(p)
            last4 = p[-4:]
            push_candidate(last4)

    # 5) symbol injection (probabilistic)
    if use_symbols and (not target_count or len(result) < target_count):
        seed_list = list(seen)[:]
        rng.shuffle(seed_list)
        for seed in seed_list:
            if target_count and len(result) >= target_count:
                break
            variants = inject_symbols_by_probability(seed, max_symbols, SYMBOL_CHARS, rng, symbol_prob_weights)
            for v in variants:
                if target_count and len(result) >= target_count:
                    break
                push_candidate(v)
            # also apply leet + symbols occasionally
            if use_leet and (not target_count or len(result) < target_count):
                lv = leet_variants(seed)
                if lv:
                    v2 = inject_symbols_by_probability(lv, max_symbols, SYMBOL_CHARS, rng, symbol_prob_weights)
                    for v in v2:
                        if target_count and len(result) >= target_count:
                            break
                        push_candidate(v)

    # 6) extras
    if not target_count or len(result) < target_count:
        extras = []
        for a, b in itertools.permutations(order, 2):
            extras.append(f"{a}.{b}")
            extras.append(f"{a}_{b}")
            if len(extras) >= 50000:
                break
        rng.shuffle(extras)
        for cand in extras:
            if target_count and len(result) >= target_count:
                break
            push_candidate(cand)

    # trim
    if target_count and len(result) > target_count:
        result = result[:target_count]

    return result

# -------------------------
# GUI
# -------------------------
class CUPPXUltimateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CUPP-X Ultimate by Bucky")
        self.root.geometry("980x820")
        self.root.configure(bg="#121212")

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TLabel", background="#121212", foreground="#e6e6e6")
        style.configure("TEntry", fieldbackground="#1b1b1b", foreground="#ffffff")
        style.configure("TButton", background="#2b2b2b", foreground="#ffffff")
        style.configure("TCheckbutton", background="#121212", foreground="#e6e6e6")

        ttk.Label(root, text="CUPP-X Ultimate by Bucky", font=("Helvetica", 18, "bold"), foreground="#00ff88").pack(pady=(10,6))

        frame = ttk.Frame(root)
        frame.pack(fill="both", expand=True, padx=12, pady=8)

        left = ttk.Frame(frame)
        left.pack(side="left", fill="y", padx=(0,8))
        right = ttk.Frame(frame)
        right.pack(side="left", fill="both", expand=True)

        # Profile inputs
        fields = [
            ("First Name", "first_name"),
            ("Last Name", "last_name"),
            ("Nickname(s) (comma)", "nicknames"),
            ("Partner Name", "partner"),
            ("Pet Name", "pet"),
            ("Company", "company"),
            ("Keywords (comma)", "keywords"),
        ]
        self.entries = {}
        for lbl, key in fields:
            ttk.Label(left, text=lbl).pack(anchor="w", pady=(6,0))
            ent = ttk.Entry(left, width=36)
            ent.pack(pady=(0,4), fill="x")
            self.entries[key] = ent

        # other small inputs
        ttk.Label(left, text="Phone Number (digits)").pack(anchor="w", pady=(6,0))
        self.ent_phone = ttk.Entry(left, width=36); self.ent_phone.pack(pady=(0,4), fill="x")
        ttk.Label(left, text="Additional Numbers (comma)").pack(anchor="w", pady=(6,0))
        self.ent_addnums = ttk.Entry(left, width=36); self.ent_addnums.pack(pady=(0,4), fill="x")
        ttk.Label(left, text="Email (optional)").pack(anchor="w", pady=(6,0))
        self.ent_email = ttk.Entry(left, width=36); self.ent_email.pack(pady=(0,4), fill="x")
        ttk.Label(left, text="Years (comma, optional)").pack(anchor="w", pady=(6,0))
        self.ent_years = ttk.Entry(left, width=36); self.ent_years.pack(pady=(0,4), fill="x")
        ttk.Label(left, text="Age (years, optional)").pack(anchor="w", pady=(6,0))
        self.ent_age = ttk.Entry(left, width=36); self.ent_age.pack(pady=(0,4), fill="x")

        # generation controls
        gen_ctrl = ttk.Frame(right)
        gen_ctrl.pack(fill="x", pady=(0,6))
        self.use_leet = tk.BooleanVar(value=True)
        ttk.Checkbutton(gen_ctrl, text="Use leet variants", variable=self.use_leet).pack(side="left", padx=(0,10))
        self.use_symbols = tk.BooleanVar(value=False)
        ttk.Checkbutton(gen_ctrl, text="Enable symbols", variable=self.use_symbols).pack(side="left")
        ttk.Label(gen_ctrl, text="Max symbols per word:").pack(side="left", padx=(12,4))
        self.max_symbols_var = tk.IntVar(value=2)
        ttk.Spinbox(gen_ctrl, from_=1, to=200, textvariable=self.max_symbols_var, width=6).pack(side="left")
        ttk.Label(gen_ctrl, text="Symbol probabilities (comma for 0..max):").pack(side="left", padx=(12,4))
        self.symbol_prob_var = tk.StringVar(value="")
        ttk.Entry(gen_ctrl, textvariable=self.symbol_prob_var, width=24).pack(side="left")
        ttk.Label(gen_ctrl, text="Target words:").pack(side="left", padx=(12,4))
        self.target_words_var = tk.StringVar(value=str(5000))
        ttk.Entry(gen_ctrl, textvariable=self.target_words_var, width=12).pack(side="left")

        # buttons
        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill="x", pady=(6,8))
        ttk.Button(btn_frame, text="Generate Wordlist", command=self.generate_wordlist).pack(side="left")
        self.save_btn = ttk.Button(btn_frame, text="Save Wordlist", command=self.save_wordlist, state="disabled")
        self.save_btn.pack(side="left", padx=(8,0))
        ttk.Button(btn_frame, text="Clear", command=self.clear_all).pack(side="left", padx=(8,0))

        # preview area
        ttk.Label(right, text="Preview (first 500 lines):").pack(anchor="w")
        self.preview_box = tk.Text(right, height=28, bg="#0f0f0f", fg="#dfffe6", insertbackground="#ffffff")
        self.preview_box.pack(fill="both", expand=True, pady=(4,0))

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(root, textvariable=self.status_var, background="#121212", foreground="#bdbdbd").pack(fill="x", padx=12, pady=(6,10))

        self.generated = []
        self.last_output_path = None

    def build_profile(self):
        prof = {}
        for k in ["first_name","last_name","partner","pet","company"]:
            prof[k] = self.entries[k].get().strip() if k in self.entries else ""
        prof["nicknames"] = split_csv_field(self.entries["nicknames"].get()) if "nicknames" in self.entries else []
        prof["keywords"] = split_csv_field(self.entries["keywords"].get()) if "keywords" in self.entries else []
        prof["phone"] = self.ent_phone.get().strip()
        prof["add_numbers"] = split_csv_field(self.ent_addnums.get())
        prof["email"] = self.ent_email.get().strip()
        prof["years"] = split_csv_field(self.ent_years.get())
        prof["age"] = self.ent_age.get().strip()
        return prof

    def generate_wordlist(self):
        prof = self.build_profile()
        use_leet = bool(self.use_leet.get())
        use_symbols = bool(self.use_symbols.get())
        try:
            max_symbols = int(self.max_symbols_var.get() or 0)
        except Exception:
            max_symbols = 2
        # parse target_count (free-form entry)
        try:
            raw = self.target_words_var.get().strip()
            target_count = int(raw) if raw != "" else DEFAULT_WORD_CAP
        except Exception:
            target_count = DEFAULT_WORD_CAP
        if target_count <= 0:
            target_count = DEFAULT_WORD_CAP

        if use_symbols and max_symbols < 1:
            messagebox.showwarning("Symbols", "Max symbols must be >= 1 when symbols enabled.")
            return

        # parse symbol probabilities
        symbol_prob_weights = None
        if use_symbols:
            symbol_prob_weights = parse_prob_weights(self.symbol_prob_var.get().strip(), max_symbols)
            # if invalid, symbol_prob_weights stays None -> generator uses uniform default

        # warn on very large requests
        if target_count >= 500_000:
            proceed = messagebox.askokcancel("Large request", f"You requested {target_count} words. This may use a lot of memory/time and may hang your machine. Continue?")
            if not proceed:
                self.status_var.set("Generation cancelled by user.")
                return

        self.status_var.set("Generating...")
        self.preview_box.delete("1.0", "end")
        self.root.update_idletasks()

        try:
            generated = generate_final_wordlist(prof,
                                                use_leet=use_leet,
                                                use_symbols=use_symbols,
                                                max_symbols=max_symbols,
                                                target_count=target_count,
                                                random_seed=random.randint(1, 1_000_000_000),
                                                symbol_prob_weights=symbol_prob_weights)
            self.generated = generated
            self.preview_box.insert("1.0", f"Generated {len(generated)} words.\n\n")
            for i, w in enumerate(generated[:500]):
                self.preview_box.insert("end", w + "\n")
            if len(generated) > 500:
                self.preview_box.insert("end", f"\n... (showing first 500 of {len(generated)})\n")
            self.status_var.set(f"Generated {len(generated)} words. Press Save to write file.")
            self.save_btn.config(state="normal")
        except MemoryError:
            self.status_var.set("Generation failed: out of memory.")
            messagebox.showerror("Memory Error", "Generation ran out of memory. Try a smaller target or disable symbols.")
            self.generated = []
            self.save_btn.config(state="disabled")
        except Exception as e:
            self.status_var.set("Generation error.")
            messagebox.showerror("Error", f"Failed to generate: {e}")
            self.generated = []
            self.save_btn.config(state="disabled")

    def save_wordlist(self):
        if not self.generated:
            messagebox.showwarning("Warning", "No wordlist generated.")
            return
        default_base = clean_token(self.entries["first_name"].get() or "cuppx")
        default_name = f"{default_base}_{len(self.generated)}.txt"
        p = filedialog.asksaveasfilename(title="Save wordlist as", defaultextension=".txt",
                                         initialfile=default_name,
                                         filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not p:
            self.status_var.set("Save cancelled.")
            return
        try:
            with open(p, "w", encoding="utf-8") as fh:
                for w in self.generated:
                    fh.write(w + "\n")
            self.last_output_path = p
            self.status_var.set(f"Saved {len(self.generated)} words to {p}")
            messagebox.showinfo("Saved", f"Wordlist saved to:\n{p}")
        except Exception as e:
            self.status_var.set("Save failed.")
            messagebox.showerror("Error", f"Failed to save: {e}")

    def clear_all(self):
        for e in self.entries.values():
            e.delete(0, "end")
        self.ent_phone.delete(0, "end")
        self.ent_addnums.delete(0, "end")
        self.ent_email.delete(0, "end")
        self.ent_years.delete(0, "end")
        self.ent_age.delete(0, "end")
        self.preview_box.delete("1.0", "end")
        self.status_var.set("Ready.")
        self.generated = []
        self.save_btn.config(state="disabled")

# -------------------------
# Run
# -------------------------
def main():
    root = tk.Tk()
    app = CUPPXUltimateGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
