# BCC compiler

My implementation of of the compiler described in [Writing a C Compiler](https://nostarch.com/writing-c-compiler) by Nora Sandler.  
Targets the JPEB architecture.  
Basically a clone of [My C Compiler](https://github.com/b-Rocks2718/c-compiler). For this project, the compiler was extended to support arrays.  
One difference is that this compiler initializes `sp` and `bp` to 0x9FFF instead of 0xFFFF so we don't use the framebuffer for stack space.  

## Building

1. [Install ghcup](https://www.haskell.org/ghcup/install/)
2. `ghcup install ghc 9.4.8`
3. `ghcup set ghc 9.4.8`
4. `cabal build`

## Usage

Compiler flags: `tokens`, `ast`, `semantics`, `tac`, or `asm`. 
You can specify as many of these flags as you want, and the compiler will print
the output of the corresponding stage. 

## Issues 
 - Dereferencing global variables does not work correctly. In order to dereference global variable, create a temp local variable.  
 - Functions that consume too much stack space will not compile. For now, just split things into smaller functions.
 - `void` hasn't been implemented yet. For functions that don't return anything, just declare an `int` return type.
 - Declaring global variables `static` doesn't actually do anything, so be careful with name collisions. Similarly, the assembler treats all labels as global.
 - Error reporting for the parser sucks. If you make a syntax error, it will not tell you where. Sorry.

Older features, like control flow, are pretty thoroughly tested. Newer features, like pointer and arrays, are still kind of buggy.  
The compiler does zero optimizations and the assembly it generates kinda sucks. Eventually I plan to use the TAC IR to build a 
control flow graph to do optimizations, and I'll write a register allocator.

## Testing
[Test script](https://github.com/b-Rocks2718/c-compiler/tree/master/test) that compares the compiler + emulator against gcc. still many failing tests to work out

