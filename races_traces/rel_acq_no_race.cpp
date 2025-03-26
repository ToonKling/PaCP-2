#include <cassert>
#include <stdatomic.h>
#include <stdio.h>
#include <threads.h>

atomic_int ptr;
int data;

void producer() {
  data = 42;
  atomic_store_explicit(&ptr, 500, memory_order_release);
}

void consumer() {
  int p2;
  while (!(p2 = atomic_load_explicit(&ptr, memory_order_acquire)))
    ;
  if (p2 != 500) {
    printf("p2 != 500\n");
  }
  if (data != 42) {
    printf("data != 42\n");
  }
}

int main() {
  thrd_t t1, t2;

  thrd_create(&t1, (thrd_start_t)&producer, NULL);
  thrd_create(&t2, (thrd_start_t)&consumer, NULL);

  thrd_join(t1);
  thrd_join(t2);
}
