# TORADH

Minimalistic library intended to bring better flow control to Python.

Have you ever install a new sdk or lib that you really wanted to use for a particular project only to find out, mid development
that if you try to `.get()` something that is not present in the instance it will `raise` an `ValueError` which was not mentioned
in any docstring. Dows it sounds familiar? well, this kind of frustration is what `toradh` (pronounced "taru") comes to ease.
By bringing some of the key fundamental structures of languages such as `Rust` to Python, we aim to make exception handling a little
less chaotic and more predictable when needed. 

