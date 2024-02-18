# Action Trees



![build status](https://gitlab.com/roxautomation/action-trees/badges/main/pipeline.svg)


---

**Documentation**: [https://roxautomation.gitlab.io/action-trees](https://roxautomation.gitlab.io/action-trees)

**Source Code**: [https://gitlab.com/roxautomation/action-trees](https://gitlab.com/roxautomation/action-trees)


---

# Summary

*Action Trees* is an `asyncio`-based framework designed for orchestrating hierarchical, asynchronous actions. It enables the structuring of complex processes into manageable, interdependent tasks, facilitating the execution of multi-step workflows either sequentially or in parallel. This framework is particularly suitable for systems that require coordinated, concurrent task management.

The `ActionItem` class, a key component of the `action_trees` module, is an abstract base class tailored for managing hierarchical action items, especially in VDA5050 compliant systems. Its main features include:

1. **State Management:** Manages various states (`NONE`, `WAITING`, `INITIALIZING`, `RUNNING`, `PAUSED`, `FINISHED`, `FAILED`) for action items, ensuring valid transitions between these states.

2. **Exception Handling:** Implements custom exceptions (`StateTransitionException` and `ActionFailedException`) to handle invalid state transitions and failures in action completion.

3. **Task Execution and Management:** Supports starting, pausing, resuming, and canceling action items, with an emphasis on asynchronous execution using `asyncio`.

4. **Child Actions Handling:** Provides functionality for adding, removing, and managing child action items, enabling a structured, hierarchical approach to action management.

5. **Core Method Implementation:** Requires subclasses to implement the `_on_run` abstract method to define the primary behavior of the action item. An optional `_on_init` method can be implemented for initial setup steps.




## Action Trees vs. Behavior Trees

Behavior Trees (BTs) and Action Trees (ATs) use a tree-like structure but have different goals. BTs make choices about *what to do next* based on current situations, which is great for tasks needing quick decisions. ATs are about *executing* complex tasks efficiently, with a focus on robust error-handling errors and asynchronous operation.
In short, BTs are for making decisions, while ATs are for carrying out tasks effectively.


## Example - Coffee maker

Let's simulate a coffee-making machine using the following action hierarchy:


    - cappuccino_order
        - prepare
            - initialize
            - clean
        - make_cappuccino
            - boil_water
            - grind_coffee


An implementation would look like this:

```python
import asyncio
from action_trees import ActionItem


class AtomicAction(ActionItem):
    """Mock action with no children."""

    def __init__(self, name: str, duration: float = 0.1):
        super().__init__(name=name)
        self._duration = duration

    async def _on_run(self):
        await self._wait_if_paused() # pause/resume helper
        await asyncio.sleep(self._duration)


class PrepareMachineAction(ActionItem):
    """Prepare the machine."""

    def __init__(self):
        super().__init__(name="prepare")
        self.add_child(AtomicAction(name="initialize"))
        self.add_child(AtomicAction(name="clean"))

    async def _on_run(self):
        # sequentially run children
        await self.get_child("initialize").start()
        await self.get_child("clean").start()


class MakeCappuccinoAction(ActionItem):
    """Make cappuccino."""

    def __init__(self):
        super().__init__(name="make_cappuccino")
        self.add_child(AtomicAction(name="boil_water"))
        self.add_child(AtomicAction(name="grind_coffee"))

    async def _on_run(self):
        # simultaneously run children
        await self._start_children_parallel()


class CappuccinoOrder(ActionItem):
    """High-level action to make a cappuccino."""

    def __init__(self):
        super().__init__(name="cappuccino_order")
        self.add_child(PrepareMachineAction())
        self.add_child(MakeCappuccinoAction())

    async def _on_run(self):
        for child in self.children:
            await child.start()


# create root order
order = CappuccinoOrder()
# start tasks in the background
await order.start()


```


# Development

see [docs](docs/development.md)

---------------------

This project was forked from [cookiecutter template](https://gitlab.com/roxautomation/python-template) template.
