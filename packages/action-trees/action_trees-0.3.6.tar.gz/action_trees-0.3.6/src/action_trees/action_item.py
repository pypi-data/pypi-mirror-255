#!/usr/bin/env python3
"""
 Base class for action items.

 Copyright (c) 2023 FILICS GmbH & ROX Automation
"""
from __future__ import annotations
from typing import Coroutine, Callable
import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum, auto
from action_trees.protocols import ActionItemProtocol


class StateTransitionException(Exception):
    """Exception raised when an invalid state transition is attempted"""


class ActionFailedException(Exception):
    """Exception raised when an action can not be completed successfully"""

    def __init__(self, message: str, action: ActionItemProtocol) -> None:
        super().__init__(message)
        self.action = action

    def __str__(self) -> str:
        message = self.args[0] if self.args else ""
        return f"{message} in action '{self.action.name}' (class {self.action.__class__.__name__}))"


class BlockingType(Enum):
    """
    Enum representing the blocking types for actions in a VDA5050 compliant system.

    Attributes:
        NONE: Action can be executed in parallel with other actions and while the vehicle is driving.
        SOFT: Action can be executed in parallel with other actions, but the vehicle must not drive.
        HARD: Action must not be executed in parallel with other actions and the vehicle must not drive.
    """

    NONE = auto()
    SOFT = auto()
    HARD = auto()

    def __str__(self) -> str:
        return self.name


class ActionState(Enum):
    """Enum representing the states of an action item."""

    NONE = auto()
    WAITING = auto()
    INITIALIZING = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()
    FAILED = auto()

    def __str__(self) -> str:
        return self.name


# used for state transition checks
VALID_STATE_TRANSITIONS = [
    (ActionState.WAITING, ActionState.INITIALIZING),
    (ActionState.WAITING, ActionState.RUNNING),
    (ActionState.WAITING, ActionState.FAILED),
    (ActionState.INITIALIZING, ActionState.RUNNING),
    (ActionState.INITIALIZING, ActionState.FAILED),
    (ActionState.RUNNING, ActionState.FINISHED),
    (ActionState.RUNNING, ActionState.FAILED),
]


def check_state_transition(current_state: ActionState, new_state: ActionState) -> None:
    """Check if a state transition is valid.

    Args:
        current_state (ActionState): current state
        new_state (ActionState): new state

    Raises:
        StateTransitionException: if the transition is invalid
    """
    # switching between PAUSED and other states is only allowed by calling resume() or pause()
    if ActionState.PAUSED in (current_state, new_state):
        raise StateTransitionException(
            f"Invalid state transition: {current_state} -> {new_state}. You must call resume() or pause()"
        )

    # all other state transitions are checked against the VALID_STATE_TRANSITIONS list
    if (current_state, new_state) not in VALID_STATE_TRANSITIONS:
        raise StateTransitionException(
            f"Invalid state transition: {current_state} -> {new_state}"
        )


class ActionItem(ABC):
    """
    Abstract base class for action items.
    """

    # TODO: add callbacks for state changes

    def __init__(
        self,
        name: str,
        parent: ActionItemProtocol | None = None,
        logger: logging.Logger | None = None,
    ):
        """logger is optional, if not provided, a default logger will be used.
        using ROS logger is allowed."""
        self.name = name
        self.parent: ActionItemProtocol | None = parent or None
        self._children: dict[str, ActionItemProtocol] = {}

        self._log = logger or logging.getLogger(self.name)
        self._state: ActionState = ActionState.WAITING
        self._saved_state: ActionState = ActionState.NONE
        self._log.debug(f"initial state: {self._state}")

        # main task reference
        self._main_task: asyncio.Task | None = None

        # note: could use one event, but it would require polling waiting for resume
        self._pause_event = asyncio.Event()
        self._resume_event = asyncio.Event()

    def get_child(self, name: str) -> ActionItemProtocol:
        """get child by name"""
        try:
            return self._children[name]
        except KeyError as e:
            raise ValueError(f"no child with name {name}") from e

    def add_child(self, child: ActionItemProtocol) -> None:
        """add child"""
        self._children[child.name] = child
        child.parent = self

    def remove_child(self, name: str) -> None:
        """remove child by name"""
        self._children[name].parent = None
        del self._children[name]

    @property
    def children(self) -> list[ActionItemProtocol]:
        """get children"""
        return list(self._children.values())

    def display_tree(self, level: int = 0) -> None:
        """
        Recursively display children and their states in a tree structure.
        """
        indent = "    " * level  # 4 spaces for each level of indentation
        state = self.state.name if self.state else "UNDEFINED"
        print(f"{indent}- {self.name} : {state}")
        for child in self.children:
            child.display_tree(level + 1)

    # ------------------ Actions ------------------
    def start(self) -> asyncio.Task:
        """Start the action item."""
        if self._main_task is None:
            self._main_task = asyncio.create_task(self.main())
        else:
            self._log.warning("action already started")

        return self._main_task

    async def _start_children_parallel(self) -> None:
        """Runs all children in parallel."""
        await asyncio.gather(*[child.start() for child in self.children])

    async def main(self) -> None:
        """Main coroutine for the action item."""
        try:
            try:  # try to run the _on_init coroutine if it exists
                coro = getattr(self, "_on_init")
                await self._execute(coro, ActionState.INITIALIZING)
            except AttributeError:
                pass

            await self._execute(self._on_run, ActionState.RUNNING)

        except ActionFailedException as e:
            self._log.error(f"Failed. {e}")
            raise
        except StateTransitionException as e:
            self._log.error(f"State transition failed. {e}")
            raise

        except Exception as e:
            self._log.exception(f"Error occurred during execution: {e}")
            raise
        finally:
            self._log.info(f"Action {self.name} finished with state {self._state}")

    async def cancel(self) -> None:
        """Cancel the action item asynchronously."""

        self._log.info(f"canceling action {self.name}")

        # if the action is already finished, do nothing
        if self._state in [
            ActionState.FINISHED,
            ActionState.FAILED,
        ]:
            self._log.debug(
                f"action {self.name} is in {self._state} state, skipping cancel"
            )
            return

        # cancelling from PAUSED is not allowed
        check_state_transition(self._state, ActionState.FAILED)

        # cancel children
        await self._cancel_children()

        # cancel main task
        if self._main_task is not None:
            try:
                if self._main_task.cancel():
                    # Wait for the task to be cancelled
                    await self._main_task
            except asyncio.CancelledError:
                self._log.debug("task cancelled")
                # don't re-raise here, the task is cancelled by command.

        self.state = ActionState.FAILED

    def pause(self) -> None:
        """Pause the action item."""
        self._log.debug(f"Pausing {self.name}")
        if self._state not in [ActionState.INITIALIZING, ActionState.RUNNING]:
            raise StateTransitionException(
                f"Cannot pause from {self._state}, must be INITIALIZING or RUNNING"
            )
        self._pause_event.set()
        self._resume_event.clear()
        self._saved_state = self._state
        self._state = ActionState.PAUSED

    def resume(self) -> None:
        """Resume the action item."""
        self._log.debug(f"Resuming {self.name}")
        if self._state != ActionState.PAUSED:
            raise StateTransitionException(
                f"Cannot resume from {self._state}, must be PAUSED"
            )

        self._pause_event.clear()
        self._resume_event.set()
        self._state = self._saved_state
        self._saved_state = ActionState.NONE

    @property
    def state(self) -> ActionState:
        """Get the state of the action item."""
        return self._state

    @state.setter
    def state(self, state: ActionState) -> None:
        """Set the state of the action item."""
        if state == self._state:
            return

        check_state_transition(self._state, state)

        self._log.debug(f"Changing state {self._state} -> {state}")
        self._state = state

    def get_exception(self) -> BaseException | None:
        """Get the exception raised by the action item."""

        if self._main_task is None or not self._main_task.done():
            return None

        try:
            return self._main_task.exception()
        except asyncio.CancelledError:
            return asyncio.CancelledError(f"Action {self.name} was cancelled")

    async def _wait_if_paused(self) -> None:
        """Wait until the action is resumed"""
        if self._pause_event.is_set():
            self._log.debug("paused...")
            await self._resume_event.wait()
            self._log.debug("resumed")

    async def _cancel_children(self) -> None:
        """Cancel all children of this action item"""

        self._log.debug(f"Canceling children of {self.name}")
        for child in self.children:
            self._log.debug(f"Canceling child {child.name}")
            await child.cancel()

    async def _execute(
        self, action: Callable[[], Coroutine], action_state: ActionState
    ) -> None:
        """execute an action coroutine and handle exceptions

        Args:
            action (Callable[[], Coroutine]): coroutine to execute
            action_state (ActionState): state to set while executing the coroutine

        Raises:
            exc: exception raised by the coroutine
        """

        self._log.debug(f"Executing {action.__name__}")
        self.state = action_state

        # just an extra check to make sure the events are not set
        assert not self._pause_event.is_set(), "pause event should not be set"
        assert not self._resume_event.is_set(), "resume event should not be set"

        try:
            await action()
        except asyncio.CancelledError:
            self._log.debug(f"action {self.name} was cancelled")
            self.state = ActionState.FAILED
            raise
        except ActionFailedException:
            self.state = ActionState.FAILED
            # cancel children
            await self._cancel_children()
            raise

        except Exception as exc:
            self._log.error(f"Error in {action.__name__}: {exc}")
            self.state = ActionState.FAILED
            raise exc

        if self._state == ActionState.RUNNING:
            self.state = ActionState.FINISHED

    # ------------------ Action coroutines ------------------
    # This is where the actual work is done.
    # They are meant to be overridden by the user.

    @abstractmethod
    async def _on_run(self) -> None:
        """main coroutine for running the action item."""
