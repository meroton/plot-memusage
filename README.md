# Plotting memusagestat's data

`memusage` is a great tool to track all allocations for a program,
this comes to many Linux distributions with `glibc` itself.
So if you need a quick-and-easy allocation tracker `memusage` is the tool for you!
There is a plotter, `memusagestat` that can draw a simple image for you,
but it shows its age and is inconvenient to work with.
  This is a new parser and plotter for the `memusage` data
with easy-to-use python code and nice looking plots.
We have a knoweldge document describing it in detail: [here]

![Improvement](static/memusagestat-bazel-improvement.png)

[here]: http://meroton.com/docs/captains-log/plotting-memusagestat-with-python/

## memusage & memusagestat

`memusage` is a good profiling tool bundled with `glibc` on Linux,
it tracks allocations for a program.
Its sibling `memusagestat` can plot the allocations,
which is interesting when looking at out-of-memory problems
and garbage-collection/memory thrashing.
The is good for an initial investigation,
there are few options for how to present the data
and the graph itself does not look very nice.
You can select to plot either by sequential allocation or by linear time.
We want to generate new,
nicer looking, figures
for the same data.

In this example use `memusage` to profile a `bazel` invocation that runs out of memory

```
$ memusage --data path/to/bazel.mem \
    bazel build ... \
    //...
```

and render a plot:

```
$ memusagestat bazel.mem -T -t
```

![original memusagestat plot](static/original-memusagestat.png)

We can create the corresponding plot with the following command:

```
$ ./memusagestat.py --stack=same-scale --title "Bazel's memory allocation" bazel.mem bazel-allocation.png
```

![new plot](static/bazel-allocation.png)
