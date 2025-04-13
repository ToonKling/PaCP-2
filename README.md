# PaCP Project Group 2

## Setup

To setup the project, run

> pip install -r requirements.txt

## Run

To run evaluate one file with traces, use

> ./trace_reader.py ./races_traces/barrier1.txt --find-all --draw-graph

or

> python3 ./races_traces/barrier1.txt --find-all --draw-graph

If the optional argument --find-all is not supplied, the algorithm will return only the first Datarace.

If the optional argument --draw-graph is not supplied, no graph will be drawn of the execution trace.

Alternatively, use any of the other traces provided in the `./races_traces/` folder.

If you run the above example command, it will generate the following output:

![Result from example script](https://github.com/user-attachments/assets/aaefa01a-03cc-4ba9-a85b-b71f35809ee3)

## Tests

To run all tests, use
> pytest

## What is inside this repo?

The main script we use is `./trace_reader.py`. It will find the data races for a given trace. For unittesting we use `test_trace_reader.py`.

We have stored example traces, together with the C/C++ programs used to generate them in `./races_traces/`.

For example, `loops.cpp` was used to generate traces in `loop1.txt` and `loops2.txt`.
Since compilation and trace generation requires the C11tester project, we provide no instructions on generating new traces.

