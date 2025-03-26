#include <cassert>

#include <stdatomic.h>
#include <stdio.h>
#include <threads.h>

#include "librace.h"

atomic_bool x, y;
atomic_int z;

void write_x() { atomic_store_explicit(&x, true, memory_order_seq_cst); }

void write_y() { atomic_store_explicit(&y, true, memory_order_seq_cst); }

void read_x_then_y() {
  while (!atomic_load_explicit(&x, memory_order_seq_cst))
    ;
  if (atomic_load_explicit(&y, memory_order_seq_cst))
    ++z;
}

void read_y_then_x() {
  while (!atomic_load_explicit(&y, memory_order_seq_cst))
    ;
  if (atomic_load_explicit(&x, memory_order_seq_cst))
    ++z;
}

int main() {
  thrd_t t1, t2, t3, t4;

  atomic_init(&x, false);
  atomic_init(&y, false);
  atomic_init(&z, 0);

  thrd_create(&t1, (thrd_start_t)&write_x, NULL);
  thrd_create(&t2, (thrd_start_t)&write_y, NULL);
  thrd_create(&t3, (thrd_start_t)&read_x_then_y, NULL);
  thrd_create(&t4, (thrd_start_t)&read_y_then_x, NULL);

  thrd_join(t1);
  thrd_join(t2);
  thrd_join(t3);
  thrd_join(t4);

  assert(atomic_load(&x)); // will never happen
}
