# Overriding expression functions

As the framework is interpreting expressions containing functions, these functions are implemented in the framework,
but there may be bugs in some of them. You can override their implementation through:

```python
   FunctionsRepository.register("concat", lambda arguments: "".join(arguments))
   FunctionsRepository.register("trim", lambda text, trim_argument: text.strip(trim_argument[0]))
```
