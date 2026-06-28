






#include <stdint.h>

/*
uint64_t means unsigned 64-bit integer.
We use it because the total can become large.

Python will call this function once.
Then C does all the looping internally.

u      = unsigned Unsigned integers cannot be negative.
int    = integer
64     = 64 bits
_t     = type
0 to 18,446,744,073,709,551,615

max is 2^64 - 1

#include <stdint.h> gave us 
int8_t
uint8_t
int16_t
uint16_t
int32_t
uint32_t
int64_t
uint64_t


*/
uint64_t sum_squares_c(uint64_t n){

    uint64_t total = 0;

    for(uint64_t i = 0; i < n; i++){
        total += i*i;
    }
    return total;

}

uint64_t square_once_c(uint64_t x) {
    return x * x;
}
