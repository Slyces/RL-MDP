open(save_path).write(str(n) + ',' + str(m) + '\n' + ''.join([c.value for c in __grid]))

lines = open(save_path).readlines()
n, m = [int(x) for x in lines[0].split(',')]
__grid = [Cell(c) for c in lines[1]]
