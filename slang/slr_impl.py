from dataclasses import dataclass
from typing import (
    Callable, FrozenSet, Generic, Iterable, Iterator, Mapping, Optional,
    Set, Tuple, TypeVar, Protocol, List, Union, Any
)
from collections import defaultdict
from functools import total_ordering

@total_ordering
class Symbol(object):
    def __init__(self, s: str) -> None:
        self.s = s
    
    def __str__(self) -> str:
        return self.s

    __repr__ = __str__

    def __hash__(self) -> int:
        return hash(self.s)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Symbol) and self.s == o.s

    def __lt__(self, o: object) -> bool:
        if isinstance(o, Symbol):
            return self.s < o.s
        else:
            raise ValueError(F"{o} not comparable with Symbol")

class Terminal(Symbol):
    pass

class NonTerminal(Symbol):
    pass

EOF = Terminal("eof")

class Rule(object):
    action: Callable[[List[Any]], Any]

    def __init__(
        self, rid: int, symbol: NonTerminal,
        pattern: List[Symbol],
        action: Optional[Callable[[List[Any]], Any]] = None,
    ) -> None:
        self.rid = rid
        self.symbol = symbol
        self.pattern = pattern
        self.action = action or (lambda l: l)

    def __str__(self) -> str:
        pat_str = " ".join(str(p) for p in self.pattern)
        return F"{self.symbol} := {pat_str}"

    __repr__ = __str__

    def __hash__(self) -> int:
        return hash(self.rid)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Rule) and self.rid == o.rid

class PartialRule(object):
    def __init__(self, rule: Rule, next_pos: int = 0) -> None:
        assert next_pos <= len(rule.pattern), "invalid next_pos"
        self.rule = rule
        self.next_pos = next_pos

    def next_symbol(self) -> Symbol:
        return self.rule.pattern[self.next_pos]

    def advance(self) -> "PartialRule":
        return PartialRule(self.rule, self.next_pos + 1)

    def is_fin(self) -> bool:
        return self.next_pos == len(self.rule.pattern)

    def __hash__(self) -> int:
        return hash((self.rule.rid, self.next_pos))

    def __eq__(self, o: object) -> bool:
        return isinstance(o, PartialRule) and (
            (self.rule.rid, self.next_pos) ==
            (o.rule.rid, o.next_pos)
        )

    def __str__(self) -> str:
        part_left = ", ".join(str(p) for p in self.rule.pattern[:self.next_pos])
        part_right = ", ".join(str(p) for p in self.rule.pattern[self.next_pos:])
        return F"{self.rule.symbol} := {part_left}! {part_right}"

    __repr__ = __str__

@dataclass
class Association(object):
    assoc: str

LeftAssoc = Association("left")
RightAssoc = Association("right")

def multidict(g, key):
    d = defaultdict(list)
    for r in g:
        k = key(r)
        d[k].append(r)
    return d

def _all_symbols(rules: List[Rule]) -> Set[Symbol]:
    return {sym for r in rules for sym in r.pattern}.union({
        r.symbol for r in rules
    })

def _compute_firsts(
    rules: List[Rule],
    rules_map: Mapping[NonTerminal, List[Rule]],
    symbols: List[Symbol]
) -> Mapping[Symbol, Set[Terminal]]:

    parital_marker = object()
    firsts_map = {}

    def first(sym: Symbol) -> Set[Terminal]:
        if (_exists := firsts_map.get(sym)) is not None:
            if _exists is parital_marker:
                raise Exception("loop detected")            
            elif _exists:  # make type checker happy
                return _exists

        firsts_map[sym] = parital_marker
        res = None
        if isinstance(sym, Terminal):
            res = {sym}
        elif isinstance(sym, NonTerminal):
            rs = rules_map[sym]
            firsts = set()
            for r in rs:
                sym0 = r.pattern[0]
                if isinstance(sym0, Terminal):
                    firsts.add(sym0)
                elif isinstance(sym0, NonTerminal) and sym0 != sym:
                    firsts.update(first(sym0))
            res = firsts
        else:
            raise Exception("invalid case")

        firsts_map[sym] = res
        return res
    
    for sym in symbols:
        first(sym)
    return firsts_map

def _compute_follows(
    rules: List[Rule],
    rules_map: Mapping[NonTerminal, List[Rule]],
    firsts_map: Mapping[Symbol, Set[Terminal]],
    symbols: List[Symbol],
) -> Mapping[NonTerminal, Set[Terminal]]:
    partial_marker = object()
    nts_follows = {}

    def _go(nt: Symbol) -> List[Terminal]:
        # DP Cache
        if _exists := nts_follows.get(nt):
            if _exists == partial_marker:
                raise Exception("loop detected")
            elif _exists:
                return _exists
        nts_follows[nt] = partial_marker
        # scan
        follows = set()
        for r in rules:
            for (i, sym) in enumerate(r.pattern):
                if sym == nt:
                    if i + 1 < len(r.pattern):
                        sym2 = r.pattern[i+1]
                        if isinstance(sym2, Terminal):
                            follows.add(sym2)
                        elif isinstance(sym2, NonTerminal):
                            follows.update(firsts_map[sym2])
                    elif r.symbol != nt:
                        follows.update(_go(r.symbol))
        nts_follows[nt] = follows
        return list(set(follows))

    for sym in symbols:
        if isinstance(sym, NonTerminal):
            _go(sym)
    return nts_follows

T_BFS_ITEM = TypeVar("BFS_ITEM")

def bfs_traverse(
    inits: Set[T_BFS_ITEM],
    f: Callable[[Set[T_BFS_ITEM]], Set[T_BFS_ITEM]]
):
    steps = inits
    while steps:
        steps = f(steps)

def _compute_nt_closure_cache(
    rules: List[Rule],
    rules_map: Mapping[NonTerminal, List[Rule]],
    symbols: List[Symbol],
) -> Mapping[NonTerminal, Set[PartialRule]]:
    closures = {}
    for sym in symbols:
        if isinstance(sym, NonTerminal):
            closure = set(PartialRule(r) for r in rules_map[sym])
            nts = set([sym])

            def _go(nts: Set[NonTerminal]):
                prs = {
                    PartialRule(r)
                    for nt in nts
                    for r in rules_map[nt]
                }
                closure.update(prs)
                this_nts = set()
                for pr in prs:
                    if not pr.is_fin():
                        sym = pr.next_symbol()
                        if isinstance(sym, NonTerminal):
                            this_nts.add(sym)
                return this_nts.difference(nts)

            bfs_traverse(nts, _go)
            closures[sym] = closure
    return closures

def _compute_closure(
    partials: Set[PartialRule],
    closure_cache: Mapping[NonTerminal, Set[PartialRule]]
) -> FrozenSet[PartialRule]:
    nexts = set()
    for p in partials:
        if not p.is_fin():
            sym_next = p.next_symbol()
            if isinstance(sym_next, NonTerminal):
                nexts.add(sym_next)
    return frozenset(partials.union({
        pr
        for sym in nexts
        for pr in closure_cache[sym]
    }))

_T_Closure = FrozenSet[PartialRule]
_T_Transition = Mapping[Symbol, int]

def _group_by_next_symbol(
    prs: Iterable[PartialRule]
) -> Mapping[Symbol, List[PartialRule]]:
    m = defaultdict(list)
    for pr in prs:
        if not pr.is_fin():
            m[pr.next_symbol()].append(pr)
    return m

def _compute_states(
    rules: List[Rule],
    rules_map: Mapping[NonTerminal, List[Rule]],
    closure_cache: Mapping[NonTerminal, Set[PartialRule]],
    init_rule: Rule,
) -> Tuple[Mapping[_T_Closure, int], Mapping[int, _T_Transition]]:
    st0 = _compute_closure(set([PartialRule(init_rule)]), closure_cache)
    states = {frozenset(st0): 0}
    st_no = [0]
    transitions = defaultdict(dict)

    def _states_go(states_in: Set[_T_Closure]):
        new_states = set()
        for state in states_in:
            flws = _group_by_next_symbol(state)
            for (sym, sub_rules) in flws.items():
                new_st = _compute_closure(
                    set(pr.advance() for pr in sub_rules if not pr.is_fin()),
                    closure_cache)
                if new_st not in states:
                    # add new state
                    st_no[0] += 1
                    states[new_st] = st_no[0]
                    # for next iteration of BFS
                    new_states.add(new_st)
                # each (state, sym) is unique, so no overwrite will occur
                transitions[states[state]][sym] = states[new_st]
        return new_states

    bfs_traverse(set(states.keys()), _states_go)
    return (states, transitions)

def print_states(states: Mapping[FrozenSet[PartialRule], int]):
    for (i, s) in sorted((i, s) for (s, i) in states.items()):
        print(F"STATE[{i}]")
        for pr in sorted(s, key=lambda pr: pr.rule.rid):
            print(F"  {str(pr)}")

Action = Union[int, Rule]
Goto = int
ParsingTable = Mapping[
    int,
    Tuple[
        Mapping[Terminal, Action],
        Mapping[NonTerminal, Goto]
    ]
]

T_AssocPrecedDefs = Tuple[
    Mapping[Rule, Tuple[int, Association]],
    Mapping[Terminal, Tuple[int, Association]],
]

def _compute_assoc_preced_mapping(
    rules: List[Rule],
    op_defs: List[Tuple[Association, List[Terminal]]]
) -> T_AssocPrecedDefs:
    t_2_rules = defaultdict(list)
    t_2_preced = {}
    r_2_preced = {}
    for r in rules:
        for sym in r.pattern:
            if isinstance(sym, Terminal):
                t_2_rules[sym].append(r)
    for (i, (assoc, ts)) in enumerate(op_defs):
        for t in ts:
            assert (t not in t_2_preced), F"{t} occured in multiple AssocPreced definitions"
            t_2_preced[t] = (i, assoc)
            for r in t_2_rules[t]:
                assert (r not in r_2_preced), F"{r} assigned multiple AssocPreced definitions"
                r_2_preced[r] = (i, assoc)
    return (r_2_preced, t_2_preced)

def _compute_parsing_table(
    states: Mapping[_T_Closure, int],
    transitions: Mapping[int, _T_Transition],
    follows: Mapping[NonTerminal, Set[Terminal]],
    assoc_preced_defs: T_AssocPrecedDefs,
) -> ParsingTable:
    (r_2_preced, t_2_preced) = assoc_preced_defs
    table = []
    for (i, s) in sorted((i, s) for (s, i) in states.items()):
        actions = []
        gotos = []
        for (sym, dst) in transitions[i].items():
            if isinstance(sym, NonTerminal):  # non-terminal
                gotos.append((sym, dst))
            elif isinstance(sym, Terminal):
                if sym is EOF:
                    actions.append((sym, -1))
                else:
                    actions.append((sym, dst))
        # >>> SLR
        reduces = [
            (sym, pr.rule)
            for pr in s
            if pr.is_fin()
            for sym in follows[pr.rule.symbol]
        ]
        actions_map = dict(actions)
        reduces_map = dict(reduces)
        merged_actions = []
        for sym in set(actions_map.keys()).union(reduces_map):
            sft = actions_map.get(sym)
            rdc = reduces_map.get(sym)
            act = None
            if sft and rdc:
                try:
                    sft_preced = t_2_preced[sym]
                    rdc_preced = r_2_preced[rdc]
                except KeyError:
                    raise Exception(F"SHIFT-REDUCE Conflict, maybe specify an AssocPreced for {sym}")
                if sft_preced > rdc_preced:
                    act = (sym, sft)
                elif sft_preced < rdc_preced:
                    act = (sym, rdc)
                elif sft_preced[1] == LeftAssoc:
                    act = (sym, rdc)
                elif sft_preced[1] == RightAssoc:
                    act = (sym, sft)
            elif sft:
                act = (sym, sft)
            elif rdc:
                act = (sym, rdc)
            assert act is not None
            merged_actions.append(act)

        actions.extend(reduces)
        table.append((i, (dict(merged_actions), dict(gotos))))
    return dict(table)

Token = TypeVar("Token")

class Matcher(Protocol[Token]):
    # EOF matches None regardlessly
    def match(self, sym: Terminal, tok: Token) -> bool: ...

def match(matcher: Matcher[Token], sym: Terminal, tok: Optional[Token]):
    return sym == EOF if tok is None else matcher.match(sym, tok) 

def next_token(toks: Iterator[Token]) -> Optional[Token]:
    try:
        return next(toks)
    except StopIteration:
        return None

class Grammar(Generic[Token]):
    rules: List[Rule]

    def __init__(
        self,
        rules: List[Rule],
        op_defs: List[Tuple[Association, List[Terminal]]],
        matcher: Matcher[Token]
    ) -> None:
        self.rules = rules
        self.matcher = matcher
        rules_map = multidict(rules, key=lambda r: r.symbol)
        symbols = list(_all_symbols(self.rules))
        firsts = _compute_firsts(rules, rules_map, symbols)
        follows = _compute_follows(rules, rules_map, firsts, symbols)
        nt_closure_cache = _compute_nt_closure_cache(rules, rules_map, symbols)
        (states, transitions) = _compute_states(rules, rules_map, nt_closure_cache, rules[0])
        assoc_preced_defs = _compute_assoc_preced_mapping(rules, op_defs)
        table = _compute_parsing_table(states, transitions, follows, assoc_preced_defs)
        # self._rules_map = rules_map
        self.symbols = symbols
        # self._firsts = firsts
        # self._follows = follows
        # self._nt_closure_cache = nt_closure_cache
        self.states = states
        self.table = table

    def parse(self, toks: Iterator[Token]):
        stack = []
        states = [0]
        lookahead = next_token(toks)

        def act_of_tok(tok, defs):
            for (sym, item) in defs.items():
                if match(self.matcher, sym, tok):
                    return item
            else:
                raise Exception("parse error")

        while True:
            state = states[-1]
            if state == -1:
                break
            actions = self.table[state][0]
            action = act_of_tok(lookahead, actions)
            from slang.stlc.lexer import ARROW
            if isinstance(action, int):
                # shift
                stack.append(lookahead)
                # states.append(state)
                lookahead = next_token(toks)
                states.append(action)
            else:
                # reuce
                size = len(action.pattern)
                partial_stack = stack[-size:]
                stack = stack[:-size]
                states = states[:-size]
                # s_prior = states.pop()
                s_prior = states[-1]
                s_next = self.table[s_prior][1][action.symbol]
                stack.append((action, partial_stack))
                states.append(s_next)
        return stack[0]

    def print_states(self):
        print_states(self.states)

    def print_parsing_table(self):
        ts = sorted(sym for sym in self.symbols if isinstance(sym, Terminal))
        nts = sorted(sym for sym in self.symbols if isinstance(sym, NonTerminal))
        widths = []
        table = []
        for i in range(len(self.states)):
            (actions, gotos) = self.table[i]
            strs = []
            for t in ts:
                if act := actions.get(t):
                    strs.append(F"r{act.rid}" if isinstance(act, Rule) else str(act))
                else:
                    strs.append("")
            for nt in nts:
                if g := gotos.get(nt):
                    strs.append(str(g))
                else:
                    strs.append("")
            table.append(strs)
        widths = [max(len(r[i]) for r in table) for i in range(len(ts) + len(nts))]
        sym_ts_w = [len(str(sym)) for sym in ts]
        sym_nts_w = [len(str(sym)) for sym in nts]
        widths[:len(ts)] = [max(ws) for ws in zip(widths[:len(ts)], sym_ts_w)]
        widths[-len(nts):] = [max(ws) for ws in zip(widths[-len(nts):], sym_nts_w)]
        # header
        actions_width = sum(widths[:len(ts)] or [0])
        gotos_width = sum(widths[-len(nts):] or [0])
        print(F"""{"state":5} {"actions":{actions_width+len(ts)-1}} {"gotos":{gotos_width+len(nts)-1}}""")
        # symbols
        s_ts = " ".join(F"{str(sym):{w}}" for (sym, w) in zip(ts, widths[:len(ts)]))
        s_nts = " ".join(F"{str(sym):{w}}" for (sym, w) in zip(nts, widths[-len(nts):]))
        print(F"""{"":5} {s_ts} {s_nts}""")
        # states
        for (i, row) in enumerate(table):
            s = " ".join(F"{s:{w}}" for (s, w) in zip(row, widths))
            print(F"""{i:<5} {s}""")

def grammar(
    rules: List[Tuple[NonTerminal, List[Symbol], Callable[[Any], Any]]],
    op_defs: List[Tuple[Association, List[Terminal]]],
    matcher: Matcher[Token],
) -> Grammar:
    return Grammar([Rule(i, *args) for (i, args) in enumerate(rules)], op_defs, matcher)

def print_parsed(res):
    def _go(indent, res):
        if isinstance(res, tuple):
            (n, vs) = res
            print(F"{indent}{n.symbol}")
            for v in vs:
                _go(indent + "  ", v)
        else:
            print(F"{indent}{res}")

    _go("", res)

def apply_tranx(res):
    def go(res):
        if isinstance(res, tuple):
            (r, vs) = res
            vs = [go(v) for v in vs]
            return r.action(vs)
        else:
            return res
    return go(res)
