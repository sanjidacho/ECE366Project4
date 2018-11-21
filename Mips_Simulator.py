def Simulation(Instructions):

    Register = [0 for i in xrange(8)]
    Memory = [0 for i in xrange(4096)]
    PC = 0
    DIC = 0

    for instructionFetch in Instructions:
        DIC += 1

        if instructionFetch == '00010000000000001111111111111111':
            break
        
        elif instructionFetch[:6] ==  '000000' and instructionFetch[26:] == '100000':
            Register[int(instructionFetch[16:21],2)] = Register[int(instructionFetch[6:11],2)] + Register[int(instructionFetch[11:16],2)]

        elif instructionFetch[:6] == '001000':
            imm = 0
            if instructionFetch[16] == '0':
                imm = int(instructionFetch[16:],2)
            else:
                imm = -32768+int(instructionFetch[17:],2)
            Register[int(instructionFetch[11:16],2)] = Register[int(instructionFetch[6:11],2)] + imm

        elif instructionFetch[:6] == '000100':
            imm = 0
            if instructionFetch[16] == '0':
                imm = int(instructionFetch[16:],2)
            else:
                imm = -32768+int(instructionFetch[17:],2)

            if (Register[int(instructionFetch[6:11],2)] == Register[int(instructionFetch[11:16],2)]):
                PC += imm

        elif instructionFetch[:6] == '000000' and instructionFetch[26:] == '101010' :

            if Register[int(instructionFetch[6:11],2)] < Register[int(instructionFetch[11:16],2)]:
                Register[int(instructionFetch[16:21],2)] = 1
            else:
                Register[int(instructionFetch[16:21],2)] = 0

        elif instructionFetch[:6] == '101011':
            if  int(instructionFetch[30:])%4 != 0:
                print 'Runtime exception: fetch address not aligned on word boundary. Exiting'
                print 'Instruction causing error:', hex(int(instructionFetch,2))
                exit()
            imm = int(instructionFetch[16:],2)
            Memory[imm + Register[int(instructionFetch[6:11],2)]-8192]= Register[int(instructionFetch[11:16],2)]

        elif instructionFetch[0:6] == '100011': 
            if int(instructionFetch[30:])%4 != 0 :
                print 'Runtime exception: fetch address not aligned on word boundary. Exiting'
                print 'Instruction causing error:', hex(int(fetch,2))
                exit()
            imm = int(instructionFetch[16:],2)
            Register[int(instructionFetch[11:16],2)] = Memory[imm + Register[int(instructionFetch[6:11],2)]-8192]
        PC += 1

    print 'Finished simulation'
    print 'Program Counter PC: ', PC
    print 'Dynamic instructions count DIC: ' ,DIC
    print 'Registers: ' , Register

def main():
    Instructions = []
    with open('i_mem.txt','r') as file:
        for line in file:
            Instructions.append(format(int(line.replace('\n',''), 16),'032b'))

    Simulation(Instructions)

if __name__ == "__main__":
    main()