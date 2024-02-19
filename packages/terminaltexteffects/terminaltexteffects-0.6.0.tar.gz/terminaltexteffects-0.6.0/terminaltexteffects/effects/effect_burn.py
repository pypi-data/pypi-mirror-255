import argparse
import random

import terminaltexteffects.utils.argtypes as argtypes
from terminaltexteffects.base_character import EffectCharacter
from terminaltexteffects.utils.terminal import Terminal
from terminaltexteffects.utils import graphics, argtypes


def add_arguments(subparsers: argparse._SubParsersAction) -> None:
    """Adds arguments to the subparser.

    Args:
        subparser (argparse._SubParsersAction): subparser to add arguments to
    """
    effect_parser = subparsers.add_parser(
        "burn",
        help="Burns vertically in the output area.",
        description="burn | Burn the output area.",
        epilog="Example: terminaltexteffects burn -a 0.003 --flame-color ff9600 --burned-color 252525",
    )
    effect_parser.set_defaults(effect_class=BurnEffect)
    effect_parser.add_argument(
        "-a",
        "--animation-rate",
        type=argtypes.nonnegative_float,
        default=0.003,
        help="Time between animation steps. Defaults to 0.03 seconds.",
    )
    effect_parser.add_argument(
        "--burned-color",
        type=argtypes.color,
        default="252525",
        metavar="(XTerm [0-255] OR RGB Hex [000000-ffffff])",
        help="Color faded toward as blocks burn. Defaults to 252525",
    )
    effect_parser.add_argument(
        "--flame-color",
        type=argtypes.color,
        default="ff9600",
        metavar="(XTerm [0-255] OR RGB Hex [000000-ffffff])",
        help="Color for the flame. Defaults to 0",
    )
    effect_parser.add_argument(
        "--final-color",
        type=argtypes.color,
        metavar="(XTerm [0-255] OR RGB Hex [000000-ffffff])",
        help="Color for the final character. Will leave as system default if not provided.",
    )


class BurnEffect:
    """Effect that burns up the screen."""

    def __init__(self, terminal: Terminal, args: argparse.Namespace):
        self.terminal = terminal
        self.args = args
        self.pending_chars: list[EffectCharacter] = []
        self.active_chars: list[EffectCharacter] = []

    def prepare_data(self) -> None:
        """Prepares the data for the effect by building the burn animation and organizing the data into columns."""
        vertical_build_order = [
            ".",
            "▖",
            "▄",
            "▙",
            "█",
            "▜",
            "▀",
        ]
        fire_gradient = graphics.Gradient(["ffffff", self.args.flame_color], 12)
        burned_gradient = graphics.Gradient([self.args.flame_color, self.args.burned_color], 7)
        groups = {
            column_index: column
            for column_index, column in enumerate(
                self.terminal.get_characters(sort_order=self.terminal.CharacterSort.COLUMN_LEFT_TO_RIGHT)
            )
        }
        for column in groups.values():
            column.reverse()

        def groups_remaining(rows) -> bool:
            return any(row for row in rows.values())

        while groups_remaining(groups):
            keys = [key for key in groups.keys() if groups[key]]
            next_char = groups[random.choice(keys)].pop(0)
            next_char.is_visible = False
            construct_scn = next_char.animation.new_scene()
            g_start = 0
            for _, block in enumerate(vertical_build_order[:5]):
                for color in fire_gradient.spectrum[g_start : g_start + 3]:
                    construct_scn.add_frame(block, 30, color=color)
                g_start += 2

            g_start = 0
            for _, block in enumerate(vertical_build_order[4:]):
                for color in burned_gradient.spectrum[g_start : g_start + 3]:
                    construct_scn.add_frame(block, 30, color=color)
                g_start += 2

            construct_scn.add_frame(next_char.input_symbol, 1, color=self.args.final_color)
            next_char.animation.activate_scene(construct_scn)
            self.pending_chars.append(next_char)

    def run(self) -> None:
        """Runs the effect."""
        self.prepare_data()
        while self.pending_chars or self.active_chars:
            if self.pending_chars:
                next_char = self.pending_chars.pop(0)
                next_char.is_visible = True
                self.active_chars.append(next_char)

            self.animate_chars()

            self.active_chars = [character for character in self.active_chars if character.is_active()]
            self.terminal.print()

    def animate_chars(self) -> None:
        """Animates the characters by calling the tick method."""
        for character in self.active_chars:
            character.animation.step_animation()
