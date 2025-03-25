#include <stdatomic.h>
#include <stdio.h>
#include <threads.h>

#include "librace.h"

atomic_int data;
atomic_int flag1;
atomic_int flag2;

static void a(void *obj) {
  // Wait for thread b to set the flag.
  while (atomic_load_explicit(&flag1, memory_order_seq_cst)) {
  }
  atomic_store_explicit(&data, 1, memory_order_seq_cst);
  atomic_store_explicit(&flag2, 0, memory_order_seq_cst);
}

static void b(void *obj) {
  // "Passing" this flag allows thread a to store 1 in `data`.
  atomic_store_explicit(&flag1, 0, memory_order_seq_cst);
  while (atomic_load_explicit(&flag2, memory_order_seq_cst)) {
  }

  // Relaxed memory data race. Could read 0 or 1!
  printf("Reading data: %d\n",
         atomic_load_explicit(&data, memory_order_seq_cst));
}

int main(int argc, char **argv) {
  thrd_t t1, t2;

  atomic_init(&data, 0);
  atomic_init(&flag1, 1);
  atomic_init(&flag2, 1);

  printf("Main thread: creating 2 threads\n");
  thrd_create(&t1, (thrd_start_t)&a, NULL);
  thrd_create(&t2, (thrd_start_t)&b, NULL);

  thrd_join(t1);
  thrd_join(t2);
  printf("Main thread is finishing\n");

  return 0;
}
