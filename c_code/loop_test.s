	movi r3 main
	jalr r0  r3 

# Data Section:

# Code Section:
main:
	movi r1 40959
	movi r2 40959
	addi r1  r1  -2
	movi r3 10
	sw r3  r2  -1
	movi r3 1
	sw r3  r2  -2
	lw r3  r2  -1
	movi r4 15
	cmp r3  r4 
	bg 1
	jmp 3
	movi r3 main.end.1
	jalr r0  r3 
	movi r3 0
	sw r3  r2  -2
main.end.1:
	lw r3  r2  -2
	movi r4 0
	cmp r3  r4 
	bz 1
	jmp 3
	movi r3 main.else.2
	jalr r0  r3 
	movi r3 25
	# Function Epilogue
	sys EXIT
	movi r3 main.end.3
	jalr r0  r3 
main.else.2:
	movi r3 35
	# Function Epilogue
	sys EXIT
main.end.3:
	movi r3 0
	# Function Epilogue
	sys EXIT
