#include <stdatomic.h>
#include <stdio.h>
#include <threads.h>

#include "librace.h"

atomic_int X, Y;
atomic_int r1, r2;

static void a(void *obj) {
  atomic_store_explicit(&X, 1, memory_order_release);                 // A
  printf("Y = %d\n", atomic_load_explicit(&Y, memory_order_acquire)); // B
}

static void b(void *obj) {
  atomic_store_explicit(&Y, 1, memory_order_release);                 // C
  printf("X = %d\n", atomic_load_explicit(&X, memory_order_acquire)); // D
}

int main(int argc, char **argv) {
  thrd_t t1, t2;

  for (int i = 0; i < 1'00; i++) {
    atomic_store_explicit(&X, 0, memory_order_seq_cst);
    atomic_store_explicit(&Y, 0, memory_order_seq_cst);

    thrd_create(&t2, (thrd_start_t)&b, NULL);
    thrd_create(&t1, (thrd_start_t)&a, NULL);

    thrd_join(t2);
    thrd_join(t1);

    printf("\n");
  }

  return 0;
}
