from typing import Any

class CFG:
    def __init__(self, N: set|list|int, A: set|list|int, S: Any) -> None:
        self.N = self._format(N)
        self.A = self._format(A)
        self.S = S
        assert self.S in self.N, f'S = {self.S} not in N = {self.N}'
        self.P: dict[str, set] = {}

    def _format(self, obj: list|str):
        if isinstance(obj, set):
            return obj
        if isinstance(obj, list):
            return set(obj)
        if isinstance(obj, int):
            return set(range(obj))
        assert False, f'obj = {obj} is not a set, list or int'
    
    def add_production(self, lhs: str, rhs: str):
        if lhs not in self.P:
            self.P[lhs] = set()
        self.P[lhs].add(rhs)
    
    def remove_production(self, lhs, rhs):
        if lhs not in self.P: return
        self.P[lhs].discard(rhs)

    def __repr__(self):
        res = ''
        for lhs, rhs in self.P.items():
            if rhs == set():
                res += str(lhs) + ' -> ø\n'
            else:
                res += str(lhs) + ' -> ' + ' | '.join(rhs) + '\n'
        return res[:-1]
    
    def cyk(self, x: str):
        table = [[set() for _ in range(len(x)+1)] for __ in range(len(x))]
        # S E table[i][j] iff S -> x[i:j] is valid
        # suppose the grammar is Chomsky. Then we have: S E table[i][j] iff there exists k, A, B: S = AB, A -> i,k and B -> k,j; or j == i+1 and S -> x[i]
        for S, prods in self.P.items():
            for prod in prods:
                if len(prod) > 1: continue
                for i, c in enumerate(x):
                    if prod == c: 
                        table[i][i+1].add(S)
        for i in range(len(x)):
            for j in range(i, len(x)+1):
                for S, prods in self.P.items():
                    for prod in prods:
                        if len(prod) == 1: continue
                        A = prod[0]
                        B = prod[1]
                        for k in range(i, j):
                            if table[i][k]:
        
if __name__ == '__main__':
    cfg = CFG({'S', 'A', 'B'}, {'a', 'b'}, 'S')
    cfg.add_production('S', 'aSb')
    cfg.add_production('S', 'a')
    print(cfg)
    print(cfg.check('aab'))

# def check_(self, word: str):
#         # we will keep trying to replace non-terminals with their productions
#         if word == self.word:
#             self.done = True
#             return word
#         for lhs, rhs in self.P.items():
#             if lhs not in word: continue
#             for prod in rhs:
#                 # print("prod", prod)
#                 if prod == 'ϵ':
#                     word_new = word.replace(lhs, '', 1) # need to take care of count occurring anywhere!
#                     print(word_new)
#                     word_new = f'{lhs} -> {rhs}\n{word} -> {word_new}\n' + self.check(word_new)
#                     if self.done: return word_new
#                 else:
#                     word_new = word.replace(lhs, prod, 1)
#                     print(word_new)
#                     word_new = f'{lhs} -> {rhs}\n{word} -> {word_new}\n' + self.check(word_new)
#                     if self.done: return word_new
#         return ''
    
#     def check(self, word: str):
#         self.word = word
#         self.done = False
#         return self.check_(str(self.S))