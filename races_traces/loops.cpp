#include <atomic>
#include <stdatomic.h>
#include <stdio.h>
#include <threads.h>

#include "librace.h"

atomic_int data;
atomic_int flag1;
atomic_int flag2;

static void a(void *obj) {
  for (int i = 0; i < 1000; i++) {
    int value = atomic_load_explicit(&data, memory_order_acquire);
    atomic_store_explicit(&data, value + 1, memory_order_release);
  }
}

int main(int argc, char **argv) {
  thrd_t t1, t2;

  atomic_init(&data, 0);

  printf("Main thread: creating 2 threads\n");
  thrd_create(&t1, (thrd_start_t)&a, NULL);
  thrd_create(&t2, (thrd_start_t)&a, NULL);

  thrd_join(t1);
  thrd_join(t2);

  printf("Reading: %d\n", atomic_load_explicit(&data, memory_order_seq_cst));
  printf("Main thread is finishing\n");

  return 0;
}
