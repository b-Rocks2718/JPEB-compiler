import sys
import os

compiler_flags = [
    "-tokens",
    "-ast",
    "-semantics",
    "-tac",
    "-asm"
]

other_flags = [
    "-out"
]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: bcc <file.c> <flags>")
        sys.exit(1)

    args = sys.argv[2:]

    cfile = sys.argv[1]
    name = cfile.split('.')[0]
    asmfile = name + ".s"
    outfile = name + ".out"
    binfile = name + ".bin"

    compiler_args = []
    for arg in args:
        # separate flags
        if arg in compiler_flags:
            compiler_args.append(arg)
        elif arg in other_flags:
            pass
        else:
            print("Unrecognized flag: " + arg)
            print("Valid flags are:")
            for flag in compiler_flags:
                print(flag)
            print("-out")
            sys.exit(1)

    # run the compiler and assembler, exit if either fails
    if os.system("cabal run exes -- " + cfile + ' ' + ' '.join(compiler_args)):
        sys.exit(1)
    if not os.path.exists(asmfile):
        sys.exit(1)
    if os.system("python3 Assembler.py " + asmfile + 
          ' asm_libraries/arithmetic.s ' + 
          ' '.join(assembler_args)):
        sys.exit(1)
    if not os.path.exists(binfile):
        sys.exit(1)
    
    result = 0

    if "-out" not in args:
        # remove .out files
        os.system("rm " + outfile)
        if "-emu" not in args:
            os.system("rm asm_libraries/os.out")
    
    sys.exit(result)
