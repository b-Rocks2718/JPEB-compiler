# BCC compiler

My implementation of of the compiler described in [Writing a C Compiler](https://nostarch.com/writing-c-compiler) by Nora Sandler.  
Targets the JPEB architecture.  
Basically a clone of [My C Compiler](https://github.com/b-Rocks2718/c-compiler). For this project, the compiler was extended to support arrays.

## Building

1. [Install ghcup](https://www.haskell.org/ghcup/install/)
2. `ghcup install ghc 9.4.8`
3. `ghcup set ghc 9.4.8`
4. `cabal build`

## Usage

Compiler flags: `tokens`, `ast`, `semantics`, `tac`, or `asm`. 
You can specify as many of these flags as you want, and the compiler will print
the output of the corresponding stage. 


Other flags: 
- `-out` if you want to keep the generated `.out` file

## Issues 
 - Dereferencing global variables does not work correctly. In order to dereference global variable, create a temp local variable.  
 - Functions that consume too much stack space will not compile. For now, just split things into smaller functions.

Older features, like control flow, are pretty thouroughly tested. Newer features, like pointer and arrays, are still kind of buggy.  
The compiler does zero optimizations and the assembly it generates kinda sucks. Eventually I plan to use the TAC IR to build a 
control flow graph to do optimizations, and I'll write a register allocator.

