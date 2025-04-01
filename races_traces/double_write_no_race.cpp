#include <stdatomic.h>
#include <stdio.h>
#include <threads.h>

#include "librace.h"

atomic_int data1;
atomic_int data2;

static void a(void *obj) {
  atomic_store_explicit(&data1, 1, memory_order_seq_cst);
  atomic_store_explicit(&data1, 2, memory_order_seq_cst);
}

static void b(void *obj) {
  atomic_store_explicit(&data2, 1, memory_order_seq_cst);
  atomic_store_explicit(&data2, 2, memory_order_seq_cst);
}

int main(int argc, char **argv) {
  thrd_t t1, t2;

  atomic_init(&data1, 0);
  atomic_init(&data2, 0);

  printf("Main thread: creating 2 threads\n");
  thrd_create(&t1, (thrd_start_t)&a, NULL);
  thrd_create(&t2, (thrd_start_t)&b, NULL);

  thrd_join(t1);
  thrd_join(t2);

  printf("Reading data1 %d\n",
         atomic_load_explicit(&data1, memory_order_seq_cst));
  printf("Reading data2 %d\n",
         atomic_load_explicit(&data2, memory_order_seq_cst));
  printf("Main thread is finishing\n");

  return 0;
}
