a = [(1,30), (2,3), (3,4), (4,2), (5,10), (6,3), (7,3), (8,9), (9, 3), (10,2), (11,3), (12,4)]
with open('input', 'w') as f:
    f.write('\t'.join(['NN']*4)+'\n')
    for x in a:
        for idx in range(x[1]):
            f.write('\t'.join(['S'+str(x[0])+'_'+str(idx), 'NN', str(x[0]), str(x[1])])+'\n')
