prompt_toolkit2
---------------

This package is simply a renamed version of the v2.0 branch of the [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit/tree/2.0) package. The intent here is
that you can install prompt_toolkit and prompt_toolkit2 into the same venv/interpreter at the same time. You can then stay on v2 by renaming all your `import prompt_toolkit` imports
to `import prompt_toolkit2`.

Note that it is almost certainly impossible to pass objects between v2 and v3 branches of prompt_toolkit so don't try using this to make some sort of hybrid use of the libraries.
I haven't tested importing prompt_toolkit v3 and prompt_toolkit2 into the same process but I don't know why you would want to do that in the first place. They probably won't interfere
with each other though so if you have to import both in the same interpreter it might work ok.

The source code is unchanged from the v2 branch aside from the mechanical renaming. There were two unreleased bug fixes from 2019 in the branch so maybe that'll help you out a bit.
I don't think anyone expects more maintenance work done on the v2 branch of prompt_toolkit so this is probably going to be the last release of prompt_toolkit2. Tests are passing in
Python 2 and Python 3.9+ interpreters.
