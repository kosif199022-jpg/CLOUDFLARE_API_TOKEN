#!/usr/bin/env python3
"""KCL probes — the typed message types and deterministic probe library of the KOSIF council.

Standalone (Python ≥ 3.10, standard library only) so project_forge.py can vendor this file
verbatim into every generated project. council_lang.py builds the council runtime on top of it.

    python3 kcl_probes.py                 list probes and the inputs each needs
    python3 kcl_probes.py NAME < kwargs   run one probe and print its result as JSON
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import operator
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Callable, Iterable, Mapping

KCL_VERSION = "3.3.0"


# ───────────────────────────── the typed language ─────────────────────────────
class Stance(str, Enum):
    SUPPORT = "support"
    OPPOSE = "oppose"
    ABSTAIN = "abstain"
    NOT_MATERIAL = "not-material"


class Severity(str, Enum):
    NONE = "none"
    LOW = "low"
    MATERIAL = "material"
    BLOCKING = "blocking"

    @property
    def rank(self) -> int:
        return ["none", "low", "material", "blocking"].index(self.value)


@dataclass(frozen=True, slots=True, kw_only=True)
class Evidence:
    source: str
    content: str
    measured: bool = False
    data: Mapping[str, Any] = field(default_factory=dict)

    def wire(self) -> str:
        return f"{'measured' if self.measured else 'observed'}:{self.source}: {self.content}"


@dataclass(frozen=True, slots=True, kw_only=True)
class Objection:
    text: str
    severity: Severity = Severity.MATERIAL
    veto: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ProbeResult:
    probe: str
    ok: bool | None            # None = informational (no pass/fail)
    value: Any
    detail: str
    flag: Severity = Severity.NONE


@dataclass(frozen=True, slots=True, kw_only=True)
class Artifact:
    persona: str
    stance: Stance
    confidence: float
    question: str
    claims: tuple[str, ...] = ()
    evidence: tuple[Evidence, ...] = ()
    objections: tuple[Objection, ...] = ()
    probes_run: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0, 1]")
        if self.stance is Stance.SUPPORT and any(o.severity is Severity.BLOCKING for o in self.objections):
            raise ValueError("a member cannot support while raising a blocking objection")

    @property
    def worst(self) -> Objection | None:
        return max(self.objections, key=lambda o: o.severity.rank, default=None)

    def wire(self) -> dict[str, Any]:
        """JSON wire format — accepted directly by council_aggregate.py."""
        w = self.worst
        return {"id": self.persona, "stance": self.stance.value, "confidence": round(self.confidence, 3),
                "evidence": [e.wire() for e in self.evidence], "claims": list(self.claims),
                "objection": w.text if w else "", "severity": w.severity.value if w else "none",
                "all_objections": [{"text": o.text, "severity": o.severity.value, "veto": o.veto} for o in self.objections],
                "question": self.question, "probes_run": list(self.probes_run)}

    def seal(self) -> str:
        return hashlib.sha256(json.dumps(self.wire(), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


# ───────────────────────────── probe registry ─────────────────────────────
Probe = Callable[..., ProbeResult]
PROBES: dict[str, tuple[Probe, tuple[str, ...], str]] = {}


def probe(name: str, needs: tuple[str, ...], summary: str) -> Callable[[Probe], Probe]:
    def deco(fn: Probe) -> Probe:
        if name in PROBES:
            raise RuntimeError(f"duplicate probe {name}")
        PROBES[name] = (fn, needs, summary)
        return fn
    return deco


def run_probe(name: str, kwargs: Mapping[str, Any]) -> ProbeResult:
    fn, needs, _ = PROBES[name]
    missing = [k for k in needs if k not in kwargs]
    if missing:
        raise ValueError(f"probe {name} needs {missing}")
    return fn(**kwargs)


# ---- arithmetic & logic ------------------------------------------------------
_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Mod: operator.mod, ast.Pow: operator.pow, ast.FloorDiv: operator.floordiv}
_UN = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def safe_arith(expr: str) -> float:
    if not isinstance(expr, str) or len(expr) > 400:
        raise ValueError("expression must be a string ≤ 400 chars")
    src = re.sub(r"(\d+(?:\.\d+)?)\s*%(?!\s*[\d(])", r"(\1/100)", expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace(",", ""))

    def ev(n: ast.AST) -> float:
        match n:
            case ast.Expression(body=b):
                return ev(b)
            case ast.Constant(value=v) if isinstance(v, (int, float)) and not isinstance(v, bool):
                return float(v)
            case ast.BinOp(left=l, op=o, right=r) if type(o) in _BIN:
                if isinstance(o, ast.Pow) and abs(ev(r)) > 64:
                    raise ValueError("exponent too large")
                return _BIN[type(o)](ev(l), ev(r))
            case ast.UnaryOp(op=o, operand=x) if type(o) in _UN:
                return _UN[type(o)](ev(x))
        raise ValueError(f"disallowed syntax: {type(n).__name__}")
    return ev(ast.parse(src, mode="eval"))


@probe("arith", ("expression",), "safe arithmetic (no names/calls); optional `claimed` is checked")
def _arith(expression: str, claimed: Any = None, tolerance: float = 1e-6) -> ProbeResult:
    v = safe_arith(expression)
    if claimed is None:
        return ProbeResult(probe="arith", ok=None, value=v, detail=f"{expression} = {v:g}")
    ok = abs(v - float(str(claimed).replace(",", ""))) <= tolerance
    return ProbeResult(probe="arith", ok=ok, value=v, detail=f"{expression} = {v:g}; claimed {claimed}",
                       flag=Severity.NONE if ok else Severity.BLOCKING)


_FALLACIES = {
    "false dilemma": r"\beither\b.+\bor\b|\bإما\b.+\bأو\b",
    "hasty generalisation": r"\b(always|never|everyone|nobody|all of them)\b|\b(دائماً|أبداً|الجميع|لا أحد)\b",
    "appeal to authority": r"\b(experts say|studies show|scientists agree)\b|يقول الخبراء|أثبتت الدراسات",
    "slippery slope": r"\b(will lead to|next thing|inevitably)\b|سيؤدي حتماً",
    "ad hominem": r"\b(stupid|idiot|liar)\b|غبي|كاذب",
    "bandwagon": r"\b(everybody is doing|most people use|popular so)\b|الكل يستخدم",
}


@probe("fallacies", ("text",), "cue-based scan for common fallacies (flags for human review)")
def _fallacies(text: str) -> ProbeResult:
    hits = [n for n, rx in _FALLACIES.items() if re.search(rx, text, re.I)]
    return ProbeResult(probe="fallacies", ok=not hits, value=hits, detail=", ".join(hits) or "no cue found",
                       flag=Severity.LOW if hits else Severity.NONE)


_STRONG = r"\b(certainly|definitely|obviously|clearly|proves?|guaranteed|always)\b|بالتأكيد|قطعاً|بلا شك|مؤكد|يثبت"


@probe("overclaim", ("text", "evidence_count"), "certainty words vs number of independent evidence items")
def _overclaim(text: str, evidence_count: int) -> ProbeResult:
    strong = len(re.findall(_STRONG, text, re.I))
    bad = strong > 0 and int(evidence_count) < 2
    return ProbeResult(probe="overclaim", ok=not bad, value={"strong_words": strong, "evidence": evidence_count},
                       detail="strong certainty needs ≥2 independent observations" if bad else "calibrated",
                       flag=Severity.MATERIAL if bad else Severity.NONE)


@probe("date_order", ("dates",), "ISO dates must be non-decreasing")
def _date_order(dates: list[str]) -> ProbeResult:
    ds = [date.fromisoformat(d) for d in dates]
    ok = all(a <= b for a, b in zip(ds, ds[1:]))
    return ProbeResult(probe="date_order", ok=ok, value=[d.isoformat() for d in ds], detail="ordered" if ok else "out of order",
                       flag=Severity.NONE if ok else Severity.MATERIAL)


# ---- probability & statistics ----------------------------------------------
@probe("bayes", ("prior", "sensitivity", "false_positive"), "posterior P(H|+) from base rate")
def _bayes(prior: float, sensitivity: float, false_positive: float) -> ProbeResult:
    p = sensitivity * prior / (sensitivity * prior + false_positive * (1 - prior))
    return ProbeResult(probe="bayes", ok=None, value=round(p, 6), detail=f"P(H|+) = {p:.4f} (prior {prior})")


@probe("coherence", ("p_a", "p_b", "p_ab"), "conjunction/union coherence of three probabilities")
def _coherence(p_a: float, p_b: float, p_ab: float) -> ProbeResult:
    issues = []
    if p_ab > min(p_a, p_b) + 1e-9:
        issues.append("conjunction fallacy: P(A∧B) > min(P(A), P(B))")
    if p_a + p_b - p_ab > 1 + 1e-9:
        issues.append("P(A∨B) > 1")
    return ProbeResult(probe="coherence", ok=not issues, value=issues, detail="; ".join(issues) or "coherent",
                       flag=Severity.MATERIAL if issues else Severity.NONE)


@probe("margin_of_error", ("n",), "95% margin of error for a proportion")
def _moe(n: int, p: float = 0.5, z: float = 1.96) -> ProbeResult:
    m = z * math.sqrt(p * (1 - p) / n)
    return ProbeResult(probe="margin_of_error", ok=m <= 0.05, value=round(m, 4), detail=f"±{m * 100:.1f} pts at n={n}",
                       flag=Severity.NONE if m <= 0.05 else Severity.LOW)


@probe("sample_size", ("margin",), "sample size for a target margin of error")
def _sample_size(margin: float, p: float = 0.5, z: float = 1.96, population: int | None = None) -> ProbeResult:
    n0 = z * z * p * (1 - p) / (margin * margin)
    n = n0 / (1 + (n0 - 1) / population) if population else n0
    return ProbeResult(probe="sample_size", ok=None, value=math.ceil(n), detail=f"n ≈ {math.ceil(n)}")


@probe("benford", ("values",), "first-digit Benford test (mean absolute deviation)")
def _benford(values: Iterable[float]) -> ProbeResult:
    digits = [int(str(abs(float(v))).lstrip("0.")[0]) for v in values if float(v) != 0]
    if len(digits) < 50:
        return ProbeResult(probe="benford", ok=None, value=None, detail=f"only {len(digits)} values; Benford needs ≥50")
    c = Counter(digits)
    mad = sum(abs(c[d] / len(digits) - math.log10(1 + 1 / d)) for d in range(1, 10)) / 9
    ok = mad < 0.015
    return ProbeResult(probe="benford", ok=ok, value=round(mad, 5),
                       detail=f"MAD {mad:.4f} ({'conforming' if ok else 'nonconforming — investigate'})",
                       flag=Severity.NONE if ok else Severity.MATERIAL)


@probe("duplicates", ("records", "keys"), "duplicate records by key fields")
def _duplicates(records: list[Mapping[str, Any]], keys: list[str]) -> ProbeResult:
    groups: dict[tuple, list[int]] = {}
    for i, r in enumerate(records):
        groups.setdefault(tuple(str(r.get(k, "")).strip().lower() for k in keys), []).append(i)
    dups = [ix for ix in groups.values() if len(ix) > 1]
    return ProbeResult(probe="duplicates", ok=not dups, value=dups, detail=f"{len(dups)} duplicate group(s)",
                       flag=Severity.MATERIAL if dups else Severity.NONE)


@probe("scenario", ("outcomes",), "expected value and spread of weighted scenarios")
def _scenario(outcomes: list[Mapping[str, float]]) -> ProbeResult:
    tot = sum(o["p"] for o in outcomes)
    if abs(tot - 1) > 1e-6:
        return ProbeResult(probe="scenario", ok=False, value=tot, detail=f"probabilities sum to {tot:g}, not 1",
                           flag=Severity.MATERIAL)
    ev = sum(o["p"] * o["value"] for o in outcomes)
    sd = math.sqrt(sum(o["p"] * (o["value"] - ev) ** 2 for o in outcomes))
    return ProbeResult(probe="scenario", ok=True, value={"expected": round(ev, 4), "sd": round(sd, 4)},
                       detail=f"E = {ev:g}, σ = {sd:g}")


@probe("weighted_rank", ("options", "weights"), "weighted-sum ranking with runner-up margin")
def _weighted_rank(options: Mapping[str, Mapping[str, float]], weights: Mapping[str, float]) -> ProbeResult:
    s = sum(weights.values()) or 1
    scores = sorted(((sum(sc.get(k, 0) * w for k, w in weights.items()) / s, name) for name, sc in options.items()), reverse=True)
    margin = scores[0][0] - scores[1][0] if len(scores) > 1 else None
    fragile = margin is not None and margin < 0.05 * max(abs(scores[0][0]), 1e-9)
    return ProbeResult(probe="weighted_rank", ok=not fragile, value=[[n, round(v, 4)] for v, n in scores],
                       detail=f"winner {scores[0][1]}" + (" (fragile: run decision_sensitivity.py)" if fragile else ""),
                       flag=Severity.LOW if fragile else Severity.NONE)


# ---- finance, tax, audit -----------------------------------------------------
@probe("npv", ("rate", "cashflows"), "net present value (cashflows[0] at t=0)")
def _npv(rate: float, cashflows: list[float]) -> ProbeResult:
    v = sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))
    return ProbeResult(probe="npv", ok=v >= 0, value=round(v, 2), detail=f"NPV @ {rate:.2%} = {v:,.2f}",
                       flag=Severity.NONE if v >= 0 else Severity.MATERIAL)


@probe("irr", ("cashflows",), "internal rate of return by bisection")
def _irr(cashflows: list[float]) -> ProbeResult:
    f = lambda r: sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows))  # noqa: E731
    lo, hi = -0.99, 10.0
    if f(lo) * f(hi) > 0:
        return ProbeResult(probe="irr", ok=None, value=None, detail="no sign change: IRR undefined")
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(lo) * f(mid) > 0 else (lo, mid)
    return ProbeResult(probe="irr", ok=None, value=round(mid, 6), detail=f"IRR ≈ {mid:.2%}")


@probe("payback", ("cashflows",), "simple payback period in periods")
def _payback(cashflows: list[float]) -> ProbeResult:
    cum = 0.0
    for t, cf in enumerate(cashflows):
        prev, cum = cum, cum + cf
        if cum >= 0 and t > 0:
            frac = -prev / cf if cf else 0
            return ProbeResult(probe="payback", ok=True, value=round(t - 1 + frac, 3), detail=f"payback ≈ {t - 1 + frac:.2f} periods")
    return ProbeResult(probe="payback", ok=False, value=None, detail="never pays back", flag=Severity.MATERIAL)


@probe("vat", ("amount", "rate"), "VAT split; inclusive=True treats amount as gross")
def _vat(amount: float, rate: float, inclusive: bool = False) -> ProbeResult:
    net = amount / (1 + rate) if inclusive else amount
    tax = net * rate
    return ProbeResult(probe="vat", ok=None, value={"net": round(net, 2), "vat": round(tax, 2), "gross": round(net + tax, 2)},
                       detail=f"net {net:,.2f} + VAT {tax:,.2f} = {net + tax:,.2f}")


# ---- security, privacy, safety ----------------------------------------------
_SECRET = {
    "openai-key": r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}", "anthropic-key": r"\bsk-ant-[A-Za-z0-9_-]{20,}",
    "github-token": r"\bgh[pousr]_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}", "aws-key": r"\bAKIA[0-9A-Z]{16}\b",
    "slack-token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}", "private-key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "jwt": r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
    "cloudflare-token": r"(?i)cloudflare[^\n]{0,20}[=:]\s*['\"]?[A-Za-z0-9_-]{40}\b",
    "password-assignment": r"(?i)\b(pass(word)?|pwd|secret|api_?key|token)\s*[=:]\s*['\"][^'\"\s]{6,}['\"]",
}


@probe("secrets", ("text",), "credential/secret patterns (values are masked in the output)")
def _secrets(text: str) -> ProbeResult:
    hits = sorted({n for n, rx in _SECRET.items() if re.search(rx, text)})
    return ProbeResult(probe="secrets", ok=not hits, value=hits, detail=("found: " + ", ".join(hits)) if hits else "none found",
                       flag=Severity.BLOCKING if hits else Severity.NONE)


def _luhn(num: str) -> bool:
    d = [int(c) for c in num][::-1]
    return (sum(d[0::2]) + sum(sum(divmod(2 * x, 10)) for x in d[1::2])) % 10 == 0


@probe("pii", ("text",), "personal data: e-mail, phone, Luhn-valid card numbers, Saudi national/IBAN ids")
def _pii(text: str) -> ProbeResult:
    found = []
    if re.search(r"\b[\w.+-]+@[\w-]+\.[\w.-]{2,}\b", text):
        found.append("email")
    if re.search(r"(?<!\d)(?:\+?966|0)?5\d{8}(?!\d)|\+\d{1,3}[\s-]?\d{6,12}", text):
        found.append("phone")
    if any(_luhn(re.sub(r"\D", "", m)) for m in re.findall(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)", text)):
        found.append("card-number")
    if re.search(r"\bSA\d{2}[0-9A-Z]{20}\b", text):
        found.append("iban")
    if re.search(r"(?<!\d)[12]\d{9}(?!\d)", text):
        found.append("national-id-like")
    return ProbeResult(probe="pii", ok=not found, value=found, detail=", ".join(found) or "none found",
                       flag=Severity.BLOCKING if found else Severity.NONE)


@probe("sql_injection", ("code",), "string-built SQL passed to execute()")
def _sqli(code: str) -> ProbeResult:
    rx = r"execute\w*\(\s*(f['\"]|['\"][^'\"]*['\"]\s*(\+|%)|[\w.]+\s*\+)|\.format\([^)]*\)\s*\)|\bSELECT\b[^;\n]*['\"]\s*\+"
    hits = len(re.findall(rx, code, re.I))
    return ProbeResult(probe="sql_injection", ok=not hits, value=hits,
                       detail=f"{hits} string-built query site(s); use parameters" if hits else "parameterised or none",
                       flag=Severity.BLOCKING if hits else Severity.NONE)


_CHECKPOINTS = {
    "captcha": r"captcha|recaptcha|hcaptcha|turnstile|are you (a )?human|not a robot|كابتشا|لست روبوت",
    "otp-mfa": r"\botp\b|2fa|mfa|one[- ]time (code|password)|verification code|authenticator|رمز التحقق|كود التحقق",
    "credential": r"password|passcode|sign[- ]?in|log[- ]?in|credentials|كلمة (المرور|السر)|تسجيل الدخول",
    "payment": r"\bpay\b|payment|checkout|purchase|buy now|credit card|cvv|transfer money|wire|دفع|شراء|تحويل|بطاقة",
    "destructive": r"\bdelete\b|drop (table|database)|rm -rf|format disk|wipe|truncate|force[- ]push|حذف|مسح نهائي|فورمات",
    "publish-send": r"\bsend\b|\bpost\b|publish|submit|tweet|email to|ارسل|إرسال|انشر|نشر",
}


@probe("checkpoint", ("text",), "human-checkpoint classes an agent must not pass alone")
def _checkpoint(text: str) -> ProbeResult:
    hits = [k for k, rx in _CHECKPOINTS.items() if re.search(rx, text, re.I)]
    hard = {"captcha", "otp-mfa", "credential", "payment"} & set(hits)
    flag = Severity.BLOCKING if hard else Severity.MATERIAL if hits else Severity.NONE
    return ProbeResult(probe="checkpoint", ok=not hits, value=hits,
                       detail=("human must act: " + ", ".join(sorted(hard))) if hard else
                       ("confirm first: " + ", ".join(hits)) if hits else "no checkpoint", flag=flag)


# ---- engineering & operations ------------------------------------------------
_GIT = [("destructive", r"push\s+(-f|--force)(?!-with-lease)|reset\s+--hard|branch\s+-D|clean\s+-fdx|filter-branch|push\s+\S+\s+:\S+|push\s+--delete|repo\s+delete"),
        ("remote-write", r"\bpush\b|pr\s+create|pull_request|merge_pull_request|create_pull_request|issue\s+(create|comment)|release\s+create|add_issue_comment|create_or_update_file|push_files"),
        ("local-write", r"\bcommit\b|checkout\s+-b|\bswitch\b|\bmerge\b|\brebase\b|\badd\b|\bstash\b|\btag\b|\binit\b|\bclone\b"),
        ("read-only", r"\bstatus\b|\blog\b|\bdiff\b|\bshow\b|\bfetch\b|\bblame\b|get_file_contents|list_|search_|pull_request_read")]


@probe("git_class", ("command",), "classify a git/GitHub operation: read-only · local-write · remote-write · destructive")
def _git_class(command: str) -> ProbeResult:
    for cls, rx in _GIT:
        if re.search(rx, command, re.I):
            flag = {"destructive": Severity.BLOCKING, "remote-write": Severity.MATERIAL}.get(cls, Severity.NONE)
            return ProbeResult(probe="git_class", ok=cls in {"read-only", "local-write"}, value=cls,
                               detail=f"{cls}" + (" — needs explicit user approval" if flag is not Severity.NONE else ""), flag=flag)
    return ProbeResult(probe="git_class", ok=None, value="unknown", detail="unrecognised operation — treat as remote-write",
                       flag=Severity.MATERIAL)


@probe("retry_safe", ("operation",), "is an operation safe to retry blindly (idempotent)?")
def _retry_safe(operation: str) -> ProbeResult:
    op = operation.strip().upper()
    safe = bool(re.match(r"^(GET|HEAD|OPTIONS|PUT|DELETE)\b|^SELECT\b|^UPSERT\b|IDEMPOTENCY-KEY", op)) and "INSERT" not in op
    return ProbeResult(probe="retry_safe", ok=safe, value=safe,
                       detail="idempotent" if safe else "not idempotent: reconcile state or use an idempotency key first",
                       flag=Severity.NONE if safe else Severity.MATERIAL)


@probe("loop_detect", ("actions",), "repeated identical actions without state change")
def _loop_detect(actions: list[Mapping[str, Any]], window: int = 3) -> ProbeResult:
    sig = [(a.get("action"), a.get("target"), a.get("state_hash")) for a in actions]
    loops = [i for i in range(window - 1, len(sig)) if len(set(sig[i - window + 1:i + 1])) == 1]
    return ProbeResult(probe="loop_detect", ok=not loops, value=loops,
                       detail=f"no-progress loop at step {loops[0]} — change strategy or escalate" if loops else "no loop",
                       flag=Severity.MATERIAL if loops else Severity.NONE)


@probe("budget", ("used", "limit"), "budget headroom (calls, tokens, credits, money)")
def _budget(used: float, limit: float) -> ProbeResult:
    share = used / limit if limit else float("inf")
    flag = Severity.BLOCKING if share >= 1 else Severity.LOW if share >= 0.8 else Severity.NONE
    return ProbeResult(probe="budget", ok=share < 1, value=round(share, 3), detail=f"{share:.0%} of budget used", flag=flag)


@probe("complexity", ("code",), "per-function cyclomatic complexity of Python source")
def _complexity(code: str, limit: int = 10) -> ProbeResult:
    tree = ast.parse(code)
    branch = (ast.If, ast.For, ast.While, ast.IfExp, ast.ExceptHandler, ast.With, ast.Assert, ast.comprehension, ast.Match)
    out = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            c = 1 + sum(isinstance(n, branch) for n in ast.walk(fn)) + sum(len(n.values) - 1 for n in ast.walk(fn) if isinstance(n, ast.BoolOp))
            out[fn.name] = c
    worst = max(out.values(), default=0)
    return ProbeResult(probe="complexity", ok=worst <= limit, value=out, detail=f"max {worst} (limit {limit})",
                       flag=Severity.NONE if worst <= limit else Severity.LOW)


@probe("json_keys", ("document", "required"), "JSON document has exactly/at least the required keys")
def _json_keys(document: Any, required: list[str], exact: bool = False) -> ProbeResult:
    obj = json.loads(document) if isinstance(document, str) else document
    keys = set(obj) if isinstance(obj, dict) else set()
    missing, extra = sorted(set(required) - keys), sorted(keys - set(required)) if exact else []
    ok = not missing and not extra
    return ProbeResult(probe="json_keys", ok=ok, value={"missing": missing, "extra": extra},
                       detail="schema ok" if ok else f"missing {missing} extra {extra}", flag=Severity.NONE if ok else Severity.MATERIAL)


# ---- design, typography, accessibility --------------------------------------
def _rgb(c: str) -> tuple[float, float, float]:
    c = c.strip().lower()
    if m := re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", c):
        h = m.group(1)
        h = "".join(ch * 2 for ch in h) if len(h) == 3 else h
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]
    if m := re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)[^)]*\)", c):
        return tuple(int(x) / 255 for x in m.groups())  # type: ignore[return-value]
    raise ValueError(f"unsupported colour {c!r}")


def luminance(c: str) -> float:
    f = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4  # noqa: E731
    r, g, b = (f(v) for v in _rgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


@probe("contrast", ("fg", "bg"), "WCAG 2.x contrast ratio; large=True uses the 3:1 threshold")
def _contrast(fg: str, bg: str, large: bool = False) -> ProbeResult:
    r = contrast_ratio(fg, bg)
    need = 3.0 if large else 4.5
    return ProbeResult(probe="contrast", ok=r >= need, value=round(r, 2),
                       detail=f"{r:.2f}:1 ({'AA pass' if r >= need else f'fails AA, needs {need}:1'}{'; AAA' if r >= (4.5 if large else 7) else ''})",
                       flag=Severity.NONE if r >= need else Severity.BLOCKING)


@probe("type_scale", ("base",), "modular type scale (px) from a base size and ratio")
def _type_scale(base: float, ratio: float = 1.25, steps: int = 6) -> ProbeResult:
    scale = [round(base * ratio ** i, 2) for i in range(-1, steps)]
    return ProbeResult(probe="type_scale", ok=base >= 16, value=scale, detail=f"{scale}" + ("" if base >= 16 else " — body text < 16px"),
                       flag=Severity.NONE if base >= 16 else Severity.LOW)


@probe("touch_target", ("width", "height"), "touch target ≥ 44×44 CSS px (WCAG 2.5.5 / Apple HIG)")
def _touch_target(width: float, height: float) -> ProbeResult:
    ok = width >= 44 and height >= 44
    return ProbeResult(probe="touch_target", ok=ok, value=[width, height], detail="ok" if ok else "below 44×44",
                       flag=Severity.NONE if ok else Severity.MATERIAL)


@probe("line_length", ("chars",), "measure (characters per line) 45–75 for body text")
def _line_length(chars: int) -> ProbeResult:
    ok = 45 <= chars <= 75
    return ProbeResult(probe="line_length", ok=ok, value=chars, detail="comfortable" if ok else "outside 45–75",
                       flag=Severity.NONE if ok else Severity.LOW)


@probe("readability", ("text",), "average words per sentence and long-word share (Arabic + Latin)")
def _readability(text: str) -> ProbeResult:
    sentences = [s for s in re.split(r"[.!?؟\n]+", text) if s.strip()]
    words = re.findall(r"[\w؀-ۿ]+", text)
    wps = len(words) / max(len(sentences), 1)
    long_share = sum(len(w) > 9 for w in words) / max(len(words), 1)
    ok = wps <= 22 and long_share <= 0.15
    return ProbeResult(probe="readability", ok=ok, value={"words_per_sentence": round(wps, 1), "long_word_share": round(long_share, 3)},
                       detail="readable" if ok else "long sentences or heavy vocabulary", flag=Severity.NONE if ok else Severity.LOW)


@probe("prompt_parts", ("prompt",), "LLM prompt skeleton: task, format, delimiters, examples, edge cases")
def _prompt_parts(prompt: str) -> ProbeResult:
    low = prompt.lower()
    parts = {"task": bool(re.search(r"\b(write|create|analy[sz]e|classify|summari[sz]e|extract|translate|generate|review|اكتب|حلل|لخص|صنف|استخرج)", low)),
             "format": bool(re.search(r"json|table|bullet|markdown|format|schema|heading|جدول|تنسيق|نقاط", low)),
             "delimiters": bool(re.search(r"<\w+>|```|\"\"\"|###", prompt)),
             "examples": bool(re.search(r"example|e\.g\.|for instance|مثال", low)),
             "edge_cases": bool(re.search(r"\bif\b.*\b(missing|unknown|not|unsure|empty)|إذا (لم|كان)", low))}
    miss = [k for k, v in parts.items() if not v]
    return ProbeResult(probe="prompt_parts", ok=len(miss) <= 1, value=parts, detail=("missing: " + ", ".join(miss)) if miss else "complete",
                       flag=Severity.NONE if len(miss) <= 1 else Severity.MATERIAL)


# ---- media ---------------------------------------------------------------------
@probe("beat", ("bpm",), "beat, bar and 8-bar phrase durations for cutting on the music")
def _beat(bpm: float, beats_per_bar: int = 4) -> ProbeResult:
    b = 60 / bpm
    return ProbeResult(probe="beat", ok=None, value={"beat_s": round(b, 4), "bar_s": round(b * beats_per_bar, 4), "phrase8_s": round(b * beats_per_bar * 8, 3)},
                       detail=f"beat {b:.3f}s · bar {b * beats_per_bar:.3f}s")


@probe("ev100", ("aperture", "shutter", "iso"), "exposure value normalised to ISO 100")
def _ev100(aperture: float, shutter: float, iso: float) -> ProbeResult:
    ev = math.log2(aperture ** 2 / shutter) - math.log2(iso / 100)
    return ProbeResult(probe="ev100", ok=None, value=round(ev, 2), detail=f"EV100 = {ev:.2f}")


_LUFS = {"spotify": -14, "youtube": -14, "apple music": -16, "podcast": -16, "tiktok": -14, "instagram": -14,
         "broadcast ebu": -23, "broadcast atsc": -24, "netflix": -27, "cinema": -27}


@probe("lufs_target", ("platform",), "integrated loudness target per platform")
def _lufs_target(platform: str, measured: float | None = None) -> ProbeResult:
    t = _LUFS.get(platform.lower())
    if t is None:
        return ProbeResult(probe="lufs_target", ok=None, value=None, detail=f"unknown platform; known: {sorted(_LUFS)}")
    if measured is None:
        return ProbeResult(probe="lufs_target", ok=None, value=t, detail=f"target {t} LUFS")
    ok = abs(measured - t) <= 1
    return ProbeResult(probe="lufs_target", ok=ok, value={"target": t, "measured": measured},
                       detail=f"{measured} vs {t} LUFS", flag=Severity.NONE if ok else Severity.LOW)


@probe("seal", ("payload",), "SHA-256 seal of any JSON payload (tamper evidence)")
def _seal(payload: Any) -> ProbeResult:
    h = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return ProbeResult(probe="seal", ok=None, value=h, detail=h[:16] + "…")



def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(json.dumps({n: {"needs": list(needs), "summary": s} for n, (_, needs, s) in sorted(PROBES.items())},
                         ensure_ascii=False, sort_keys=True))
        return 0
    try:
        r = run_probe(argv[1], json.load(sys.stdin))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(asdict(r), ensure_ascii=False, sort_keys=True, default=str))
    return 0 if r.ok is not False else 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
