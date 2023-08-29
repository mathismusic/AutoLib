import graphviz as gv
from automaton import automaton
from typing import Any

class dfa(automaton):
    def __init__(self, Q: set|list|int, A: set|list|int, Q_0: Any, F: set|list|str, name:str=None) -> None:
        super().__init__(Q, A, F, name)
        # self.Q_0 = self.Q[Q_0] if isinstance(Q_0, int) else Q_0
        self.Q_0 = Q_0
        assert self.Q_0 in self.Q, f'Q_0 = {self.Q_0} not in Q = {self.Q}'

    def add_vertex(self, name=None, final=False):
        self.Q.add(name) 
        if final: self.F.add(name)
    
    def add_edge(self, q1, q2, a):
        assert q1 in self.Q, f'q1 = {q1} not in Q = {self.Q}'
        assert q2 in self.Q, f'q2 = {q2} not in Q = {self.Q}'
        assert a in self.A, f'a = {a} not in A = {self.A}'
        self.delta[(q1, a)] = q2
    
    def remove_vertex(self, q):
        if q not in self.Q: return
        assert q != self.Q_0, f'q = {q} is the start state, cannot remove it'
        self.Q.remove(q)
        self.F.discard(q)
        for a in self.A:
            self.delta.pop((q, a), None)
        for (q1, a), q2 in self.delta.copy().items():
            if q2 == q:
                self.delta.pop((q1, a))
        
    def remove_edge(self, q, a):
        assert q in self.Q, f'q = {q} not in Q = {self.Q}'
        assert a in self.A, f'a = {a} not in A = {self.A}'
        self.delta.pop((q, a))

    def draw(self, savefig=False, directory=None, filename=None):
        def _format(q):
            if isinstance(q, frozenset):
                return str(set(q)) if q != frozenset() else 'ø'
            return str(q)
        fig = gv.Digraph(self.name, format='png')
        status = {q: False for q in self.Q}
        q = self.Q_0
        fig.node(_format(q), shape='circle', color='red')
        status[q] = True
        for q in self.F:
            if status[q]:
                fig.node(_format(q), shape='doublecircle', color='red')
            else:
                fig.node(_format(q), shape='doublecircle')
            status[q] = True
        for q in self.Q:
            if status[q]: continue
            fig.node(_format(q), shape='circle')

        # edges
        for (q1, a), q2 in self.delta.items():
            if q2 is None: continue
            fig.edge(_format(q1), _format(q2), label=a)
        fig.graph_attr['rankdir'] = 'LR'
        fig.graph_attr['size'] = '10'
        if savefig:
            fig.render(filename if filename else self.name, directory=directory, view=False)
        return fig
    
    def run(self, word: str):
        q = self.Q_0
        path = f'{q}'
        for a in word:
            if (q, a) not in self.delta: return path, False
            q = self.delta[(q, a)]
            path += f' -> {q}'
        return path, (q in self.F)
    
    def extended_delta(self, X: set, word: str):
        # convention
        if len(X) == 0: return X
        
        # basecase
        if len(word) == 0: return X
        
        # inductive step
        X1 = set(self.delta[(q, word[0])] for q in X if (q, word[0]) in self.delta)
        return self.extended_delta(X1, word[1:])
    
    def accepts(self, word: str):
        return self.extended_delta({self.Q_0}, word) & self.F != set()
    
    def union(self, other: 'dfa'):
        return self.join(other, lambda x, y: x or y)
    
    def intersect(self, other: 'dfa'):
        return self.join(other, lambda x, y: x and y)
    
    def join(self, other: 'dfa', accept_cn: Any):
        """compute the cross product of two DFAs, and accept_cn is a function (q in F, q' in F) -> bool that tells whether the pair (q, q') is accepted (True) or not (False)"""
        assert self.A == other.A, f'A = {self.A} != A = {other.A}'
        
        Q = set()
        for q1 in self.Q:
            for q2 in other.Q:
                Q.add(frozenset([q1, q2]))
        Q_0 = frozenset([self.Q_0, other.Q_0])
        F = set()
        for q1 in self.Q:
            for q2 in other.Q:
                if accept_cn(q1 in self.F, q2 in other.F):
                    F.add(frozenset([q1, q2]))

        M = dfa(Q, self.A, self.Q_0, self.F, name=f'{self.name} union {other.name}')
        for a in self.A:
            for q1 in self.Q:
                for q2 in other.Q:
                    if (q1, a) in self.delta and (q2, a) in other.delta:
                        M.add_edge(frozenset([q1, q2]), frozenset([self.delta[(q1, a)], other.delta[(q2, a)]]), a)
        return M
    
    def complement(self):
        return dfa(self.Q, self.A, self.Q_0, self.Q.difference(self.F), name=f'{self.name}.complement')
    
    def remove_unreachable_states(self):
        visited = set([self.Q_0])
        def dfs_recursive(q):
            for a in self.A:
                if (q, a) not in self.delta: continue
                q_ = self.delta[(q, a)]
                if q_ not in visited:
                    visited.add(q_)
                    dfs_recursive(q_)
        dfs_recursive(self.Q_0)
        unreachable = self.Q.difference(visited)
        for q in unreachable:
            self.remove_vertex(q)
        return self
    
    def get_equivalence_classes(self):
        # Hopcroft'71
        Q_lst = list(self.Q)
        # initially, all unmarked
        table = {(Q_lst[i],Q_lst[j]):True for i in range(len(Q_lst)-1) for j in range(i+1, len(Q_lst))}
        # print(table)
        # print(Q_lst)
        # mark all states, one in F one not in F:
        modified = False
        for (q1, q2) in table:
            if (q1 in self.F) != (q2 in self.F):
                table[(q1, q2)] = False
                modified = True

        while modified:
            modified = False
            for (q1, q2) in table:
                if not table[(q1, q2)]: continue
                for a in self.A:
                    if (q1, a) not in self.delta or (q2, a) not in self.delta: continue
                    q1_ = self.delta[(q1, a)]
                    q2_ = self.delta[(q2, a)]
                    if q1_ == q2_: continue
                    if (q1_, q2_) in table and table[(q1_, q2_)]: continue
                    if (q2_, q1_) in table and table[(q2_, q1_)]: continue
                    else:
                        table[(q1, q2)] = False
                        modified = True
                        break # don't need to check other a's
        # print(table)
        # now to make the classes
        classes: list[list] = []
        for q in self.Q:
            for cls in classes:
                elem = next(cls)
                if (q, elem) in table and table[(q, elem)]: 
                    cls.append(q)
                    break
                elif (elem, q) in table and table[(elem, q)]:
                    cls.append(q)
                    break
            else:
                classes.append([q])
        return classes
                    

if __name__ == '__main__':
    Q = ['q0', 'q1', 'q2']
    A = ['0', '1']
    Q_0 = 'q0'
    F = ['q2']
    M = dfa(Q, A, Q_0, F, name='M')
    M.add_edge('q0', 'q1', '0')
    M.add_edge('q0', 'q2', '1')
    M.add_edge('q1', 'q1', '0')
    M.add_edge('q1', 'q2', '1')
    M.add_edge('q2', 'q2', '0')
    M.add_edge('q2', 'q2', '1')
    M.draw()

    # # a much more complicated example
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
        print(f'{word}: {"accepted" if M.accepts(word) else "rejected"}')