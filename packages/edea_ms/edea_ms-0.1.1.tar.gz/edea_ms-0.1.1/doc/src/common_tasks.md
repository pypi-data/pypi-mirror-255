# Common Tasks

As edea-ms (and edea-tmc) are rather simple in terms of complexity, it can be a real headscratcher if one needs to do things which seem outside the box at first glance. The following are a few ideas how to solve some problems which we encountered ourselves while characterizing hardware.

## Postprocessing results

Often the raw measurement data needs to go through another stage of refinement until it's actually in a shape that's useful to compare and analyze. Given that there's no concept of postprocessing in edea-ms, it's something that has to be represented with what we have available.

What we have are testruns. If we apply the same concept of TMaC[^tmac] to our data, we can write a program which takes the initial testrun, postprocesses the data and then publishes it again as a testrun. This way we can also iterate over our postprocessing pipeline easily while keeping the original data around so that we don't need to run the measurements again all the time.

While this is not too useful of a thing to do once everything is up and running and performs as expected, it makes iterating easier in the early stages.

```python
# example code here
```

[^tmac]: Test and Measurement as Code
