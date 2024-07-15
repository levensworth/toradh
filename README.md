# TORADH
[![codecov](https://codecov.io/github/levensworth/toradh/graph/badge.svg?token=hsojulL0hJ)](https://codecov.io/github/levensworth/toradh)

Minimalistic library intended to bring better flow control to Python.

## Motivation:
Have you ever install a new sdk or lib that you really wanted to use for a particular project only to find out, mid development
that if you try to `.get()` something that is not present in the instance it will `raise` an `ValueError` which was not mentioned
in any docstring. Dows it sounds familiar? well, this kind of frustration is what `toradh` (pronounced "taru") comes to ease.
By bringing some of the key fundamental structures of languages such as `Rust` to Python, we aim to make exception handling a little
less chaotic and more predictable when needed. 

## Install:
```
pip install toradh
```


## How to:
We support structural pattern matching with the `match` operator as well as build in methods for control flow management.

```python
from typing import Literal
from toradh import Result, Ok, Err

DB = {
    1: 'john', 
    2: 'jane',
}

def create_user(name: str) -> Result[int, ValueError | KeyError]:
    if name in DB:
        return Err(KeyError(f'A user by {name} already exists'))
    if len(name) > 10:
        return Err(ValueError('names can not be too long'))
    user_id = len(DB)+1
    DB[user_id] = name
    return Ok(user_id)

def basic_handling():
    # In this example, we don't want to interrupt the execution
    # but we don't really want to handle specific errors
    res = create_user('janet')
    match res:
        case Ok(user_id):
            print(f'successfully persisted under {user_id}')
        case Err(err):
            print(f'There was an error => {err}')

def concrete_error_handling():
    # In this case, we are handling each possible scenario and 
    # taking some sort of action based on the type of error
    res = create_user('janet')
    
    # If all cases aren't handle mypy will alert about this.
    match res.kind():
        case int():
            print(f'successfully persisted under {res.unwrap()}')
        case ValueError():
            print(f'There was a problem with the name\'s length')
        case KeyError()
            print(f'Name already exists')
            #include possible measure to recover from this error
            ...

def no_handling():
    # in this case, we do not want to handle the possible errors
    # if any are give, the .unwrap() call simply raise them as normal python code
    res = create_user('janet')
    print(f'successfully persisted under {res.unwrap()}')

if __name__ == '__main__:
    basic_handling()

    concrete_error_handling()
    
    no_handling()

```


### Example of why to use Toradh
First let's go over some simple examples:

Let's go over an example not using the framework
```python

DB = {
    1: 'john', 
    2: 'jane',
}

# instead of this
def get_user_by_id_old(user_id: int) -> str | None:
    return DB.get(user_id)    

def main():
    user = get_user_by_id_old(1)
    
    if user is not None:
        print(f'Hello {user}')
    else:
        print('id not found')
```

and how it would look like if using it
```python
from toradh import Option, Nothing, Some

DB = {
    1: 'john', 
    2: 'jane',
}

def get_user_by_id_new(user_id: int) -> Option[str]:
    if user_id not in DB:
        return Nothing()
    
    return Some(DB.get(user_id))
    
def main():
    user = get_user_by_id_new(1)
    
    if user.is_some():
        print(f'Hello {user.unwrap()}')
    else:
        print('id not found')
        
```


Now, at this point it really doesn't add too much. But if you allow the following state to 
exist in your `DB`.

```python
D  = {
    1: 'john',
    2: 'jane',
    3: None
}
```
Then things, get tricky for the first implementation. 
***How do you distinguish between the DB value `None` and the state of element not found?***

A possible solution would be:

```python

DB = {
    1: 'john', 
    2: 'jane',
}

def get_user_by_id_old(user_id: int) -> str | None:
    return DB[user_id] # this will raise a KeyError if user_id is not part of DB

def main():
    try:
        user = get_user_by_id_old(1)
    except KeyError:
        print('user not found') 
        return # cut control flow here
    
    if user is not None:
        print(f'Hello {user}')
    else:
        print(f'User gone')
```

Which is not ideal as the KeyError exception is not visible throw the type hint system, which puts the 
pleasure of correctly handling this behavior on the invoker.

As opposed to this implementation:

```python
from toradh import Option, Nothing, Some

DB = {
    1: 'john', 
    2: 'jane',
    3: None
}

def get_user_by_id_new(user_id: int) -> Option[str | None]:
    if user_id not in DB:
        return Nothing()
    
    return Some(DB.get(user_id))
    
def main():
    user = get_user_by_id_new(1)
    
    match user:
        case Nothing():
            print('id not found')    
        case Some(None):
            print('User is gone')
        case Some(name):
            print(f'Hello {name}')
        
```

In this example (although not really a good use of `None`) we can see that there is a clear distinction between the absence of what 
we want and an actual product of calling the function.

