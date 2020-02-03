import itertools

from collections import defaultdict, OrderedDict
from typing import Dict, FrozenSet, Generic, Iterable, List, Mapping, OrderedDict, Pattern, Set, Tuple, TypeVar, Union
from functools import partial, reduce, total_ordering
from sortedcontainers import SortedList, SortedDict, SortedSet

class T(object):
    def __init__(self, name):
        self.name = name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, T) and self.name == o.name

    def __str__(self) -> str:
        return F"<{self.name}>"

    __repr__ = __str__

TS = [
    "val"
]

Symbol = Union[str, T]

@total_ordering
class Rule(object):
    def __init__(self, i: int, name: str, pattern: List[Symbol]) -> None:
        self.i = i
        self.name = name
        self.pattern = pattern
    
    def __hash__(self) -> int:
        return hash(self.i)
    
    def __eq__(self, o: object) -> bool:
        return isinstance(o, Rule) and self.i == o.i

    def __lt__(self, o: object) -> bool:
        if isinstance(o, Rule):
            return self.i < o.i
        else:
            raise ValueError(o)

    def __str__(self) -> str:
        pat = " ".join([str(s) for s in self.pattern])
        return F"[{self.i}] {self.name} := {pat}"

    __repr__ = __str__

@total_ordering
class PartialRule(object):
    def __init__(self, r: Rule):
        self.r = r  # (name, rules)
        self.i = 0
    
    def follow(self) -> Symbol:
        return self.r.pattern[self.i]

    def advance(self) -> "PartialRule":
        new_pr = PartialRule(self.r)
        new_pr.i = self.i + 1
        return new_pr

    def is_fin(self) -> bool:
        return self.i == len(self.r.pattern)

    def __hash__(self) -> int:
        return hash((self.r.i, self.i))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, PartialRule):
            return self.r.i == o.r.i and self.i == o.i
        else:
            return False

    def __lt__(self, o: object) -> bool:
        if isinstance(o, PartialRule):
            return (self.r.i, self.i) < (o.r.i, o.i)
        else:
            raise ValueError(o)

    def __str__(self) -> str:
        part_left = self._fmt_pat(self.r.pattern[:self.i])
        part_right = self._fmt_pat(self.r.pattern[self.i:])
        return F"[{self.r.i}] {self.r.name} := {part_left}! {part_right}"

    __repr__ = __str__

    @staticmethod
    def _fmt_pat(pat: List[Symbol]) -> str:
        return ", ".join([str(sym) for sym in pat])

def multidict(g, key):
    d = defaultdict(list)
    for r in g:
        k = key(r)
        d[k].append(r)
    return d

_T = TypeVar("_T")

class SortedSet_(Iterable[_T]):
    pass

def build_init_closures(g: List[Rule]) -> List[SortedSet_[PartialRule]]:
    g_map = multidict(g, key=lambda r: r.name)
    closures = []
    for r in g:
        closure = SortedSet(PartialRule(r) for r in g_map[r.name])
        # initial non-terminals
        nts = SortedSet()
        sym_0 = r.pattern[0]
        if isinstance(sym_0, str):
            nts = SortedSet([sym_0])
        # BFS-style closure building
        new_nts = nts
        while True:
            new_nts2 = SortedSet()
            for nt in new_nts:
                for item in g_map[nt]:
                    pr = PartialRule(item)
                    # non-terminals for next iteration of expansion
                    if (flw := pr.follow()) and isinstance(flw, str) and flw not in nts:
                        new_nts2.add(flw)
                    closure.add(pr)
            if not new_nts2:
                break
            new_nts = new_nts2
            nts.update(new_nts)
        # the closure for current rule r
        closures.append(closure)
    return closures

def close(rules: Iterable[PartialRule], init_closures: Mapping[Symbol, List[SortedSet_[PartialRule]]]) -> FrozenSet[PartialRule]:
    follow_syms = [r.follow() for r in rules if not r.is_fin()]
    follow_nts = [sym for sym in follow_syms if isinstance(sym, str)]
    nt_closures = SortedSet(rules)
    for nt in follow_nts:
        for clos in init_closures[nt]:
            nt_closures.update(clos)
    return frozenset(nt_closures)

Closure = FrozenSet[PartialRule]

# for a closure, get it's follow symbol with associated rules
def follows(closure: Closure) -> Mapping[Symbol, List[PartialRule]]:
    d = defaultdict(list)
    for r in closure:
        if not r.is_fin():
            sym_0 = r.follow()
            d[sym_0].append(r)
    return d

def states(g: List[Rule], st_idx: int) -> Tuple[Mapping[Closure, int], SortedSet_[Closure], Dict[Tuple[Closure, Symbol], Closure]]:
    _closures = build_init_closures(g)
    closures_map = defaultdict(list)
    for r, clos in zip(g, _closures):
        closures_map[r.name].append(clos)

    st0 = close([PartialRule(g[st_idx])], closures_map)
    states = SortedSet([st0])
    states_2_no = {st0: 0}
    st_no = 1
    transitions: Dict[Tuple[Closure, Symbol], Closure] = {}

    def _states_go(state: Closure):
        flws = follows(state)
        new_states = SortedSet()
        for (sym, rules) in flws.items():
            # follows() should all be !is_fin()
            assert(all(not pr.is_fin() for pr in rules))
            new_st = close([pr.advance() for pr in rules if not pr.is_fin()], closures_map)
            if new_st not in states:
                new_states.add(new_st)
            if (state, sym) not in transitions:
                transitions[(state, sym)] = new_st
        return new_states

    level = states
    while True:
        level2 = SortedSet()
        for s in level:
            level2.update(_states_go(s))
        if not level2:
            break
        states.update(level2)
        for s in level2:
            states_2_no[s] = st_no
            st_no += 1
        level = level2
    return (states_2_no, states, transitions)

def prn_states(states: SortedSet_[Closure], transitions: Dict[Tuple[Closure, Symbol], Closure]):
    no_states = list(enumerate(states))
    state_2_no = {s: i for (i, s) in no_states}
    # print states
    for (i, s) in no_states:
        print(F"STATE {i}")
        for pr in s:
            print(F"  {pr}")
    # print transitions
    syms = list(set(sym for (_, sym) in transitions.keys()))
    for (i, s) in no_states:
        trans = []
        for sym in syms:
            dst = None
            if dst := transitions.get((s, sym)):
                trans.append(F"{sym} :> {state_2_no[dst] if dst else None}")
        trans_str = " ".join(trans)
        print(F"{i}: {trans_str}")

def prn_parsing_table(states: SortedSet_[Closure], transitions: Dict[Tuple[Closure, Symbol], Closure]):
    no_states = list(enumerate(states))
    state_2_no: Mapping[Closure, int] = {s: i for (i, s) in no_states}
    ts = sorted(
        set(sym for (_, sym) in transitions.keys() if isinstance(sym, T)),
        key=lambda s: str(s)
    )
    nts = sorted(
        set(sym for (_, sym) in transitions.keys() if isinstance(sym, str)),
        key=lambda s: str(s)
    )

    def the_follows(nt):
        follows = []
        for r in G:
            for (i, sym) in enumerate(r.pattern):
                if sym == nt and i + 1 < len(r.pattern):
                    if isinstance((sym2 := r.pattern[i+1]), T):
                        follows.append(sym2)
        return follows

    nts_follows = {nt: the_follows(nt) for nt in [r.name for r in G]}
    transitions_map = multidict(
        [
            (state_2_no[src], sym, state_2_no[dst])
            for ((src, sym), dst)
            in transitions.items()
        ], key=lambda t3: t3[0])

    # print parsing table
    lines = []
    for (i, s) in no_states:
        trans0 = transitions_map[i]
        shifts = [
            (sym, dst)
            for (_, sym, dst) in trans0
            if isinstance(sym, T)
        ]
        gotos = [
            (sym, dst)
            for (_, sym, dst) in trans0
            if isinstance(sym, str)
        ]
        reduces = [
            (sym, pr.r)
            for pr in s
            if pr.is_fin()
            for sym in nts_follows[pr.r.name]
        ]
        notes   = []
        if set(s for (s, _) in shifts).intersection(s for (s, _) in reduces):
            notes.append("SHIFT-REDUCE-CONFLICT")
        # if len(reduces) > 1:
        #     notes.append("REDUCE-REDUCE-CONFLICT")
        shifts_str  = " ".join(F"{sym} :> {dst}"  for (sym, dst) in shifts )
        gotos_str   = " ".join(F"{sym} :> {dst}"  for (sym, dst) in gotos  )
        reduces_str = " ".join(F"{sym} :> R{r.i}" for (sym, r)   in reduces)
        notes_str   = " ".join(notes)
        lines.append((i, shifts_str, reduces_str, gotos_str, notes_str))
    widths = [
        max(10, max(len(x) for x in [l[i] for l in lines]))
        for i in range(1, 5)
    ]
    (shifts_w, reduces_w, gotos_w, notes_w) = widths
    print(F"""{"id":3} {"SHIFTS":<{shifts_w}} {"REDUCES":<{reduces_w}} {"GOTOS":<{gotos_w}} {"NOTES":<{notes_w}}""")
    for (i, shifts, reduces, gotos, notes) in lines:
        print(F"{i:<3} {shifts:<{shifts_w}} {reduces:<{reduces_w}} {gotos:<{gotos_w}} {notes:<{notes_w}}")

G : List[Rule] = [
    Rule(i, *rdef) for (i, rdef) in enumerate([
        ("G", ["S", T("eof")]),
        ("S", ["S", T("+"), "P"]),
        ("S", ["P"]),
        ("P", ["P", T("x"), "F"]),
        ("P", ["F"]),
        ("F", ["V"]),
        ("F", [T("("), "S", T(")")]),
        ("V", [T("val")]),
    ])
]

# G : List[Rule] = [
#     Rule(0, "E", ["E", T("*"), "B"]),
#     Rule(1, "E", ["E", T("+"), "B"]),
#     Rule(2, "E", ["B"]),
#     Rule(3, "B", [T("0")]),
#     Rule(4, "B", [T("1")]),
# ]

# print("rules")
# for r in G:
#     print(r)
# S = states(G, 0)
# print("states")
# prn_states(*S)
# print("parsing table")
# prn_parsing_table(*S)

# parsing table

# state -> (Sym -> Action, Sym -> Goto)
# Action := Union[Shift(state), Reduce(rule)]
# Goto := state

Action = Union[int, Rule]
Goto = int
ParsingTable = Mapping[int, Tuple[Mapping[T, Action], Mapping[str, Goto]]]

def build_parsing_table(
        states: List[Tuple[int, Closure]],
        transitions: Mapping[Tuple[Closure, Symbol], Closure],
        grammar: List[Rule]
    ) -> ParsingTable:
    table = []

    # helpers
    def all_symbols(g: List[Rule]) -> Set[Union[str, T]]:
        return {
            p
            for r in g
            for p in r.pattern
        }.union({
            r.name for r in g
        })

    nt_2_rules: Mapping[str, List[Rule]] = multidict(G, key=lambda r: r.name)
    def the_firsts(sym: Union[T, str]) -> List[T]:
        if isinstance(sym, T):
            return [sym]
        else:
            rs = nt_2_rules[sym]
            firsts = []
            for r in rs:
                sym0 = r.pattern[0]
                if isinstance(sym0, T):
                    firsts.append(sym0)
                elif sym0 != sym:
                    firsts.extend(the_firsts(sym0))
            return firsts
    firsts_map = {sym: the_firsts(sym) for sym in all_symbols(G)}

    # follows marker
    FLW_PARTIAL_MARKER = object()

    def all_follows(g: List[Rule]):
        nts_follows: Dict[str, Union[List[T], object]] = {}
        def _go(nt: str) -> List[T]:
            # DP Cache
            if _exists := nts_follows.get(nt):
                if _exists == FLW_PARTIAL_MARKER:
                    raise Exception("loop detected")
                else:
                    return _exists
            nts_follows[nt] = FLW_PARTIAL_MARKER
            # scan
            follows = []
            for r in G:
                for (i, sym) in enumerate(r.pattern):
                    if sym == nt:
                        if i + 1 < len(r.pattern):
                            sym2 = r.pattern[i+1]
                            if isinstance(sym2, T):
                                follows.append(sym2)
                            else:
                                follows.extend(firsts_map[sym2])
                        else:
                            follows.extend(_go(r.name))
            nts_follows[nt] = follows
            return list(set(follows))
        for r in g:
            _go(r.name)
        return nts_follows

    nts_follows = all_follows(G)

    # def the_follows(nt):
    #     follows = []
    #     for r in G:
    #         for (i, sym) in enumerate(r.pattern):
    #             if sym == nt:
    #                 if i + 1 < len(r.pattern):
    #                     if isinstance((sym2 := r.pattern[i+1]), T):
    #                         follows.append(sym2)
    #     return follows
    # nts_follows = {nt: the_follows(nt) for nt in [r.name for r in G]}
    state_2_no = {s: i for (i, s) in states}
    transitions_map = multidict(
    [
        (state_2_no[src], sym, state_2_no[dst])
        for ((src, sym), dst)
        in transitions.items()
    ], key=lambda t3: t3[0])
    # constructing table
    for (i, s) in states:
        actions = []
        gotos = []
        for (_, sym, dst) in transitions_map[i]:
            if isinstance(sym, str):  # non-terminal
                gotos.append((sym, dst))
            else:
                if sym.name == "eof":
                    actions.append((sym, -1))
                else:
                    actions.append((sym, dst))
        # >>> LR(0)
        # fin_rs = [pr.r for pr in s if pr.is_fin()]
        # assert(len(fin_rs) <= 1 and not (actions and fin_rs))
        # if fin_rs:
        #     actions.append(fin_rs[0])
        # >>> SLR
        reduces = [
            (sym, pr.r)
            for pr in s
            if pr.is_fin()
            for sym in nts_follows[pr.r.name]
        ]
        assert (
            not set(sym for (sym,_) in actions)
                .intersection(sym for (sym,_) in reduces)
        ), "SHIFT-REDUCE-CONFLICT"
        actions.extend(reduces)
        table.append((i, (dict(actions), dict(gotos))))
    return dict(table)

EOF = object()

def match(t: T, tok):
    return (
        (t.name == "\\" and tok == "\\") or
        (t.name == "." and tok == ".") or
        (t.name == "val" and tok.isdigit()) or
        (t.name == "+" and tok == "+") or
        (t.name == "x" and tok == "x") or
        (t.name == "(" and tok == "(") or
        (t.name == ")" and tok == ")") or
        (t.name == "eof" and tok == EOF)
    )

SHIFT = object()
REDUCE = object()

def parse(tbl: ParsingTable, toks):
    stack = []
    states = [0]
    lookahead = next(toks)

    def act_of_tok(tok, defs):
        for (sym, item) in defs.items():
            if match(sym, tok):
                return item
        else:
            raise Exception("parse error")

    while True:
        state = states[-1]
        if state == -1:
            break
        actions = tbl[state][0]
        action = act_of_tok(lookahead, actions)
        if isinstance(action, int):
            # shift
            stack.append(lookahead)
            # states.append(state)
            lookahead = next(toks)
            states.append(action)
        else:
            # reuce
            size = len(action.pattern)
            partial_stack = stack[-size:]
            stack = stack[:-size]
            states = states[:-size]
            # s_prior = states.pop()
            s_prior = states[-1]
            s_next = tbl[s_prior][1][action.name]
            stack.append((action.name, partial_stack))
            states.append(s_next)
    return stack[0]

def prn_states2(states: List[Tuple[int, Closure]], transitions: Dict[Tuple[Closure, Symbol], Closure]):
    state_2_no = {s: no for (no, s) in states}
    # print states
    for (i, s) in states:
        print(F"STATE {i}")
        for pr in sorted(s):
            print(F"  {pr}")
    # print transitions
    syms = list(set(sym for (_, sym) in transitions.keys()))
    for (i, s) in states:
        trans = []
        for sym in syms:
            dst = None
            if dst := transitions.get((s, sym)):
                trans.append(F"{sym} :> {state_2_no[dst] if dst else None}")
        trans_str = " ".join(trans)
        print(F"{i}: {trans_str}")

def prn_parsed(res):
    def _go(indent, res):
        if isinstance(res, str):
            print(F"{indent}{res}")
            return
        (n, vs) = res
        print(F"{indent}{n}")
        for v in vs:
            _go(indent + "  ", v)
    _go("", res)

(the_states_2_no, the_states, the_transitions) = states(G, 0)
numbered_states = [(no, s) for (s, no) in the_states_2_no.items()]
prn_states2(numbered_states, the_transitions)
toks = iter(itertools.chain(["34", "+", "(", "12", "x", "(", "88", "+", "1", ")", ")"], itertools.repeat(EOF)))
parse_table = build_parsing_table(list((i, s) for s, i in the_states_2_no.items()), the_transitions, G)
res = parse(parse_table, toks)
prn_parsed(res)
