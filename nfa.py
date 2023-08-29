# Om Sri Sai Ram

import graphviz as gv
from automaton import automaton
import dfa

class nfa(automaton):
    def __init__(self, Q: set|list|int, A: set|list|int, Q_0: set|list|str, F: set|list|str, name:str=None) -> None:
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
        print("yee", head, tail)
        if tail == "":
            subsets = [self.delta[(q, head)] for q in X if (q, head) in self.delta]
            print(subsets)
            if len(subsets) == 0: return set()
            return set.union(*subsets)
        return self.extended_delta(self.extended_delta(X, head), tail)
        # return set.union(*[self.extended_delta(q_, tail) for q_ in self.delta[(q, head)]])
        
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

    # no deterministic path. Random run is not very useful? - use backtracking instead to check whether accepted or not
    # def run_from(self, q, word: str):
    #     assert q in self.Q, f'q = {q} not in Q = {self.Q}'
    #     path = f'{q}'
    #     if len(word) == 0:
    #         return path, (q in self.F)
    #     # recurse. We will recurse on single head and tail
                  
    # def run(self, word: str):
    #     q = self.Q_0
    #     for a in word:
    #         q = self.delta[(q[0], a)]
    #         if q is None: return False
    #     return any([q_ in self.F for q_ in q])
    def load_from_dfa(self, M: dfa.dfa):
        super().__init__(M.Q, M.A, M.F, name=M.name + '.nfa')
        self.Q_0 = self._format(set([M.Q_0]))
        for (q, a), q2 in M.delta.items():
            self.delta[(q, a)] = set([q2])
    
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
    # a much more complicated example
    # Q = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5']
    # A = ['0', '1']
    # Q_0 = ['q0']
    # F = ['q5']
    # M = automaton(Q, A, Q_0, F, name='M')
    # M.add_edge('q0', 'q1', '0')
    # M.add_edge('q0', 'q2', '1')
    # M.add_edge('q1', 'q3', '0')
    # M.add_edge('q1', 'q2', '1')
    # M.add_edge('q2', 'q1', '0')
    # M.add_edge('q2', 'q4', '1')
    # M.add_edge('q3', 'q5', '0')
    # M.add_edge('q3', 'q2', '1')
    # M.add_edge('q4', 'q1', '0')
    # M.add_edge('q4', 'q4', '1')
    # M.add_edge('q5', 'q5', '0')
    # M.add_edge('q5', 'q5', '1')
    # M.draw()

    # print the transition table
    print('Transition table:')
    for (q, a), q_ in M.delta.items():
        print(f'({q}, {a}) -> {q_}')
    
    # print some runs with their words
    print('Some runs:')
    for word in ['010', '011', '101', '111', '000', '001']:
        print(f'{word}: {M.run(word)}')