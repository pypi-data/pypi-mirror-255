import asyncio
from action_trees import ActionItem


class AtomicAction(ActionItem):
    """Basic machine action with no children."""

    def __init__(self, name: str, duration: float = 0.1):
        super().__init__(name=name)
        self._duration = duration

    async def _on_run(self) -> None:
        await asyncio.sleep(self._duration)


class PrepareMachineAction(ActionItem):
    """Prepare the machine."""

    def __init__(self) -> None:
        super().__init__(name="prepare")
        self.add_child(AtomicAction(name="initialize"))
        self.add_child(AtomicAction(name="clean"))

    async def _on_run(self) -> None:
        # sequentially run children
        await self.get_child("initialize").start()
        await self.get_child("clean").start()


class MakeCappuccinoAction(ActionItem):
    """Make cappuccino."""

    def __init__(self) -> None:
        super().__init__(name="make_cappuccino")
        self.add_child(AtomicAction(name="boil_water"))
        self.add_child(AtomicAction(name="grind_coffee"))

    async def _on_run(self) -> None:
        # simultaneously run children
        await self._start_children_parallel()


class CappuccinoOrder(ActionItem):
    """High-level action to make a cappuccino."""

    def __init__(self) -> None:
        super().__init__(name="cappuccino_order")
        self.add_child(PrepareMachineAction())
        self.add_child(MakeCappuccinoAction())

    async def _on_run(self) -> None:
        for child in self.children:
            await child.start()


async def main() -> None:
    order = CappuccinoOrder()
    await order.start()
    order.display_tree()


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
