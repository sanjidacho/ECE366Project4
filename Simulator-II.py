def Simulation(instructionList, associativity=0, blockSize=0, sets=0):
    
    # PC, DIC variables
    PC = 0
    DIC = 0

    # Cycles Count for Multi-Cycle MIPS CPU
    totalCycles = 0
    threeCyclesInstructions = 0
    fourCyclesInstructions = 0
    fiveCyclesInstructions = 0

    # Cycle and Stall count for Pipeline MIPS CPU
    # initialized with 4 because 4 cyles are mandatory to fill the pipeline, after that one instruction completes in one cycle without stalls
    totalPipelinedCycles = 4
    stalls = 0

    # total registers $0-$7
    registers=[0 for i in xrange(8)]

    # instruction Memory is in range 0x0000 to 0x1000, total 0x1000 = 4096 in decimal
    # we divide 4096 by 4 because memory is byte addressable and we are storing 4 byte instruction in one location
    instructionMemory = [0 for i in xrange(4096/4)]

    # since dataMemory is in range 0x2000 to 0x3000, total 0x1000 = 4096 in decimal 
    dataMemory = [0 for i in xrange(4096/4)]

    # Caches
    DMCache1 = [[0,0] for j in xrange(2)]
    DMCache1Hits = 0

    DMCache2 = [[0,0] for j in xrange(4)]
    DMCache2Hits = 0

    FACache = [[0,0,0] for j in xrange(4)]
    FACacheHits = 0

    TWSACache = [[[0,0,0] for j in xrange(2)] for k in xrange(4)]
    TWSACacheHits = 0

    testCache = None
    testCacheHits = 0

    totalCachesAccess = 0

    if associativity != 0 and blockSize != 0 and sets != 0:
        testCache = [[[0,0,0] for j in xrange(associativity)] for k in xrange(sets)]

    #Load instructions in instruction memory
    for idx in xrange(len(instructionList)):
        instructionMemory[idx] = int(instructionList[idx], 16)

    # Starting Simulation
    print 'Starting Simulation'

    # fetch instruction from instructionMemory

    while PC < len(instructionMemory):
        DIC += 1
        fetch = instructionMemory[PC]
        
        # if fetched instruction is dead loop (i.e. 0x1000ffff), end program execution
        if fetch == 0x1000ffff:
            print "PC:",PC,"Dead Loop, Exiting"
            
            totalCycles += 3
            threeCyclesInstructions += 1
            break

        # since we have only R and I type instructions, opcode, rs, and rt are common in both
        # extracting opcode, rs, and rt

        opcode = (fetch & 0xfc000000) >> 26 

        # rs is after opcode and 5 bits
        rs = (fetch & 0x03e00000) >> 21

        # rt is after rs and 5 bits
        rt = (fetch & 0x001f0000) >> 16

        # if opcode is zero then instructions is R-type
        if opcode == 0:
            
            # extract all remaining parameters from instruction
           
            # rd is after rt and 5 bits
            rd = (fetch & 0x0000f800) >> 11

            # since we have no shift instructions shamt is not needed
            # extract last 6 funct bits
            funct = fetch & 0x0000003f

            # Add instruction
            if funct == 32:

                print "PC:",PC,"Add","$"+str(rd)+", $"+str(rs)+", $"+str(rt) 

                totalCycles += 4
                totalPipelinedCycles += 1
                fourCyclesInstructions += 1
                if rd != 0:
                    registers[rd] = registers[rs] + registers[rt]
                    print "Register $"+str(rd),"=", registers[rd]
                else:
                    print "Zero register can't be updated"

            # Sub instruction
            elif funct == 34:

                print "PC:",PC,"Sub","$"+str(rd)+", $"+str(rs)+", $"+str(rt)

                totalCycles += 4
                totalPipelinedCycles += 1
                fourCyclesInstructions += 1
                if rd != 0:
                    registers[rd] = registers[rs] - registers[rt]
                    print "Register $"+str(rd),"=", registers[rd]
                else:
                    print "Zero register can't be updated"

            # Xor instruction
            elif funct == 38:

                print "PC:",PC,"Xor","$"+str(rd)+", $"+str(rs)+", $"+str(rt)

                totalCycles += 4
                totalPipelinedCycles += 1
                fourCyclesInstructions += 1
                if rd != 0:
                    registers[rd] = registers[rs] ^ registers[rt]
                    print "Register $"+str(rd),"=", registers[rd]
                else:
                    print "Zero register can't be updated"

            # Slt instruction
            elif funct == 42:

                print "PC:",PC,"Slt","$"+str(rd)+", $"+str(rs)+", $"+str(rt)

                totalCycles += 4
                totalPipelinedCycles += 1
                fourCyclesInstructions += 1
                if rd != 0:
                    registers[rd] = int(registers[rs] < registers[rt])
                    print "Register $"+str(rd),"=", registers[rd]
                else:
                    print "Zero register can't be updated"
            
        # opcode is not zero then I type instruction
        else:

            # extract immediate
            imm = fetch & 0x0000ffff
            if imm > 32767:
                imm = -(65535-imm+1)
            

            # Addi instruction
            if opcode == 8:

                print "PC:",PC,"Addi","$"+str(rt)+", $"+str(rs)+",",imm

                totalCycles += 4
                totalPipelinedCycles += 1
                fourCyclesInstructions += 1
                if rt != 0:
                    registers[rt] = registers[rs] + imm
                    print "Register $"+str(rt),"=", registers[rt]
                else:
                    print "Zero register can't be updated"

            
            # Beq instruction
            elif opcode == 4:

                print "PC:",PC,"Beq","$"+str(rs)+", $"+str(rt)+",",imm
                
                totalCycles += 3
                totalPipelinedCycles += 1
                threeCyclesInstructions += 1
                if registers[rs] == registers[rt]:
                    PC += imm
                    print "Branch Taken, Updated PC:",PC
                    stalls += 2
                    totalPipelinedCycles += 2

            
            # Bne instruction
            elif opcode == 5:

                print "PC:",PC,"Bne","$"+str(rs)+", $"+str(rt)+",",imm

                totalCycles += 3
                totalPipelinedCycles += 1
                threeCyclesInstructions += 1
                if registers[rs] != registers[rt]:
                    PC += imm
                    print "Branch Taken, Updated PC:",PC
                    stalls += 2
                    totalPipelinedCycles += 2

            
            # Lw instruction
            elif opcode == 35:

                print "PC:",PC,"Lw","$"+str(rt)+",",str(imm)+"($"+str(rs)+")"

                totalCycles += 5
                totalPipelinedCycles += 1
                fiveCyclesInstructions += 1
                totalCachesAccess += 1

                # since dataMemory starts from 0x2000 = 8192 in decimal, subtract from address 8192
                if rt != 0:
                    address = (registers[rs] + imm -8192)/4
                    
                    cacheIndex = (address/4)%2 
                    tag = (address/8)
                    offset = address%4
                    
                    print "\nAccessing address:",registers[rs] + imm -8192

                    print "\nFor Direct Mapped Cache with block size 4 words and total 2 blocks:"
                    print "Tag:",tag,", Cache Index:",cacheIndex,", Offset:",offset,", Valid Bit:",DMCache1[cacheIndex][0]

                    if DMCache1[cacheIndex][0] == 1 and DMCache1[cacheIndex][1] == tag:
                        print "Cache Access was a hit"
                        DMCache1Hits += 1
                    else:
                        DMCache1[cacheIndex][0] = 1
                        DMCache1[cacheIndex][1] = tag
                        print "Cache Access was a miss"

                    cacheIndex = (address/2)%4 
                    tag = (address/8)
                    offset = address%2

                    print "\nFor Direct Mapped Cache with block size 2 words and total 4 blocks:"
                    print "Tag:",tag,", Cache Index:",cacheIndex,", Offset:",offset,", Valid Bit:",DMCache2[cacheIndex][0]
                    if DMCache2[cacheIndex][0] == 1 and DMCache2[cacheIndex][1] == tag:
                        print "Cache Access was a hit"
                        DMCache2Hits += 1
                    else:
                        DMCache2[cacheIndex][0] = 1
                        DMCache2[cacheIndex][1] = tag
                        print "Cache Access was a miss"

                    tag = (address/2)
                    offset = address%2
                    
                    print "\nFor Fully Associative Cache with block size 2 words and total 4 blocks:"
                    print "Tag:",tag,"Offset:",offset
                    for i in xrange(4):

                        if FACache[i][0] == 1 and FACache[i][1] == tag:
                            print "Cache Access was a hit"
                            FACacheHits += 1
                            for j in xrange(4):
                                if i!=j and FACache[j][0] == 1 and FACache[j][2]<FACache[i][2]:
                                    FACache[j][2]+=1
                            FACache[i][2] = 1
                            break
                        if i==3:
                            print "Cache Access was a miss"
                            for j in xrange(4):
                                if FACache[j][0]==0:
                                    print "Found Empty Place at",j
                                    FACache[j][0] = 1
                                    FACache[j][1] = tag
                                    FACache[j][2] = 1
                                    for k in xrange(4):
                                        if j!=k and FACache[k][0]==1:
                                            FACache[k][2]+=1
                                    break
                                
                                if j==3:
                                    print "Cache is Full, replacing block based on LRU replacement policy"
                                    for k in xrange(4):
                                        if FACache[k][2]==4:
                                            FACache[k][0]=1
                                            FACache[k][1]=tag
                                            FACache[k][2] = 1
                                            print "Replaced block at", k
                                            for l in xrange(4):
                                                if k!=l:
                                                    FACache[l][2]+=1
                                            break
                                    

                    cacheIndex = (address/2)%4
                    offset = address%2
                    tag = address/8

                    print "\nFor 2-way set Associatove Cache with block size 2 words and total 4 sets:"
                    print "Tag:",tag,"Cache Index:",cacheIndex,"Offset:",offset
                    for i in xrange(2):
                        if TWSACache[cacheIndex][i][0]==1 and TWSACache[cacheIndex][i][1]==tag:
                            print "Cache Access was a hit\n"
                            TWSACacheHits += 1
                            for j in xrange(2):
                                if i!=j and TWSACache[cacheIndex][j][0]==1 and TWSACache[cacheIndex][j][2]<TWSACache[cacheIndex][i][2]:
                                    TWSACache[cacheIndex][j][2]+=1
                            TWSACache[cacheIndex][i][2] = 1   
                            break
                        if i==1:
                            print "Cache Access was a miss\n"
                            for j in xrange(2):
                                if TWSACache[cacheIndex][j][0]==0:
                                    print "Found empty place at",j
                                    TWSACache[cacheIndex][j][0] = 1
                                    TWSACache[cacheIndex][j][1] = tag
                                    TWSACache[cacheIndex][j][2] = 1
                                    for k in xrange(2):
                                        if j!=k and TWSACache[cacheIndex][k][0]==1:
                                            TWSACache[cacheIndex][k][2]+=1
                                    
                                    break
                                
                                if j==1:
                                    print "Set is full, replacing block based on LRU policy"
                                    for k in xrange(2):
                                        if TWSACache[cacheIndex][k][2]==2:
                                            print "Replacing block at", k
                                            TWSACache[cacheIndex][k][0]=1
                                            TWSACache[cacheIndex][k][1]=tag
                                            TWSACache[cacheIndex][k][2]=1
                                            for l in xrange(2):
                                                if k!=l:
                                                    TWSACache[cacheIndex][l][2]+=1
                                            break

                    if testCache:
                        cacheIndex = (address/blockSize)%sets
                        offset = address%blockSize
                        tag = address/(blockSize*sets)

                        print "For Cache Configured by user"
                        print "Tag:",tag,"Cache Index:",cacheIndex,"Offset:",offset
                        for i in xrange(associativity):
                            if testCache[cacheIndex][i][0]==1 and testCache[cacheIndex][i][1]==tag:
                                print "Cache Access was a hit\n"
                                testCacheHits += 1
                                for j in xrange(associativity):
                                    if i!=j and testCache[cacheIndex][j][0]==1 and testCache[cacheIndex][j][2]<testCache[cacheIndex][i][2]:
                                        testCache[cacheIndex][2]+=1
                                testCache[cacheIndex][i][2]=1
                                break
                            if i==associativity-1:
                                print "Cache Access was a miss\n"
                                for j in xrange(associativity):
                                    if testCache[cacheIndex][j][0]==0:
                                        print "Replacing block at", j
                                        testCache[cacheIndex][j][0] = 1
                                        testCache[cacheIndex][j][1] = tag
                                        testCache[cacheIndex][j][2] = 1
                                        for k in xrange(associativity):
                                            if j!=k and testCache[cacheIndex][k][0]==1:
                                                testCache[cacheIndex][k][2]+=1
                                        break
                                    
                                    if j==associativity-1:
                                        print "Set is full, replacing block based on LRU policy."
                                        for k in xrange(associativity):
                                            if testCache[cacheIndex][k][2]==associativity:
                                                print "Replacing block at", k
                                                testCache[cacheIndex][k][0] = 1
                                                testCache[cacheIndex][k][1] = tag
                                                testCache[cacheIndex][k][2] = 1
                                                for l in xrange(associativity):
                                                    if l!=k and testCache[cacheIndex][l][0]==1:
                                                        testCache[cacheIndex][l][2]+=1
                                                break
                                    
                    registers[rt] = dataMemory[address]
                    print "Register $"+str(rt),"=", registers[rt]
                    stalls += 1
                else:
                    print "Zero register can't be updated\n"

            
            # Sw instruction
            elif opcode == 43:
                print "PC:",PC,"Sw","$"+str(rt)+",",str(imm)+"($"+str(rs)+")"
                totalCycles += 4
                totalPipelinedCycles += 1
                fourCyclesInstructions += 1
                # since dataMemory starts from 0x2000 = 8192 in decimal, subtract from address 8192
                dataMemory[(registers[rs] + imm - 8192)/4] = registers[rt]
                print "Memory["+str(registers[rs] + imm - 8192)+"] =", registers[rt]

            
        PC += 1
        print "Registers:",registers
        
    print "Simulation Ended Successfully"
    
    print "PC:",PC
    print "DIC:",DIC
    print "Registers:",registers

    print "\nTotal Cycles for Multi-Cycle MIPS CPU:",totalCycles
    print "Total Cycles for Piplelined MIPS CPU:",0 if totalPipelinedCycles==4 else totalPipelinedCycles
    print "Total 3 Cycle Instructions:",threeCyclesInstructions
    print "Total 4 Cycle Instructions:",fourCyclesInstructions
    print "Total 5 Cycle Instructions:",fiveCyclesInstructions

    if totalCachesAccess == 0:
        print "No cache access"
    else:
        print "\nCache 1 hit rate:",DMCache1Hits/float(totalCachesAccess)
        print "Cache 2 hit rate:",DMCache2Hits/float(totalCachesAccess)
        print "Cache 3 hit rate:",FACacheHits/float(totalCachesAccess)
        print "Cache 4 hit rate:",TWSACacheHits/float(totalCachesAccess)
        if testCache:
            print "Cache hit rate for user configured cache:",testCacheHits/float(totalCachesAccess)

if __name__ == '__main__':
    # read instructions from i_mem.txt

    instructions = []
    fileName = raw_input("Enter file name:")
    with open(fileName,'r') as file:
        for line in file:
            instructions.append(line.replace('\n','').replace('0x',''))

    x = input("Enter \n1) If you want to input cache configuratios. \n2) Ignore\n")
    if x==1:
        associativity = input("Enter associativity (greater than one):")
        blockSize = input("Enter block size (greater than one):")
        sets = input("Enter number of sets (greater than one):")
        Simulation(instructions, associativity, blockSize, sets)
    else:
        Simulation(instructions)