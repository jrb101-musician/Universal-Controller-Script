"""
control_surfaces > controls > control_surface

Contains the ControlSurface class, which defines the abstract base type for
all control surfaces.

Authors:
* Miguel Guthridge [hdsq@outlook.com.au, HDSQ#2154]

This code is licensed under the GPL v3 license. Refer to the LICENSE file for
more details.
"""
# from __future__ import annotations

from fl_classes import FlMidiMsg
from time import time
from typing import Optional, final
from abc import abstractmethod
from common import getContext
from common.util.abstract_method_error import AbstractMethodError
from common.types import Color
from control_surfaces.event_patterns import NullPattern
from control_surfaces.value_strategies import NullEventStrategy
from ..event_patterns import IEventPattern
from ..value_strategies import IValueStrategy
from ..control_mapping import ControlEvent, ControlMapping
from ..managers import (
    IAnnotationManager,
    IColorManager,
    IValueManager,
    DummyAnnotationManager,
    DummyColorManager,
    DummyValueManager,
)


class ControlSurface:
    """
    Defines an abstract base class for a control surface.

    This class is extended by all other control surfaces.
    """

    @staticmethod
    @abstractmethod
    def getControlAssignmentPriorities() -> 'tuple[type[ControlSurface], ...]':
        """
        Returns a list of the control's assignment priorities

        These determine what controls are assigned to what parameters. If an
        assignment can't be made to this type, then it will be made to the next
        available type in the list, and so on...

        ### Returns:
        * `list[type]`: control assignment priorities
        """
        raise AbstractMethodError()

    @staticmethod
    def isPress(value: float) -> bool:
        """
        Returns whether a value (0-1.0) for this control should count as a
        press.

        Control surface definitions override this method in order to provide
        double press functionality.

        This is used to create the doublePress property for ControlEvent
        objects

        ### Args:
        * `value` (`float`): value to check

        ### Returns:
        * `bool`: whether this value should be counted as a press
        """
        return False

    def __init__(
        self,
        event_pattern: Optional[IEventPattern] = None,
        value_strategy: Optional[IValueStrategy] = None,
        coordinate: tuple[int, int] = (0, 0),
        annotation_manager: Optional[IAnnotationManager] = None,
        color_manager: Optional[IColorManager] = None,
        value_manager: Optional[IValueManager] = None,
    ) -> None:
        """
        Create a ControlSurface

        ### Args:
        * `event_pattern` (`IEventPattern`): pattern to use when recognizing
          the event
        * `value_strategy` (`IValueStrategy`): strategy for getting values from
          events
        * `group` (`str`): group that this control belongs to. Controls in
          different groups are never assigned together.
        * `coordinate` (`tuple[int, int]`, optional): coordinate of controls.
          Used if controls form a 2D grid (eg, drum pads). Defaults to (0, 0).
        """
        if event_pattern is None:
            event_pattern = NullPattern()
        self._pattern = event_pattern
        self._color = Color()
        self._annotation = ""
        self._value = 0.0
        if value_strategy is None:
            value_strategy = NullEventStrategy()
        self._value_strategy = value_strategy
        self._coord = coordinate

        # Attributes to make our pressed thing work better
        self._needs_update = False
        self._got_update = False

        # Whether we need to call the onUpdate... methods
        self._color_changed: bool = True
        self._annotation_changed: bool = True
        self._value_changed: bool = True

        # Managers for control
        if annotation_manager is None:
            self.__annotation_manager = annotation_manager
        else:
            self.__annotation_manager = DummyAnnotationManager()
        if color_manager is None:
            self.__color_manager = color_manager
        else:
            self.__color_manager = DummyColorManager()
        if value_manager is None:
            self.__value_manager = value_manager
        else:
            self.__value_manager = DummyValueManager()

        # The time that this control was pressed last
        self._press = 0.0
        # The time that this control was tweaked last
        self._tweak = 0.0

    def __repr__(self) -> str:
        """
        String representation of the control surface
        """
        return \
            f"{self.__class__}, ({self._coord}, {self.value})"

    @final
    def getPattern(self) -> IEventPattern:
        """
        Returns the event pattern used by this control surface

        This allows validation to be performed if using the control within a
        particular control matcher.

        ### Returns:
        * `IEventPattern`: pattern
        """
        return self._pattern

    @final
    def getMapping(self) -> ControlMapping:
        """
        Returns a mapping to this control, for the purpose of acting as a key
        to the control in a dictionary.

        Mappings are used to refer to a control without being able to easily
        modify its value.

        ### Returns:
        * `ControlMapping`: A mapping to this control
        """
        return ControlMapping(self)

    @final
    def match(self, event: FlMidiMsg) -> Optional[ControlEvent]:
        """
        Returns a control event if the given event matches this
        control surface, otherwise returns None

        ### Args:
        * `event` (`FlMidiMsg`): event to potentially match

        ### Returns:
        * `Optional[ControlEvent]`: control mapping, if the event maps
        """
        if self._pattern.matchEvent(event):
            self._value = self._value_strategy.getValueFromEvent(
                event, self._value)
            channel = self._value_strategy.getChannelFromEvent(event)
            self._needs_update = True
            self._got_update = False
            t = time()
            self._tweak = t
            if self.isPress(self.value):
                double_press = t - self._press \
                    <= getContext().settings.get("controls.double_press_time")
                self._press = t
            else:
                double_press = False
            return ControlEvent(self, self.value, channel, double_press)
        else:
            return None

    ###########################################################################
    # Properties

    @property
    def coordinate(self) -> tuple[int, int]:
        """
        Coordinate of the control. Read only.
        """
        return self._coord

    @property
    def color(self) -> Color:
        """
        Represents the color of the control

        On compatible controllers, this can be displayed on the control using
        LED lighting.
        """
        return self._color

    @color.setter
    def color(self, c: Color):
        self._got_update = True
        if self._color != c:
            self._color = c
            self._color_changed = True

    @property
    def annotation(self) -> str:
        """
        Represents the annotation of the control

        On compatible controllers, this can be displayed as text near the
        control.
        """
        return self._annotation

    @annotation.setter
    def annotation(self, a: str):
        if self._annotation != a:
            self._annotation = a
            self._annotation_changed = True

    @property
    def value(self) -> float:
        """
        The value property represents the value of a control (eg the rotation
        of a knob, or the position of a fader).

        It is gotten and set using a float between 0-1.0, but could be
        represented in other ways inside the class. The way it is gotten and
        set is determined by the functions _getValue() and _setValue()
        respectively.
        """
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        # Ensure value is within bounds
        if not (0 <= val <= 1):
            raise ValueError(
                "Value for control must be between 0 and 1"
            )
        if self._value != val:
            self._value = val
            self._needs_update = True
            self._got_update = False
            self._value_changed = True

    @property
    def needs_update(self) -> bool:
        """
        Represents whether the value of the control has changed since the last
        time the color was set.
        """
        return self._needs_update

    @property
    def got_update(self) -> bool:
        """
        Represents whether the value of the control has changed since the last
        time the color was set, and was since updated.
        """
        return self._got_update

    @property
    def last_tweaked(self) -> float:
        """
        Returns the last time that the control was tweaked

        ### Returns:
        * `float`: unix time of last tweak
        """
        return self._tweak

    ###########################################################################
    # Events

    def onColorChange(self, new: Color) -> None:
        """
        Called when the color of the control changes

        This can be overridden to send a MIDI message to the controller if
        required, so that the color can be shown on compatible controls.

        ## Args:
        * `new` (`Color`): The new value
        """

    def onAnnotationChange(self, new: str) -> None:
        """
        Called when the annotation of the control changes

        This can be overridden to send a MIDI message to the controller if
        required, so that the annotation can be shown on compatible controls.

        ## Args:
        * `new` (`str`): The new value
        """

    def onValueChange(self, new: float) -> None:
        """
        Called when the value of the control changes

        This can be overridden to send a MIDI message to the controller if
        required, so that the value can be shown on compatible controls.

        ## Args:
        * `new` (`float`): The new value as a float between `0` and `1`
        """

    @final
    def doTick(self, thorough: bool) -> None:
        """
        Called when a tick happens

        This function is used to call the main tick method which is overridden
        by child classes.

        ### Args:
        * thorough (`bool`): Whether a full tick should be done.
        """
        # If it's a thorough tick, force all the properties to update on the
        # device
        # Otherwise, only update them if they need it
        if thorough or self._color_changed:
            self.onColorChange(self.color)
        if thorough or self._annotation_changed:
            self.onAnnotationChange(self.annotation)
        if thorough or self._value_changed:
            self.onValueChange(self.value)
        self.tick()
        if self._got_update:
            self._needs_update = False
            self._got_update = False

    def tick(self) -> None:
        """
        Called when a tick happens

        This can be overridden to do anything necessary to keep the control
        functioning correctly.
        """
