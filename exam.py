#!/usr/bin/env python3
"""Exam simulator.

Walks through ex1..exN of an exam folder. For each level it picks one
exercise (the only one if there's just one, otherwise at random), shows the
subject, and grades your function by calling it side by side with the
reference solution: on the README examples and on random inputs.

Usage:
    python3 exam.py [exam_dir] [--seed N] [--time MINUTES]

Your answers go in rendu/<exercise>/<exercise>.py next to this script.
"""

import ast
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RENDU = ROOT / "rendu"
TIMEOUT = 10        # seconds for one grading run
RANDOM_TESTS = 25   # random inputs per grade


# ---------- terminal look ----------

COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def c(text, code):
    return f"\033[{code}m{text}\033[0m" if COLOR else str(text)


def bold(t): return c(t, "1")
def dim(t): return c(t, "2")
def red(t): return c(t, "31")
def green(t): return c(t, "32")
def yellow(t): return c(t, "33")
def cyan(t): return c(t, "36")


def clear():
    if COLOR:
        print("\033[2J\033[H", end="")


def width():
    return min(shutil.get_terminal_size((80, 24)).columns, 90)


def rule(ch="─"):
    print(dim(ch * width()))


def ask(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "q"


def fmt_time(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 3600:d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}"


# ---------- discovery ----------

def find_levels(exam_dir):
    levels = [d for d in exam_dir.iterdir()
              if d.is_dir() and re.fullmatch(r"ex\d+", d.name)]
    return sorted(levels, key=lambda d: int(d.name[2:]))


def find_exercises(level):
    return sorted(d for d in level.iterdir()
                  if d.is_dir() and any(d.glob("*.py")))


def pick(exercises):
    return exercises[0] if len(exercises) == 1 else random.choice(exercises)


def exercise_name(ex):
    # some folders are named like "py_foo.py"
    return ex.name[:-3] if ex.name.endswith(".py") else ex.name


def reference_file(ex):
    name = exercise_name(ex)
    preferred = ex / f"{name}.py"
    return preferred if preferred.exists() else next(ex.glob("*.py"))


# ---------- subject ----------

def readme(ex):
    p = ex / "README.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def subject_text(ex):
    text = readme(ex)
    if not text:
        return "(no README for this exercise)"
    start = text.find("Assignment")
    if start != -1:
        text = text[start:]
    text = re.sub(r"<!--\s*|\s*-->", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    # light highlighting
    text = re.sub(r"^(Assignment|Function signature|Examples)$",
                  lambda m: bold(cyan(m.group(1))), text, flags=re.M)
    text = re.sub(r"^(def .*)$", lambda m: yellow(m.group(1)), text, flags=re.M)
    return text


def examples(ex):
    """(call, expected) pairs from the README's Input/Output blocks."""
    lines = [l.strip() for l in readme(ex).splitlines()]
    pairs = []
    for i, line in enumerate(lines):
        if line == "Input" and i + 3 < len(lines) and lines[i + 2] == "Output":
            pairs.append((lines[i + 1], lines[i + 3]))
    return pairs


def function_name(ex):
    for call, _ in examples(ex):
        m = re.match(r"\s*(\w+)\s*\(", call)
        if m:
            return m.group(1)
    m = re.search(r"def\s+(\w+)\s*\(", readme(ex))
    return m.group(1) if m else None


# ---------- random inputs ----------

def parse_signature(ex):
    """List of type specs per parameter, e.g. ['str', ('list', 'int')]."""
    m = re.search(r"^\s*(?:<!--\s*)?(def .*?:)\s*(?:-->)?\s*$", readme(ex), re.M)
    if not m:
        return None
    try:
        fn = ast.parse(m.group(1) + " pass").body[0]
    except SyntaxError:
        return None

    def spec(node):
        if node is None:
            return "any"
        if isinstance(node, ast.Name):
            return "list" if node.id == "list" else node.id
        if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
                and node.value.id == "list"):
            return ("list", spec(node.slice))
        return "any"

    return [spec(a.annotation) for a in fn.args.args]


def example_args(ex):
    """Per-parameter pools of argument values taken from the README calls."""
    pools = {}
    for call, _ in examples(ex):
        try:
            node = ast.parse(call, mode="eval").body
            values = [ast.literal_eval(a) for a in node.args]
        except (SyntaxError, ValueError):
            continue
        for i, v in enumerate(values):
            pools.setdefault(i, []).append(v)
    return pools


def flatten(values):
    out = []
    for v in values:
        if isinstance(v, list):
            out.extend(flatten(v))
        else:
            out.append(v)
    return out


def infer(value_pool):
    kinds = {type(v).__name__ for v in value_pool}
    return kinds.pop() if len(kinds) == 1 else "int"


def gen_str(pool):
    if pool and random.random() < 0.25:
        s = random.choice(pool)
        return "".join(random.sample(s, len(s)))
    chars = "".join(sorted(set("".join(pool)))) or "abcABC 123"
    max_len = max((len(s) for s in pool), default=8) + 3
    s = "".join(random.choice(chars) for _ in range(random.randint(0, max_len)))
    if random.random() < 0.15:
        s = s + s[::-1]     # palindromes are rare otherwise
    return s


def gen_int(pool):
    lo, hi = (min(pool), max(pool)) if pool else (-10, 10)
    # don't invent negatives when the subject never shows any
    return random.randint(lo - 2 if lo < 0 else max(0, lo - 2), hi + 2)


def gen(spec, pool):
    if spec == "str":
        return gen_str([p for p in pool if isinstance(p, str)])
    if spec == "int":
        return gen_int([p for p in pool if isinstance(p, int)])
    if spec == "bool":
        return random.choice([True, False])
    if spec == "float":
        return round(random.uniform(-100, 100), 2)
    if spec == "list" or isinstance(spec, tuple):
        lists = [p for p in pool if isinstance(p, list)]
        inner = spec[1] if isinstance(spec, tuple) else infer(flatten(lists))
        if lists and random.random() < 0.25:
            base = random.choice(lists)
            return random.sample(base, len(base))
        max_len = max((len(l) for l in lists), default=5) + 2
        n = random.randint(0, max_len)
        if isinstance(inner, tuple):            # matrix: keep rows the same width
            rows = [r for l in lists for r in l if isinstance(r, list)]
            w = random.randint(1, max((len(r) for r in rows), default=3) + 1)
            elems = flatten(lists)
            return [[gen(inner[1], elems) for _ in range(w)] for _ in range(n)]
        elems = [e for l in lists for e in l]
        out = [gen(inner, elems) for _ in range(n)]
        if lists and all(l == sorted(l) for l in lists if l):
            out.sort()                          # inputs in the subject are sorted
        return out
    if pool:
        return random.choice(pool)
    return None


def random_calls(ex, n):
    specs, name = parse_signature(ex), function_name(ex)
    if not specs or not name:
        return []
    pools = example_args(ex)
    calls, seen = [], set()
    for _ in range(n * 6):
        args = [gen(s, pools.get(i, [])) for i, s in enumerate(specs)]
        if len(args) == 2 and type(args[0]) is type(args[1]) and \
                isinstance(args[0], (str, list)) and random.random() < 0.3:
            # second argument derived from the first: rotations, anagrams...
            a = args[0]
            if random.random() < 0.5:
                k = random.randint(0, len(a))
                args[1] = a[k:] + a[:k]
            else:
                shuffled = random.sample(list(a), len(a))
                args[1] = shuffled if isinstance(a, list) else "".join(shuffled)
        call = f"{name}({', '.join(repr(a) for a in args)})"
        if call not in seen:
            seen.add(call)
            calls.append(call)
        if len(calls) >= n * 2:     # extra margin: reference may reject some
            break
    return calls


# ---------- running code ----------

def run_calls(user, ref, calls):
    """Evaluate calls in user's and reference file, in a separate process."""
    payload = json.dumps({"user": str(user), "ref": str(ref) if ref else None,
                          "calls": calls})
    try:
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--run-calls"],
            input=payload, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"error": f"timed out after {TIMEOUT}s (infinite loop?)"}
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return {"error": proc.stderr.strip() or "no output from grader"}


def runner():
    """Child-process mode: import both files quietly, evaluate each call."""
    import contextlib
    import io
    import math
    import runpy

    data = json.loads(sys.stdin.read())
    sink = io.StringIO()

    def load(path, who):
        try:
            with contextlib.redirect_stdout(sink):
                return runpy.run_path(path, run_name="__exam__")
        except BaseException as e:
            raise RuntimeError(f"{who} file crashed on import: "
                               f"{type(e).__name__}: {e}")

    def call(ns, expr):
        try:
            with contextlib.redirect_stdout(sink):
                return True, eval(expr, ns)
        except BaseException as e:
            return False, f"{type(e).__name__}: {e}"

    def equal(a, b):
        if isinstance(a, float) and isinstance(b, float):
            return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
        return type(a) is type(b) and a == b

    try:
        user = load(data["user"], "your")
        ref = load(data["ref"], "reference") if data["ref"] else None
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        return

    results = []
    for expr in data["calls"]:
        u_ok, u = call(user, expr)
        r = {"user": repr(u) if u_ok else None, "user_error": None if u_ok else u}
        if ref is not None:
            r_ok, rv = call(ref, expr)
            r["ref"] = repr(rv) if r_ok else None
            r["ref_error"] = None if r_ok else rv
            r["equal"] = u_ok and r_ok and equal(u, rv)
        results.append(r)
    print(json.dumps({"results": results}))


def same_as_readme(got_repr, expected):
    try:
        got = ast.literal_eval(got_repr)
    except (ValueError, SyntaxError):
        got = got_repr
    try:
        return got == ast.literal_eval(expected)
    except (ValueError, SyntaxError):
        return str(got) == expected


# ---------- grading ----------

def check_ready(ex, answer):
    if not answer.exists() or not answer.read_text().strip():
        print(yellow(f"  Nothing to grade yet. Write your code in "
                     f"{answer.relative_to(ROOT)}"))
        return False
    name = function_name(ex)
    if name and not re.search(rf"^\s*def\s+{name}\s*\(", answer.read_text(), re.M):
        print(red(f"  Your file doesn't define {name}()"))
        return False
    return True


def show_case(call, expected, got, error):
    print(f"    {dim('call    ')} {call}")
    print(f"    {dim('expected')} {green(expected)}")
    print(f"    {dim('got     ')} {red(error) if error else red(got)}")


def grade(ex, answer):
    if not check_ready(ex, answer):
        return False
    ref = reference_file(ex)
    pairs = examples(ex)
    rand = random_calls(ex, RANDOM_TESTS)

    print(dim("  Running your function next to the reference solution..."))
    res = run_calls(answer, ref, [c for c, _ in pairs] + rand)
    if "error" in res:
        print(red(f"  ✗ {res['error']}"))
        print(bold(red("  FAILURE")))
        return False
    results = res["results"]
    ex_res, rand_res = results[:len(pairs)], results[len(pairs):]

    ok = True
    print(bold("\n  Subject examples"))
    for (call, expected), r in zip(pairs, ex_res):
        # the reference is the judge; fall back to the README if it crashed
        passed = r["equal"] if r["ref_error"] is None else \
            r["user_error"] is None and same_as_readme(r["user"], expected)
        mark = green("✓") if passed else red("✗")
        print(f"  {mark} {call}")
        if not passed:
            ok = False
            show_case(call, r["ref"] or expected, r["user"], r["user_error"])

    valid = [(c_, r) for c_, r in zip(rand, rand_res) if r["ref_error"] is None]
    valid = valid[:RANDOM_TESTS]
    if valid:
        fails = [(c_, r) for c_, r in valid if not r["equal"]]
        passed = len(valid) - len(fails)
        colour = green if not fails else red
        print(bold(f"\n  Random tests vs reference: ") +
              colour(f"{passed}/{len(valid)} passed"))
        for c_, r in fails[:3]:
            print(f"  {red('✗')}")
            show_case(c_, r["ref"], r["user"], r["user_error"])
        if len(fails) > 3:
            print(dim(f"    ... and {len(fails) - 3} more"))
        ok = ok and not fails

    print()
    print(bold(green("  ✔ SUCCESS")) if ok else bold(red("  ✘ FAILURE")))
    return ok


def try_call(ex, answer, expr, show_ref):
    if not check_ready(ex, answer):
        return
    name = function_name(ex)
    if name and not re.match(rf"\s*{name}\s*\(", expr):
        expr = f"{name}({expr})"    # "try 'abc'" works too
    res = run_calls(answer, reference_file(ex) if show_ref else None, [expr])
    if "error" in res:
        print(red(f"  {res['error']}"))
        return
    r = res["results"][0]
    print(f"  {dim('yours    ')} {red(r['user_error']) if r['user_error'] else r['user']}")
    if show_ref:
        ref = red(r["ref_error"]) if r["ref_error"] else r["ref"]
        match = r["equal"] or (r["user_error"] and r["user_error"] == r["ref_error"])
        print(f"  {dim('reference')} {ref}   "
              f"{green('match') if match else red('differ')}")


def open_editor(path):
    editor = os.environ.get("EDITOR") or next(
        (e for e in ("code", "nano", "vim", "vi") if shutil.which(e)), None)
    if not editor:
        print(yellow(f"  No editor found. Open {path} yourself."))
        return
    subprocess.call([*editor.split(), str(path)])


# ---------- screens ----------

def header(state, idx, total, name):
    elapsed = time.time() - state["start"]
    dots = "".join(green("●") if i < idx else (yellow("●") if i == idx else dim("○"))
                   for i in range(total))
    clock = fmt_time(elapsed)
    if state["limit"]:
        left = state["limit"] - elapsed
        clock = (red if left < 600 else cyan)(f"{fmt_time(left)} left")
    rule("═")
    print(f" {bold(state['title'])}   Level {idx + 1}/{total} {dots}   ⏱ {clock}")
    print(f" {bold(cyan(name))}   {dim('attempts: ' + str(state['tries']))}")
    rule("═")


def help_bar(practice):
    items = ["[g]rade", "[s]ubject", "[e]dit", "[t]ry <args>", "[c]lear"]
    if practice:
        items.append("[n]ext")
    items.append("[q]uit")
    print(dim("  " + "  ".join(items)))


def play(plan, title, practice, limit):
    state = {"start": time.time(), "limit": limit, "title": title, "tries": 0}
    idx = 0
    while idx < len(plan):
        lvl, ex = plan[idx]
        name = exercise_name(ex)
        answer = RENDU / name / f"{name}.py"
        answer.parent.mkdir(parents=True, exist_ok=True)
        answer.touch()
        state["tries"] = 0

        def screen():
            clear()
            header(state, idx, len(plan), name)
            print(subject_text(ex))
            print()
            rule()
            print(f"  Your file: {bold(answer.relative_to(ROOT))}")
            help_bar(practice)

        screen()
        while True:
            if limit and time.time() - state["start"] > limit:
                print(bold(red("\n  Time's up!")))
                return summary(state, idx, len(plan))
            line = ask(f"\n{cyan('exam')}{dim('>')} ")
            cmd, _, arg = line.partition(" ")
            cmd = cmd.lower()
            if cmd in ("g", "grade"):
                state["tries"] += 1
                if grade(ex, answer):
                    ask(dim("\n  Press Enter for the next level..."))
                    idx += 1
                    break
            elif cmd in ("s", "subject", "c", "clear", ""):
                screen()
            elif cmd in ("e", "edit"):
                open_editor(answer)
                screen()
            elif cmd in ("t", "try"):
                if arg:
                    try_call(ex, answer, arg, show_ref=practice)
                else:
                    print(dim(f"  e.g. try {examples(ex)[0][0] if examples(ex) else 'f(1)'}"))
            elif cmd in ("n", "next") and practice:
                idx += 1
                break
            elif cmd in ("q", "quit", "exit"):
                return summary(state, idx, len(plan))
            else:
                help_bar(practice)
    return summary(state, len(plan), len(plan))


def summary(state, done, total):
    rule("═")
    elapsed = fmt_time(time.time() - state["start"])
    if done >= total:
        print(bold(green(f"  All {total} levels passed in {elapsed}. 🎉")))
    else:
        print(f"  Passed {bold(done)}/{total} levels in {elapsed}.")
    rule("═")


def choose(prompt, options):
    for i, opt in enumerate(options, 1):
        print(f"  {cyan(i)}) {opt}")
    while True:
        a = ask(f"\n{prompt} ")
        if a.lower() == "q":
            sys.exit(0)
        if a.isdigit() and 1 <= int(a) <= len(options):
            return int(a) - 1
        print(dim(f"  Pick 1-{len(options)} (q to quit)"))


def main():
    args = sys.argv[1:]
    limit = None
    if "--seed" in args:
        i = args.index("--seed")
        random.seed(int(args[i + 1]))
        del args[i:i + 2]
    if "--time" in args:
        i = args.index("--time")
        limit = int(args[i + 1]) * 60
        del args[i:i + 2]

    exam_dir = Path(args[0]).resolve() if args else ROOT / "exam03"
    levels = [(l, find_exercises(l)) for l in find_levels(exam_dir)]
    levels = [(l, exs) for l, exs in levels if exs]
    if not levels:
        sys.exit(f"No ex1..exN folders with exercises found in {exam_dir}")

    # start fresh: drop the previous session's answers
    shutil.rmtree(RENDU, ignore_errors=True)
    RENDU.mkdir(exist_ok=True)

    clear()
    rule("═")
    print(bold(f"  {exam_dir.name.upper()} simulator") +
          dim(f"   {len(levels)} levels, "
              f"{sum(len(e) for _, e in levels)} exercises"))
    rule("═")
    mode = choose("Mode?", [
        "Exam — one random exercise per level, in order",
        "Practice a level — random exercise from one level",
        "Practice an exercise — pick it yourself",
    ])

    title = exam_dir.name.upper()
    if mode == 0:
        plan = [(l.name, pick(exs)) for l, exs in levels]
        play(plan, title, practice=False, limit=limit)
    elif mode == 1:
        print()
        i = choose("Level?", [f"{l.name}  {dim(f'({len(exs)} exercises)')}"
                              for l, exs in levels])
        lvl, exs = levels[i]
        plan = [(lvl.name, pick(exs))]
        play(plan, f"{title} · practice", practice=True, limit=limit)
    else:
        flat = [(l.name, e) for l, exs in levels for e in exs]
        print()
        i = choose("Exercise?", [f"{dim(l)}  {exercise_name(e)}" for l, e in flat])
        play([flat[i]], f"{title} · practice", practice=True, limit=limit)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run-calls":
        runner()
    else:
        main()
