#include <stdatomic.h>
#include <stdio.h>
#include <threads.h>

#include "librace.h"

atomic_int data;

static void a(void *obj) {
  atomic_store_explicit(&data, 1, memory_order_seq_cst);
}

static void b(void *obj) {
  atomic_store_explicit(&data, 2, memory_order_seq_cst);
}

int main(int argc, char **argv) {
  thrd_t t1, t2;

  atomic_init(&data, 0);

  thrd_create(&t1, (thrd_start_t)&a, NULL);
  thrd_create(&t2, (thrd_start_t)&b, NULL);

  thrd_join(t1);
  thrd_join(t2);

  printf("Reading %d\n", atomic_load_explicit(&data, memory_order_seq_cst));

  return 0;
}
