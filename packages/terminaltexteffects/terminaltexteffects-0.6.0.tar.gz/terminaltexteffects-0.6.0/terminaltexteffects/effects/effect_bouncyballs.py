import argparse
import random

import terminaltexteffects.utils.argtypes as argtypes
from terminaltexteffects.utils import graphics, motion
from terminaltexteffects.base_character import EffectCharacter, EventHandler
from terminaltexteffects.utils.terminal import Terminal


def add_arguments(subparsers: argparse._SubParsersAction) -> None:
    """Adds arguments to the subparser.

    Args:
        subparser (argparse._SubParsersAction): subparser to add arguments to
    """
    effect_parser = subparsers.add_parser(
        "bouncyballs",
        formatter_class=argtypes.CustomFormatter,
        help="Characters are bouncy balls falling from the top of the output area.",
        description="bouncyball | Characters are bouncy balls falling from the top of the output area.",
        epilog=f"""{argtypes.EASING_EPILOG}
        
Example: terminaltexteffects bouncyball -a 0.01 --ball-colors 00ff00 ff0000 0000ff --final-color ffffff --ball-delay 15 --movement-speed 0.25 --easing OUT_BOUNCE""",
    )
    effect_parser.set_defaults(effect_class=BouncyBallsEffect)
    effect_parser.add_argument(
        "-a",
        "--animation-rate",
        type=argtypes.nonnegative_float,
        default=0.01,
        help="Time between animation steps. ",
    )
    effect_parser.add_argument(
        "--ball-colors",
        type=argtypes.color,
        nargs="*",
        default=0,
        metavar="(XTerm [0-255] OR RGB Hex [000000-ffffff])",
        help="Space separated list of colors from which ball colors will be randomly selected. If no colors are provided, the colors are random.",
    )
    effect_parser.add_argument(
        "--final-color",
        type=argtypes.color,
        default="ffffff",
        metavar="(XTerm [0-255] OR RGB Hex [000000-ffffff])",
        help="Color for the final character.",
    )
    effect_parser.add_argument(
        "--ball-delay",
        type=argtypes.positive_int,
        default=15,
        metavar="(int > 0)",
        help="Number of animation steps between ball drops, increase to reduce ball drop rate.",
    ),
    effect_parser.add_argument(
        "--movement-speed",
        type=argtypes.positive_float,
        default=0.25,
        metavar="(float > 0)",
        help="Movement speed of the characters. Note: Speed effects the number of steps in the easing function. Adjust speed and animation rate separately to fine tune the effect.",
    )
    effect_parser.add_argument(
        "--easing",
        default="OUT_BOUNCE",
        type=argtypes.ease,
        help="Easing function to use for character movement.",
    )


class BouncyBallsEffect:
    """Effect that displays the text as bouncy balls falling from the top of the output area."""

    def __init__(self, terminal: Terminal, args: argparse.Namespace):
        self.terminal = terminal
        self.args = args
        self.pending_chars: list[EffectCharacter] = []
        self.active_chars: list[EffectCharacter] = []
        self.group_by_row: dict[int, list[EffectCharacter | None]] = {}

    def prepare_data(self) -> None:
        """Prepares the data for the effect by assigning colors and waypoints and
        organizing the characters by row."""
        ball_symbols = ("*", "o", "O", "0", ".")
        for character in self.terminal.characters:
            character.is_visible = False
            if self.args.ball_colors:
                color = random.choice(self.args.ball_colors)
            else:
                color = graphics.Animation.random_color()
            symbol = random.choice(ball_symbols)
            ball_scene = character.animation.new_scene()
            ball_scene.add_frame(symbol, 1, color=color)
            final_scene = character.animation.new_scene()
            for step in graphics.Gradient([color, self.args.final_color], 12):
                final_scene.add_frame(
                    character.input_symbol,
                    10,
                    color=step,
                )
            character.motion.set_coordinate(motion.Coord(character.input_coord.column, self.terminal.output_area.top))
            input_coord_path = character.motion.new_path(speed=self.args.movement_speed, ease=self.args.easing)
            input_coord_path.new_waypoint(character.input_coord)
            character.motion.activate_path(input_coord_path)
            character.animation.activate_scene(ball_scene)
            character.event_handler.register_event(
                character.event_handler.Event.PATH_COMPLETE,
                input_coord_path,
                character.event_handler.Action.ACTIVATE_SCENE,
                final_scene,
            )
            self.pending_chars.append(character)
        for character in sorted(self.pending_chars, key=lambda c: c.input_coord.row):
            if character.input_coord.row not in self.group_by_row:
                self.group_by_row[character.input_coord.row] = []
            self.group_by_row[character.input_coord.row].append(character)

    def run(self) -> None:
        """Runs the effect."""
        self.prepare_data()
        self.pending_chars.clear()
        ball_delay = 0
        while self.group_by_row or self.active_chars or self.pending_chars:
            if not self.pending_chars and self.group_by_row:
                self.pending_chars.extend(self.group_by_row.pop(min(self.group_by_row.keys())))  # type: ignore
            if self.pending_chars and ball_delay == 0:
                for _ in range(random.randint(1, 5)):
                    if self.pending_chars:
                        next_character = self.pending_chars.pop(random.randint(0, len(self.pending_chars) - 1))
                        next_character.is_visible = True
                        self.active_chars.append(next_character)
                    else:
                        break
                ball_delay = self.args.ball_delay
            ball_delay -= 1
            self.animate_chars()
            self.active_chars = [character for character in self.active_chars if character.is_active()]
            self.terminal.print()

    def animate_chars(self) -> None:
        """Animates the characters by calling the tick method."""
        for character in self.active_chars:
            character.tick()
