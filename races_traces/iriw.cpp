#include <cassert>
#include <stdatomic.h>
#include <stdio.h>
#include <threads.h>

#include "librace.h"

atomic_int flag;
atomic_int X;
atomic_int Y;
int x_1, x_2, y_1, y_2;

static void a(void *obj) {
  while (atomic_load_explicit(&flag, memory_order_seq_cst) == 0)
    ;

  atomic_store_explicit(&X, 1, memory_order_seq_cst);
}

static void b(void *obj) {
  while (atomic_load_explicit(&flag, memory_order_seq_cst) == 0)
    ;

  atomic_store_explicit(&Y, 1, memory_order_seq_cst);
}

static void c(void *obj) {
  while (atomic_load_explicit(&flag, memory_order_seq_cst) == 0)
    ;

  x_1 = atomic_load_explicit(&X, memory_order_seq_cst);
  y_1 = atomic_load_explicit(&Y, memory_order_seq_cst);
}

static void d(void *obj) {
  while (atomic_load_explicit(&flag, memory_order_seq_cst) == 0)
    ;

  y_2 = atomic_load_explicit(&Y, memory_order_seq_cst);
  x_2 = atomic_load_explicit(&X, memory_order_seq_cst);
}

int main(int argc, char **argv) {
  thrd_t t1, t2, t3, t4;

  atomic_init(&flag, 0);
  atomic_init(&X, 0);
  atomic_init(&Y, 0);

  thrd_create(&t1, (thrd_start_t)&a, NULL);
  thrd_create(&t2, (thrd_start_t)&b, NULL);
  thrd_create(&t3, (thrd_start_t)&c, NULL);
  thrd_create(&t4, (thrd_start_t)&d, NULL);

  atomic_store_explicit(&flag, 1, memory_order_seq_cst);

  thrd_join(t1);
  thrd_join(t2);
  thrd_join(t3);
  thrd_join(t4);

  printf("Reading X at 1: %d\n", x_1);
  printf("Reading Y at 1: %d\n", y_1);
  printf("Reading X at 2: %d\n", x_2);
  printf("Reading Y at 2: %d\n", y_2);

  if (x_1 == 1 && y_1 == 0 && y_2 == 1 && x_2 == 0)
    printf("Wild shit");

  return 0;
}
