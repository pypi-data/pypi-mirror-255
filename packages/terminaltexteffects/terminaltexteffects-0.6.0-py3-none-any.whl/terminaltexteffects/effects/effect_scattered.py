import argparse
import random

from terminaltexteffects.utils import motion, graphics
import terminaltexteffects.utils.argtypes as argtypes
import terminaltexteffects.utils.terminal as terminal
from terminaltexteffects.base_character import EffectCharacter, EventHandler


def add_arguments(subparsers: argparse._SubParsersAction) -> None:
    """Adds arguments to the subparser.

    Args:
        subparser (argparse._SubParsersAction): subparser to add arguments to
    """
    effect_parser = subparsers.add_parser(
        "scattered",
        formatter_class=argtypes.CustomFormatter,
        help="Move the characters into place from random starting locations.",
        description="scattered | Move the characters into place from random starting locations.",
        epilog=f"""{argtypes.EASING_EPILOG}
        
Example: terminaltexteffects scattered --movement-speed 0.5 --easing IN_OUT_BACK""",
    )
    effect_parser.set_defaults(effect_class=ScatteredEffect)
    effect_parser.add_argument(
        "-a",
        "--animation-rate",
        type=argtypes.nonnegative_float,
        default=0.01,
        help="Time between animation steps.",
    )
    effect_parser.add_argument(
        "--gradient-stops",
        type=argtypes.color,
        nargs="*",
        default=[],
        metavar="(XTerm [0-255] OR RGB Hex [000000-ffffff])",
        help="Space separated, unquoted, list of colors for the character gradient. If only one color is provided, the characters will be displayed in that color.",
    )
    effect_parser.add_argument(
        "--gradient-steps",
        type=argtypes.positive_int,
        default=10,
        metavar="(int > 0)",
        help="Number of gradient steps to use. More steps will create a smoother and longer gradient animation.",
    )
    effect_parser.add_argument(
        "--gradient-frames",
        type=argtypes.positive_int,
        default=5,
        metavar="(int > 0)",
        help="Number of frames to display each gradient step.",
    )
    effect_parser.add_argument(
        "--movement-speed",
        type=argtypes.positive_float,
        default=0.5,
        metavar="(float > 0)",
        help="Movement speed of the characters. Note: Speed effects the number of steps in the easing function. Adjust speed and animation rate separately to fine tune the effect.",
    )
    effect_parser.add_argument(
        "--easing",
        default="IN_OUT_BACK",
        type=argtypes.ease,
        help="Easing function to use for character movement.",
    )


class ScatteredEffect:
    """Effect that moves the characters into position from random starting locations."""

    def __init__(self, terminal: terminal.Terminal, args: argparse.Namespace):
        self.terminal = terminal
        self.args = args
        self.pending_chars: list[EffectCharacter] = []
        self.active_chars: list[EffectCharacter] = []
        self.gradient_stops: list[int | str] = self.args.gradient_stops

    def prepare_data(self) -> None:
        """Prepares the data for the effect by scattering the characters within range of the input width and height."""
        if len(self.gradient_stops) > 1:
            gradient = graphics.Gradient(self.gradient_stops, self.args.gradient_steps)

        for character in self.terminal.characters:
            if self.terminal.output_area.right < 2 or self.terminal.output_area.top < 2:
                character.motion.set_coordinate(motion.Coord(1, 1))
            else:
                character.motion.set_coordinate(self.terminal.output_area.random_coord())
            input_coord_path = character.motion.new_path(speed=self.args.movement_speed, ease=self.args.easing)
            input_coord_path.new_waypoint(character.input_coord)
            character.event_handler.register_event(
                EventHandler.Event.PATH_ACTIVATED, input_coord_path, EventHandler.Action.SET_LAYER, 1
            )
            character.event_handler.register_event(
                EventHandler.Event.PATH_COMPLETE, input_coord_path, EventHandler.Action.SET_LAYER, 0
            )
            character.motion.activate_path(input_coord_path)
            character.is_visible = True
            if self.gradient_stops:
                gradient_scn = character.animation.new_scene()
                if len(self.gradient_stops) > 1:
                    for step in gradient:
                        gradient_scn.add_frame(character.input_symbol, self.args.gradient_frames, color=step)
                else:
                    gradient_scn.add_frame(character.input_symbol, 1, color=self.gradient_stops[0])
                character.animation.activate_scene(gradient_scn)
            self.active_chars.append(character)

    def run(self) -> None:
        """Runs the effect."""
        self.prepare_data()
        self.terminal.print()
        while self.pending_chars or self.active_chars:
            self.animate_chars()
            self.active_chars = [character for character in self.active_chars if character.is_active()]
            self.terminal.print()

    def animate_chars(self) -> None:
        for character in self.active_chars:
            character.tick()
