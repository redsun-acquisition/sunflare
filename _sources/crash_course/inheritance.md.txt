# Inheritance

[Inheritance] is a mechanism of basing a class on the implementation of another class. The original class is often referred to as a *parent*, the class that implements the original is often referred to as a *child* class.

In Python, parent classes can provide *abstract methods*, functions without actual executable code but instead serving as a customizable template.

```mermaid
:config: {"theme": "base"}
:align: center
%%{init: { 'theme': 'base', 'themeVariables': { 'primaryColor': '#fefefe', 'lineColor': '#aaa000', } } }%%

    classDiagram
        class Animal{
            +int paws
            fly()*void
            talk()*void
            how_many_paws() int
        }
        class Duck {
            fly() void
            talk() void
        }

        Animal <|-- Duck : inherits from
        note for Animal "Duck inherits from Animal"
```

The diagram shows an example this: `Animal` provides an interface with both _abstract_ and normal methods, while `Duck` provides an implementation for the _abstract_ methods. In Python, this would be equivalent to:

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    paws: int

    @abstractmethod
    def fly(self):
        ...
    @abstractmethod
    def talk(self):
        ...
    
    def how_many_paws(self):
        print("I have", self.paws, "paws")

class Duck(Animal):
    def __init__():
        self.paws = 2

    def fly(self):
        print("Flying!")
    def talk(self):
        print("Quack!")

animal = Duck(2)
duck.fly() # prints "Flying!"
duck.talk() # prints "Quack!"
duck.how_many_paws() # prints "I have 2 paws"
```

It's an effective pattern which allows to reuse the same code and extend it depending on the need.

But sometimes it may become an hinderance. If we want to create a `Cat` class instead ...

```python

class Cat(Animal):
    def __init__(self):
        self.paws = 4

    # cats can't fly,
    # they can only talk
    def talk(self):
        print("Meow!")

cat = Cat()
# the line above causes an exception:
# TypeError: Can't instantiate abstract class Cat with abstract method fly
```

... we get an error! Of course, we could just implement `fly()` and simply print `I can't fly`, but a real situation that method may be doing a computation or performing another action which is inconsistent with the defined base class `Animal`.


[inheritance]: https://en.wikipedia.org/wiki/Inheritance_(object-oriented_programming)
