## Follow the Path

Due to the extensive filesystem use of the application, a helper is created to aid in the handling of paths.

#### Path Objects

In its basic form the [NoisePath] object allows one to store a normalized path, return it as a string, and return an appended path when called:

```python
class NoisePath(object):
    def __init__(self, path):
        # determine normalized path
        path = os.path.normpath(path)
        # determine file directory
        if len(os.path.splitext(path)[1]):
            path = os.path.dirname(path)
        # set path
        self.path = path

    def __str__(self):
        # return path string
        return str(self.path)

    def __call__(self, path):
        # return joined path
        return os.path.join(str(self.path), str(path).lstrip('/'))
```

This provides the following functionality:

```python
>>> from path import Path
>>> path = Path('/tmp')
>>> print path
/tmp
>>> print path('foo.txt')
/tmp/foo.txt
>>> print path.paths
('build', 'static', 'template')
>>> print path.build('bar.txt')
/tmp/build/bar.txt
```

Additional logic provides a method for returning the relative path compared to a passed argument:

```python
class NoisePath(object):
    def __init__(self, path):
        ...
        # relative path helper
        class relpath(object):
            path = self.path
            def __str__(self):
                return '/'
            def __call__(self, path):
                return '/' + os.path.relpath(str(path), str(self.path))
        # set relative path
        self.relative = relpath()
```

#### Path Helper

A [Path] helper object encapsulates this `Path` object to represent the project root. Additional path objects are then instantiated to represent the `build`, `static`, and `template` directories:

```python
class Path(NoisePath):
    paths = ('build', 'static', 'template')

    def __init__(self, path):
        # initialize project path
        NoisePath.__init__(self, path)

        # initialize additional paths
        map(lambda p: setattr(self, p, NoisePath(self(p))), self.paths)
```

An `init()` method is provided to handle the creation of project directories:

```python
class Path(NoisePath):
    ...
    def init(self):
        # create project paths
        map(os.makedirs, filter(lambda p: not os.path.exists(p),
            map(str, [self.path] + map(lambda p: getattr(self, p),
                self.paths))))
```

Calling this upon application initialization products the following directory tree:

```
$ ./noise.py init blog

blog
|-- build
|-- static
`-- template
```

[Path]: https://github.com/ryonsherman/noise/blob/c062b663ef97ca71d7bf7ef1d6be48b66d94c197/src/noise/path.py#L41
[NoisePath]: https://github.com/ryonsherman/noise/blob/c062b663ef97ca71d7bf7ef1d6be48b66d94c197/src/noise/path.py#L11
