from methods import *

# Task B.1 Test cases
f1 = [[1, 2], [-1, 3], [-2, 3], [-3, 4], [-3, -4]]
res = cdcl(f1)
print(res)

f2 = [[1, 2], [-1, 3], [-2, 4], [-3, -4], [-3, 5], [-4, -5]]
res = cdcl(f2)
print(res)

php_3_4_dimacs = '''
p cnf 12 22
1 2 3 0
4 5 6 0
7 8 9 0
10 11 12 0
-1 -4 0
-1 -7 0
-1 -10 0
-4 -7 0
-4 -10 0
-7 -10 0
-2 -5 0
-2 -8 0
-2 -11 0
-5 -8 0
-5 -11 0
-8 -11 0
-3 -6 0
-3 -9 0
-3 -12 0
-6 -9 0
-6 -12 0
-9 -12 0
'''
res = cdcl(parse_dimacs(php_3_4_dimacs))
print(res)