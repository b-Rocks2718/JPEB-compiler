	movi r3 main
	jalr r0  r3 

# Data Section:

# Code Section:
main:
	movi r1 40959
	movi r2 40959
	addi r1  r1  -5
	movi r3 10
	sw r3  r2  -1
	movi r3 0
	sw r3  r2  -2
main.for.0.start:
	movi r3 1
	sw r3  r2  -3
	lw r3  r2  -2
	movi r4 10
	cmp r3  r4 
	bl 1
	jmp 3
	movi r3 main.end.2
	jalr r0  r3 
	movi r3 0
	sw r3  r2  -3
main.end.2:
	lw r3  r2  -3
	movi r4 0
	cmp r3  r4 
	bz 1
	jmp 3
	movi r3 main.for.0.break
	jalr r0  r3 
	movi r3 2
	lw r4  r2  -2
	call smul
	sw r3  r2  -4
	lw r3  r2  -4
	sw r3  r2  -5
	lw r3  r2  -1
	lw r4  r2  -5
	add r3  r3  r4 
	sw r3  r2  -1
main.for.0.continue:
	lw r3  r2  -2
	movi r4 1
	add r3  r3  r4 
	sw r3  r2  -2
	movi r3 main.for.0.start
	jalr r0  r3 
main.for.0.break:
	lw r3  r2  -1
	# Function Epilogue
	sys EXIT
	movi r3 0
	# Function Epilogue
	sys EXIT
