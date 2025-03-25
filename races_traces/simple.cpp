#include <stdatomic.h>
#include <stdio.h>
#include <threads.h>

#include "librace.h"

atomic_int data;

static void a(void *obj) {
  atomic_store_explicit(&data, 1, memory_order_seq_cst);
}

static void b(void *obj) {
  int read = atomic_load_explicit(&data, memory_order_seq_cst);
  printf("Reading data: %d\n", read);
}

int main(int argc, char **argv) {
  thrd_t t1, t2;

  atomic_init(&data, 0);

  printf("Main thread: creating 2 threads\n");
  thrd_create(&t1, (thrd_start_t)&a, NULL);
  thrd_create(&t2, (thrd_start_t)&b, NULL);

  thrd_join(t1);
  thrd_join(t2);
  printf("Main thread is finishing\n");

  return 0;
}
