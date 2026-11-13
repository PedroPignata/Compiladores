    primeiro = 18
    segundo = 6
    operacao = 1
    resultado = 0
    valido = eh_memo
    t1 = operacao == 1
    ifFalse t1 goto L1
    t2 = primeiro + segundo
    resultado = t2
    goto L2
L1:
    t3 = operacao == 2
    ifFalse t3 goto L3
    t4 = primeiro - segundo
    resultado = t4
    goto L4
L3:
    t5 = operacao == 3
    ifFalse t5 goto L5
    t6 = primeiro * segundo
    resultado = t6
    goto L6
L5:
    t7 = operacao == 4
    ifFalse t7 goto L7
    t8 = segundo != 0
    ifFalse t8 goto L9
    t9 = primeiro / segundo
    resultado = t9
    goto L10
L9:
    valido = num_eh
L10:
    goto L8
L7:
    valido = num_eh
L8:
L6:
L4:
L2:
    print valido
    ifFalse valido goto L11
    print resultado
    goto L12
L11:
L12:
