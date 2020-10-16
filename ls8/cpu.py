"""CPU functionality."""

import sys

# LDI: load "immediate", store a value in a register, or "set this register to this value".
LDI = 0b10000010
# PRN: a pseudo-instruction that prints the numeric value stored in a register.
PRN = 0b01000111
HLT = 0b00000001  # HLT: halt the CPU and exit the emulator.

# day 2
MUL = 0b10100010
ADD = 0b10100000


# sprint
JEQ = 0b01010101
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110

# stack pointer
SP = 7


class CPU:
    """Main CPU class."""
# day 1 Implement the CPU constructor , Add RAM functions ram_read() and ram_write()

    def __init__(self):
        # total CPU memory
        self.ram = [0] * 256
        # lambda CPU to print 8
        self.reg = [0] * 8  # r0 - r7
        # Program Counter, address of the currently executing instruction
        self.pc = 0
        # stack pointer SP as a registar
        self.reg[SP] = 0xf4
        # this stopped the infinite loop
        self.stop = False
        # flag pointer fl
        self.fl = 0
        # flag for if the program increments pc manually || not
        self.should_advance = False

        # branch table
        self.branch_table = {
            ADD: self.op_add,
            MUL: self.op_mul,
            LDI: self.op_ldi,
            HLT: self.op_hlt,
            PRN: self.op_prn,
            JEQ: self.op_jeq,
            JMP: self.op_jmp,
            JNE: self.op_jne,
            CMP: self.op_cmp,
        }

    # day 1 should accept the address to read and return the value stored there. The MAR contains the address that is being read or written to. MAR = address = location
    def ram_read(self, mar):
        return self.ram[mar]

    # day 1 should accept a value to write, and the address to write it to. The MDR contains the data that was read or the data to write. MDR = value
    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    # Later on, you might do further initialization here, e.g. setting the initial value of the stack pointer.

# day 2 Implement the load() function to load an .ls8 file given the filename passed in as an argument
    def load(self, file):
        """Load a program into memory."""

        try:
            with open(file) as f:

                address = 0
                for line in f:
                    # split the lines with comments
                    comments = line.strip().split('#')
                # take the first element of the line
                    strings = comments[0].strip()
                # skip empty lines
                    if strings == "":
                        continue
                # convert the line to an int
                    int_value = int(strings, 2)
                # save to memory
                    self.ram[address] = int_value
                # increment the address counter
                    address += 1
                # then close the file
                f.close()

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {file} not found")
            sys.exit(2)

# day 3 math and comparison

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            # if a < b, set L flag to 1
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            # if a > b, set G flag to 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            # if equal set E flag
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

# day 1  Implement the core of run() # day 2 Implement a Multiply instruction (run mult.ls8)
    def run(self):
        # It needs to read the memory address that's stored in register PC, and store that result in IR, the Instruction Register. This can just be a local variable in run()
        while not self.stop:
            ir = self.ram[self.pc]
        # Sometimes the byte value is a register number, other times it's a constant value (in the case of LDI). Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b in case the instruction needs them.
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # getting the initial increment size from the end of the instructions
            increment = (ir >> 6) + 1
            # check if instruction sets pc manually
            self.should_advance = ((ir >> 4) & 0b1) == 1

            if ir in self.branch_table:
                self.branch_table[ir](operand_a, operand_b)

            if not self.should_advance:
                self.pc += increment

    def op_prn(self, operand_a, operand_b):
        print(self.reg[operand_a])

    # Set the value of a register to an integer.
    def op_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def op_add(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)

    def op_mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)

    # Jump to the address stored in the given register. Set the PC to the address stored in the given register.
    def op_jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]

    # If equal flag is set (true), jump to the address stored in the given register.
    def op_jeq(self, operand_a, operand_b):
        if self.fl == 1:
            self.pc = self.reg[operand_a]
        else:
            self.should_advance = False

    # If E flag is clear (false, 0), jump to the address stored in the given register.
    def op_jne(self, operand_a, operand_b):
        if not self.fl == 1:
            self.pc = self.reg[operand_a]
        else:
            self.should_advance = False
    # Compare the values in two registers. call logic from ALU

    def op_cmp(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)

    def op_hlt(self, operand_a, operand_b):
        self.stop = True