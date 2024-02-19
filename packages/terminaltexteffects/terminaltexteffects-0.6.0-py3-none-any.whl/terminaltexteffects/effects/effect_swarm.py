import argparse
import random

import terminaltexteffects.utils.argtypes as argtypes
from terminaltexteffects.base_character import EffectCharacter, EventHandler
from terminaltexteffects.utils.terminal import Terminal
from terminaltexteffects.utils import graphics, motion, argtypes, easing


def add_arguments(subparsers: argparse._SubParsersAction) -> None:
    """Adds arguments to the subparser.

    Args:
        subparser (argparse._SubParsersAction): subparser to add arguments to
    """
    effect_parser = subparsers.add_parser(
        "swarm",
        formatter_class=argtypes.CustomFormatter,
        help="Characters are grouped into swarms and move around the terminal before settling into position.",
        description="Characters are grouped into swarms and move around the terminal before settling into position.",
        epilog=f"""Example: terminaltexteffects swarm -a 0.01 --base-color 0f74fa --flash-color f2ea79 --final-color 96ed89 --swarm-size 5 --swarm-coordination 80""",
    )
    effect_parser.set_defaults(effect_class=SwarmEffect)
    effect_parser.add_argument(
        "-a",
        "--animation-rate",
        type=argtypes.nonnegative_float,
        default=0.01,
        help="Minimum time, in seconds, between animation steps. This value does not normally need to be modified. Use this to increase the playback speed of all aspects of the effect. This will have no impact beyond a certain lower threshold due to the processing speed of your device.",
    )
    effect_parser.add_argument(
        "--base-color",
        type=argtypes.color,
        default="0f74fa",
        metavar="(XTerm [0-255] OR RGB Hex [000000-ffffff])",
        help="Color for the characters when not flashing.",
    )
    effect_parser.add_argument(
        "--flash-color",
        type=argtypes.color,
        default="f2ea79",
        metavar="(XTerm [0-255] OR RGB Hex [000000-ffffff])",
        help="Color for the character flash. Characters flash when moving.",
    )
    effect_parser.add_argument(
        "--final-color",
        type=argtypes.color,
        default="96ed89",
        metavar="(XTerm [0-255] OR RGB Hex [000000-ffffff])",
        help="Color for the characters when they reach their input coordinate.",
    )
    effect_parser.add_argument(
        "--swarm-size",
        type=argtypes.float_zero_to_one,
        metavar="(float 0 < n <= 1)",
        default=0.05,
        help="Percent of total characters in each swarm.",
    )
    effect_parser.add_argument(
        "--swarm-coordination",
        type=argtypes.float_zero_to_one,
        metavar="(float 0 < n <= 1)",
        default=0.80,
        help="Percent of characters in a swarm that move as a group.",
    )


class SwarmEffect:
    """Characters behave with swarm characteristics before flying into position."""

    def __init__(self, terminal: Terminal, args: argparse.Namespace):
        self.terminal = terminal
        self.args = args
        self.pending_chars: list[EffectCharacter] = []
        self.active_chars: list[EffectCharacter] = []
        self.swarms: list[list[EffectCharacter]] = []
        self.swarm_size: int = max(round(len(self.terminal.characters) * self.args.swarm_size), 1)

    def make_swarms(self) -> None:
        unswarmed_characters = list(self.terminal.characters[::-1])
        while unswarmed_characters:
            new_swarm: list[EffectCharacter] = []
            for _ in range(self.swarm_size):
                if unswarmed_characters:
                    new_swarm.append(unswarmed_characters.pop())
                else:
                    break
            self.swarms.append(new_swarm)

    def prepare_data(self) -> None:
        """Prepares the data for the effect by creating swarms of characters and setting waypoints and animations."""
        self.make_swarms()
        final_gradient = graphics.Gradient([self.args.base_color, self.args.final_color], 10)
        swarm_gradient = graphics.Gradient([self.args.base_color, self.args.flash_color], 7)
        flash_list = [self.args.flash_color for _ in range(10)]
        swarm_gradient_mirror = list(swarm_gradient) + flash_list + list(swarm_gradient)[::-1]
        for swarm in self.swarms:
            swarm_area_coordinate_map: dict[motion.Coord, list[motion.Coord]] = {}
            swarm_spawn = self.terminal.output_area.random_coord(outside_scope=True)
            swarm_areas: list[motion.Coord] = []
            swarm_area_count = random.randint(2, 4)
            # create areas where characters will swarm
            while len(swarm_areas) < swarm_area_count:
                # get random coord within inner 90% of terminal
                col = random.randint(round(self.terminal.input_width * 0.1), round(self.terminal.input_width * 0.9) + 1)
                row = random.randint(
                    round(self.terminal.output_area.top * 0.1), round(self.terminal.output_area.top * 0.9) + 1
                )
                area = motion.Coord(col, row)
                if area not in swarm_areas:
                    swarm_areas.append(area)
                    # swarm area radius is a function of the terminal size, approximately 1/4 of the smallest dimension
                    swarm_area_coordinate_map[area] = motion.Motion.find_coords_in_circle(
                        area, max(min(self.terminal.output_area.right, self.terminal.output_area.top) // 6, 1)
                    )

            # assign characters waypoints for swarm areas and inner waypoints within the swarm areas
            for character in swarm:
                swarm_area_count = 0
                character.motion.set_coordinate(swarm_spawn)
                flash_scn = character.animation.new_scene(sync=graphics.SyncMetric.DISTANCE)
                for step in swarm_gradient_mirror:
                    flash_scn.add_frame(character.input_symbol, 1, color=step)
                for _, swarm_area_coords in swarm_area_coordinate_map.items():
                    swarm_area_name = f"{swarm_area_count}_swarm_area"
                    swarm_area_count += 1
                    origin_path = character.motion.new_path(id=swarm_area_name, speed=0.25, ease=easing.out_sine)
                    origin_path.new_waypoint(random.choice(swarm_area_coords), id=swarm_area_name)
                    character.event_handler.register_event(
                        EventHandler.Event.PATH_ACTIVATED, origin_path, EventHandler.Action.ACTIVATE_SCENE, flash_scn
                    )
                    character.event_handler.register_event(
                        EventHandler.Event.PATH_ACTIVATED, origin_path, EventHandler.Action.SET_LAYER, 1
                    )
                    character.event_handler.register_event(
                        EventHandler.Event.PATH_COMPLETE,
                        origin_path,
                        EventHandler.Action.DEACTIVATE_SCENE,
                        flash_scn,
                    )
                    inner_paths = 0
                    total_inner_paths = 2
                    while inner_paths < total_inner_paths:
                        next_coord = random.choice(swarm_area_coords)
                        inner_paths += 1
                        inner_path = character.motion.new_path(
                            id=str(len(character.motion.paths)), speed=0.1, ease=easing.in_out_sine
                        )
                        inner_path.new_waypoint(next_coord, id=str(len(character.motion.paths)))
                # create landing waypoint and scene
                input_path = character.motion.new_path(speed=0.3, ease=easing.in_out_quad)
                input_path.new_waypoint(character.input_coord)
                input_scn = character.animation.new_scene()
                for step in final_gradient:
                    input_scn.add_frame(character.input_symbol, 3, color=step)
                character.event_handler.register_event(
                    EventHandler.Event.PATH_COMPLETE, input_path, EventHandler.Action.ACTIVATE_SCENE, input_scn
                )
                character.event_handler.register_event(
                    EventHandler.Event.PATH_COMPLETE, input_path, EventHandler.Action.SET_LAYER, 0
                )
                character.event_handler.register_event(
                    EventHandler.Event.PATH_ACTIVATED, input_path, EventHandler.Action.ACTIVATE_SCENE, flash_scn
                )
                character.motion.chain_paths(list(character.motion.paths.values()))

    def run(self) -> None:
        """Runs the effect."""
        self.prepare_data()
        call_next = True
        active_swarm_area = "0_swarm_area"
        while self.swarms or self.active_chars:
            if self.swarms and call_next:
                call_next = False
                current_swarm = self.swarms.pop()
                active_swarm_area = "0_swarm_area"
                for character in current_swarm:
                    character.motion.activate_path(character.motion.query_path("0_swarm_area"))
                    character.is_visible = True
                    self.active_chars.append(character)
            self.terminal.print()
            self.animate_chars()
            if len(self.active_chars) < len(current_swarm):
                call_next = True
            if current_swarm:
                for character in current_swarm:
                    if (
                        character.motion.active_path
                        and character.motion.active_path.path_id != active_swarm_area
                        and "swarm_area" in character.motion.active_path.path_id
                        and int(character.motion.active_path.path_id[0]) > int(active_swarm_area[0])
                    ):
                        active_swarm_area = character.motion.active_path.path_id
                        for other in current_swarm:
                            if other is not character and random.random() < self.args.swarm_coordination:
                                other.motion.activate_path(other.motion.paths[active_swarm_area])
                        break

            self.active_chars = [character for character in self.active_chars if character.is_active()]

    def animate_chars(self) -> None:
        """Animates the characters by calling the tick method."""
        for character in self.active_chars:
            character.tick()
