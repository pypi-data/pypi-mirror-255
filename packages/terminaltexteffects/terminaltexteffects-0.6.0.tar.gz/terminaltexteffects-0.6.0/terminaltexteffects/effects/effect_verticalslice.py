import argparse

from terminaltexteffects.utils import argtypes, motion
from terminaltexteffects.base_character import EffectCharacter
from terminaltexteffects.utils.terminal import Terminal


def add_arguments(subparsers: argparse._SubParsersAction) -> None:
    """Adds arguments to the subparser.

    Args:
        subparser (argparse._SubParsersAction): subparser to add arguments to
    """
    effect_parser = subparsers.add_parser(
        "verticalslice",
        formatter_class=argtypes.CustomFormatter,
        help="Slices the input in half vertically and slides it into place from opposite directions.",
        description="verticalslice | Slices the input in half vertically and slides it into place from opposite directions.",
        epilog=f"""{argtypes.EASING_EPILOG}
        
Example: terminaltexteffects verticalslice -a 0.02""",
    )
    effect_parser.set_defaults(effect_class=VerticalSlice)
    effect_parser.add_argument(
        "-a",
        "--animation-rate",
        type=argtypes.nonnegative_float,
        default=0.02,
        help="Minimum time, in seconds, between animation steps. This value does not normally need to be modified. Use this to increase the playback speed of all aspects of the effect. This will have no impact beyond a certain lower threshold due to the processing speed of your device.",
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
        default="IN_OUT_EXPO",
        type=argtypes.ease,
        help="Easing function to use for character movement.",
    )


class VerticalSlice:
    """Effect that slices the input in half vertically and slides it into place from opposite directions."""

    def __init__(self, terminal: Terminal, args: argparse.Namespace):
        self.terminal = terminal
        self.args = args
        self.pending_chars: list[EffectCharacter] = []
        self.active_chars: list[EffectCharacter] = []
        self.new_rows: list[list[EffectCharacter]] = []

    def prepare_data(self) -> None:
        """Prepares the data for the effect by setting the left half to start at the top and the
        right half to start at the bottom, and creating rows consisting off halves from opposite
        input rows."""

        self.rows = self.terminal.get_characters(sort_order=self.terminal.CharacterSort.ROW_BOTTOM_TO_TOP)
        lengths = [max([c.input_coord.column for c in row]) for row in self.rows]
        mid_point = sum(lengths) // len(lengths) // 2
        for row_index, row in enumerate(self.rows):
            new_row = []
            left_half = [character for character in row if character.input_coord.column <= mid_point]
            for character in left_half:
                character.motion.set_coordinate(
                    motion.Coord(character.input_coord.column, self.terminal.output_area.top)
                )
                input_coord_path = character.motion.new_path(speed=self.args.movement_speed, ease=self.args.easing)
                input_coord_path.new_waypoint(character.input_coord)
                character.motion.activate_path(input_coord_path)
            opposite_row = self.rows[-(row_index + 1)]
            right_half = [c for c in opposite_row if c.input_coord.column > mid_point]
            for character in right_half:
                character.motion.set_coordinate(
                    motion.Coord(character.input_coord.column, self.terminal.output_area.bottom)
                )
                input_coord_path = character.motion.new_path(speed=self.args.movement_speed, ease=self.args.easing)
                input_coord_path.new_waypoint(character.input_coord)
                character.motion.activate_path(input_coord_path)
            new_row.extend(left_half)
            new_row.extend(right_half)
            self.new_rows.append(new_row)

    def run(self) -> None:
        """Runs the effect."""
        self.prepare_data()
        while self.new_rows or self.active_chars:
            if self.new_rows:
                next_row = self.new_rows.pop(0)
                for character in next_row:
                    character.is_visible = True
                self.active_chars.extend(next_row)
            self.animate_chars()
            self.terminal.print()
            self.active_chars = [character for character in self.active_chars if character.is_active()]

    def animate_chars(self) -> None:
        """Animates the characters by calling the move method and printing the characters to the terminal."""
        for character in self.active_chars:
            character.tick()
