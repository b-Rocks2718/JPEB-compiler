unsigned collatz(unsigned x){
  if (x & 1){
    // if x is odd, return 3 * x + 1
    return x + x + x + 1;
  } else {
    // if x is even, return x/2
    return x >> 1;
  }
}

int main(void) {

  unsigned x = 121;
  unsigned max = x;
  unsigned i = 0;

  while (x != 1){
    x = collatz(x);
    if (x > max) max = x;
    ++i;
  }
  return max;
}