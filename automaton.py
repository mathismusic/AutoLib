# Om Sri Sai Ram

class automaton:
    def __init__(self, Q: set|list|int, A: set|list|int, F: set|list|str, name:str|None=None) -> None:
        self.Q: set = self._format(Q)
        self.A: set = self._format(A)
        self.F: set = self._format(F)
        assert self.F.issubset(self.Q), f'F = {self.F} not a subset of Q = {self.Q}'
        self.name = name if name else 'automaton'
        self.delta = {}

    def _format(self, obj: list|str):
        if isinstance(obj, set):
            return obj
        if isinstance(obj, list):
            return set(obj)
        if isinstance(obj, int):
            return set(range(obj))
        assert isinstance(obj, str)
        return set(q for q, bit in zip(self.Q, obj) if bit == '1')
    
    def size(self):
        return len(self.Q)
    
    def add_edge(self, q1, q2, a):
        pass

    def add_transition(self, q1, a, q2):
        return self.add_edge(q1, q2, a)
    
    def remove_edge(self, q1, q2, a):
        pass
    
    def draw(self, directory=None, filename=None):
        pass

    def clear_edges(self):
        self.delta = {}
        return self
    
    def run(self, word: str):
        pass

if __name__ == '__main__':
    Q = ['q0', 'q1', 'q2']
    A = ['0', '1']
    Q_0 = ['q0']
    F = ['q2']
    M = automaton(Q, A, F, name='M')
    M.add_edge('q0', 'q1', '0')
    M.add_edge('q0', 'q2', '1')
    M.add_edge('q1', 'q1', '0')
    M.add_edge('q1', 'q2', '1')
    M.add_edge('q2', 'q2', '0')
    M.add_edge('q2', 'q2', '1')
    # M.draw()

    # a much more complicated example
    Q = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5']
    A = ['0', '1']
    Q_0 = ['q0']
    F = ['q5']
    M = automaton(Q, A, F, name='M')
    M.add_edge('q0', 'q1', '0')
    M.add_edge('q0', 'q2', '1')
    M.add_edge('q1', 'q3', '0')
    M.add_edge('q1', 'q2', '1')
    M.add_edge('q2', 'q1', '0')
    M.add_edge('q2', 'q4', '1')
    M.add_edge('q3', 'q5', '0')
    M.add_edge('q3', 'q2', '1')
    M.add_edge('q4', 'q1', '0')
    M.add_edge('q4', 'q4', '1')
    M.add_edge('q5', 'q5', '0')
    M.add_edge('q5', 'q5', '1')
    M.draw()

    # print the transition table
    print('Transition table:')
    for (q, a), q_ in M.delta.items():
        print(f'({q}, {a}) -> {q_}')
    
    # print some runs with their words
    print('Some runs:')
    for word in ['010', '011', '101', '111', '000', '001']:
        print(f'{word}: {M.run(word)}')