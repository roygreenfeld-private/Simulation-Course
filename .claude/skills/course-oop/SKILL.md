---
name: course-oop
description: OOP rules for this Simulation course project, merging the course's Python OOP tutorial (תרגול 2) with general OOP guidance, where the tutorial wins every conflict. Use whenever writing, reviewing or designing a class or method in this project, including Trek, Traveler, Guide, Agency or any new class, and for questions about inheritance, encapsulation, composition, SOLID or design patterns, or requests in Hebrew such as מחלקה, מתודה, הורשה, בנאי, תכנות מונחה עצמים. Prefer this skill over oop-guide inside this project.
---

# Course OOP Guide

Graders compare the work to what the course taught, so course style comes first.
General OOP guidance fills only the gaps the tutorial leaves open.

## Priority

1. The assignment spec, when one applies (for HW1: `HW 2027A.pdf`). It is binding.
2. The course tutorial (תרגול 2 - חזרה על מונחת עצמים בפייתון).
3. General OOP guidance (the `oop-guide` skill).

## Rules from the tutorial

- A class models one concept, through attributes (data) and methods (behavior).
- `__init__` defines every attribute. Create lists there, so that a change to one object never affects another.
- Default parameters give meaningful behavior and are immutable values, such as `x=0` or `category="general"`.
- Every method takes `self` and works on that object's own attributes.
- Objects interact by passing an object as a parameter, like `get_distance(self, other_rocket)`.
- A container class holds objects in a list and offers add, search and show methods, like `Library`.
- Inherit when the child is a special kind of the parent, like `Shuttle(Rocket)`:
  - Call `super().__init__(...)` and pass it the parent's arguments.
  - Add only what is new, and override a method only when behavior differs.
  - Reuse the parent's version inside an override with `super().method()`, like `display_info`.
- Module files are lowercase with underscores, and classes start with a capital letter (`rocket.py`, `Rocket`).
- Import with `from module import ClassName`. Never use `import *`, and avoid cryptic aliases like `import rocket as r`.
- Access attributes and methods with dot notation.

## Conflicts, resolved for the tutorial

| Topic | Tutorial | General guidance | Ruling |
|---|---|---|---|
| State | Public attributes read with dot notation (`my_rocket.y`) | Keep state private | Public attributes. Do not use `_` prefixes or `@property`. Change state that has rules through methods, as `move_rocket` and `borrow_book` do |
| Reuse | Teaches inheritance for "a special kind of" | Prefer composition | Use inheritance when the is-a relation is true. Use composition for has-a, as `Library` holds `Book` objects |
| Contracts | Shared method names, with no abstract classes; `get_distance` works for a `Rocket` or a `Shuttle` | Program to interfaces, use abstract classes | Rely on shared method names. Do not add `abc` unless the user or spec asks for it |

## What general guidance still adds

None of these contradict the tutorial, so apply them:

- **Single responsibility:** split a class only by real responsibility. Methods the spec assigns to a class stay in that class, even when the class grows.
- **Liskov substitution:** a subclass must honor its parent's behavior, and code that accepts a parent must also work with a child. Check objects with `isinstance`, not `type(x) is`, so that subclasses pass.
- **Patterns:** add Factory, Strategy or Observer only when one clearly simplifies existing code, never in advance.
- **Mutable state:** no method reassigns an object's identity field after creation. Copy a list received from a caller before storing it.

## Design smells

- **God Object:** new behavior that does not belong to the concept goes to a new class.
- **Refused Bequest:** a subclass that disables inherited behavior is not really a kind of its parent; use composition.
- **Downcasting:** code asking which subclass it holds should call a shared method instead.
- **Alternative classes:** two classes doing the same job use the same method name and signature.
- **Temporary Field:** a field that is empty in some states, like `guide=None`, is handled explicitly wherever it is read. Keep it when the spec requires the field.

## Failure reporting

The tutorial's `borrow_book` only prints a failure message. Follow that unless the spec asks for exception handling.
HW1 does ask, so there methods `raise` and the calling code decides what to do with `try/except`.

## When a choice goes beyond the tutorial

State it in a short comment or note, so the reader sees that it was deliberate.
