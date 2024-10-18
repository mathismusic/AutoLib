# Om Sri Sai Ram

import graphviz as gv
from automaton import automaton
import dfa

class nfa(automaton):
    def __init__(self, Q: set|list|int, A: set|list|int, Q_0: set|list|str, F: set|list|str, name:str|None=None) -> None:
        super().__init__(Q, A, F, name)
        self.Q_0 = self._format(Q_0)
        assert self.Q_0.issubset(self.Q), f'Q_0 = {self.Q_0} not a subset of Q = {self.Q}'

    def add_vertex(self, name=None, start=False, final=False):
        self.Q.add(name) 
        if start: self.Q_0.add(name)
        if final: self.F.add(name)
    
    def add_edge(self, q1, q2, a):
        assert q1 in self.Q, f'q1 = {q1} not in Q = {self.Q}'
        assert q2 in self.Q, f'q2 = {q2} not in Q = {self.Q}'
        assert a in self.A, f'a = {a} not in A = {self.A}'
        if (q1, a) not in self.delta:
            self.delta[(q1, a)] = set([q2])
        else:
            self.delta[(q1, a)].add(q2)
    
    def remove_edge(self, q1, q2, a):
        assert q1 in self.Q, f'q1 = {q1} not in Q = {self.Q}'
        assert q2 in self.Q, f'q2 = {q2} not in Q = {self.Q}'
        assert a in self.A, f'a = {a} not in A = {self.A}'
        if (q1, a) not in self.delta: return
        it: set = self.delta[(q1, a)]
        if q2 in it:
            it.remove(q2)
            if len(it) == 0:
                self.delta.pop((q1, a))
    
    def draw_format(self, q):
        return q
    
    def draw(self, savefig=False, directory=None, filename=None):
        fig = gv.Digraph(self.name, format='png')
        status = {q: False for q in self.Q}
        for q in self.Q_0:
            fig.node(str(q), shape='circle', color='red')
            status[q] = True
        for q in self.F:
            if status[q]:
                fig.node(str(q), shape='doublecircle', color='red')
            else:
                fig.node(str(q), shape='doublecircle')
            status[q] = True
        for q in self.Q:
            if status[q]: continue
            fig.node(str(q), shape='circle')
        for (q1, a), q2s in self.delta.items():
            for q2 in q2s:
                fig.edge(str(q1), str(q2), label=a)
        # want the graph to be more left to right than top to bottom
        fig.graph_attr['rankdir'] = 'LR'
        # and fairly large
        fig.graph_attr['size'] = '10'
        if savefig:
            fig.render(filename if filename else self.name, directory=directory, view=False)
        return fig
    
    def extended_delta(self, X: set, word: str):
        if len(X) == 0: return X
        assert X.issubset(self.Q), f'X = {X} not a subset of Q = {self.Q}'

        # Let D = extended delta and d for delta. We use the recurrence:
        # D(X, epsilon) = X
        # D(X, a) = union_{q' E X} d(q', a)
        # D(X, aw) = D(D(X, a),w)

        if len(word) == 0:
            return X
        # recurse. We recurse on single head and tail (this seems to be faster in Python than on l[:-1] and l[-1])
        head = word[0]
        tail = word[1:]
        # print("yee", head, tail)
        one_step_lst = [self.delta[(q, head)] for q in X if (q, head) in self.delta]
        one_step = set.union(*one_step_lst) if len(one_step_lst) > 0 else set()
        return self.extended_delta(one_step, tail)

    def clear_edges(self):
        self.delta = {}
        return self
    
    def to_dfa(self):
        # we will use the powerset construction
        def powerset(s):
            # https://stackoverflow.com/questions/1482308/how-to-get-all-subsets-of-a-set-powerset
            masks = [1 << i for i in range(len(s))]
            for i in range(1 << len(s)):
                yield frozenset(elem for mask, elem in zip(masks, s) if i & mask)
        Q = set(powerset(self.Q))
        Q_0 = frozenset(self.Q_0)
        # print(Q)
        F = set(q for q in Q if q.intersection(self.F))
        dfa2 = dfa.dfa(Q, self.A, Q_0, F, name=self.name + ".to_dfa")
        for q in Q:
            for a in self.A:
                dfa2.delta[(q, a)] = frozenset(self.extended_delta(q, a))
                assert dfa2.delta[(q, a)] in Q, f'dfa2.delta[{q}, {a}] = {dfa2.delta[(q, a)]} not in Q = {Q}'
        return dfa2

    def load_from_dfa(self, M: dfa.dfa):
        super().__init__(M.Q, M.A, M.F, name=M.name + '.nfa')
        self.Q_0 = self._format(set([M.Q_0]))
        for (q, a), q2 in M.delta.items():
            self.delta[(q, a)] = set([q2])

    def accepts(self, word: str):
        return self.extended_delta(self.Q_0, word) & self.F != set()
    
if __name__ == '__main__':
    Q = ['q0', 'q1', 'q2']
    A = ['0', '1']
    Q_0 = ['q0']
    F = ['q2']
    M = nfa(Q, A, Q_0, F, name='nfa_test')
    M.add_edge('q0', 'q1', '0')    
    M.add_edge('q0', 'q2', '0')
    M.add_edge('q0', 'q2', '1')
    M.add_edge('q1', 'q1', '0')
    M.add_edge('q2', 'q2', '0')
    M.draw()
    M_dfa = M.to_dfa()
    M_dfa.draw()

    # print the transition table
    print('Transition table:')
    for (q, a), q_ in M.delta.items():
        print(f'({q}, {a}) -> {q_}')
    
    # print some runs with their words
    print('Some runs:')
    for word in ['010', '011', '101', '111', '000', '001']:
        print(f'{word}: {M.run(word)}')

class eps_nfa(nfa):
    eps = 'ϵ'
    def __init__(self, Q: set | list | int, A: set | list | int, Q_0: set | list | str, F: set | list | str, name: str | None = None) -> None:
        super().__init__(Q, A, Q_0, F, name)
        self.A.add(self.eps)

    def eps_closure(self, X: set):
        if not hasattr(self, 'closure'): 
            self.set_eps_closure()
        if isinstance(X, set):
            return set.union(*[self.closure[q] for q in X])
        assert X in self.Q, f'X = {X} not in Q = {self.Q}'
        return self.closure[X]
    
    def set_eps_closure(self):
        if hasattr(self, 'closure'): return
        closures = {}
        def recurse(q):
            if q in closures: return closures[q]
            closure = set([q])
            if (q, self.eps) in self.delta:
                for q_ in self.delta[(q, self.eps)]:
                    closure = closure.union(recurse(q_))
            closures[q] = closure
            return closure
        for q in self.Q:
            recurse(q)
        self.closure = closures
        return self
    
    def extended_delta(self, X: set, word: str):
        if len(X) == 0: return X
        assert X.issubset(self.Q), f'X = {X} not a subset of Q = {self.Q}'
        self.set_eps_closure()
        X = self.eps_closure(X)

        if len(word) == 0:
            return X
        head = word[0]; tail = word[1:]
        one_step_lst = [self.eps_closure(self.delta[(q, head)]) for q in X if (q, head) in self.delta]
        one_step = self.eps_closure(set.union(*one_step_lst)) if len(one_step_lst) > 0 else set()
        return self.extended_delta(one_step, tail)
    
    def to_nfa(self):
        A = self.A - set([self.eps])
        self.set_eps_closure()
        M = nfa(self.Q, A, self.eps_closure(self.Q_0), self.F, name=self.name + '.to_nfa')
        
        for (q, a) in self.delta:
            if a == self.eps: continue
            M.delta[(q, a)] = self.eps_closure(self.extended_delta(set([q]), a))
            # these are not the only edges that will be added - or are they?
        return M
    
    def to_dfa(self):
        return self.to_nfa().to_dfa()
