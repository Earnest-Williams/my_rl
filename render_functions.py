import libtcodpy as libtcod
from enum import Enum
from game_states import GameStates
from menus import character_screen, inventory_menu, level_up_menu, debug_menu
import logging

# Set up logging
logging.basicConfig(
    filename="render_functions.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class RenderOrder(Enum):
    STAIRS = 1
    CORPSE = 2
    ITEM = 3
    ACTOR = 4


def get_color(color):
    logging.debug(f"get_color called with: {color}")
    if isinstance(color, (tuple, list)):
        if len(color) == 3:
            return libtcod.Color(*color)
        elif len(color) == 4:
            logging.warning(
                f"RGBA color {color} passed to get_color. This should be blended first."
            )
            return blend_colors(libtcod.white, color)  # Blend with white as default
    elif isinstance(color, libtcod.Color):
        return color
    logging.warning(f"Invalid color format: {color}. Using white as default.")
    return libtcod.white  # Default color


def blend_colors(base_color, overlay_color):
    logging.debug(
        f"blend_colors called with base_color: {base_color}, overlay_color: {overlay_color}"
    )
    if not isinstance(base_color, libtcod.Color):
        logging.error(f"Invalid base_color: {base_color}. Must be libtcod.Color.")
        base_color = libtcod.white

    if not isinstance(overlay_color, (tuple, list)) or len(overlay_color) != 4:
        logging.error(f"Invalid overlay_color: {overlay_color}. Must be RGBA tuple.")
        return base_color

    try:
        alpha = overlay_color[3] / 255.0
        r = int(base_color.r * (1 - alpha) + overlay_color[0] * alpha)
        g = int(base_color.g * (1 - alpha) + overlay_color[1] * alpha)
        b = int(base_color.b * (1 - alpha) + overlay_color[2] * alpha)
        blended_color = libtcod.Color(r, g, b)
        logging.debug(f"Blended color result: {blended_color}")
        return blended_color
    except Exception as e:
        logging.error(f"Error blending colors: {e}")
        return base_color


def apply_color(console, x, y, color):
    logging.debug(f"apply_color called at ({x}, {y}) with color: {color}")
    try:
        if isinstance(color, tuple) and len(color) == 4:
            base_color = libtcod.console_get_char_background(console, x, y)
            blended = blend_colors(base_color, color)
        else:
            blended = get_color(color)

        if not isinstance(blended, libtcod.Color):
            logging.error(f"Invalid blended color: {blended}. Must be libtcod.Color.")
            blended = libtcod.white

        libtcod.console_set_char_background(console, x, y, blended, libtcod.BKGND_SET)
    except Exception as e:
        logging.error(f"Error applying color at ({x}, {y}): {e}")


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)
    logging.debug(f"get_names_under_mouse called at ({x}, {y})")

    names = [
        entity.name
        for entity in entities
        if entity.x == x
        and entity.y == y
        and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)
    ]
    names = ", ".join(names)

    logging.debug(f"Names under mouse: {names}")
    return names.capitalize()


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    logging.debug(f"render_bar called for {name}: {value}/{maximum}")
    try:
        bar_width = int(float(value) / maximum * total_width)

        libtcod.console_set_default_background(panel, get_color(back_color))
        libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

        libtcod.console_set_default_background(panel, get_color(bar_color))
        if bar_width > 0:
            libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

        libtcod.console_set_default_foreground(panel, libtcod.white)
        libtcod.console_print_ex(
            panel,
            int(x + total_width / 2),
            y,
            libtcod.BKGND_NONE,
            libtcod.CENTER,
            f"{name}: {value}/{maximum}",
        )
    except Exception as e:
        logging.error(f"Error rendering bar: {e}")


def render_all(
    con,
    panel,
    entities,
    player,
    game_map,
    fov_map,
    fov_recompute,
    message_log,
    screen_width,
    screen_height,
    bar_width,
    panel_height,
    panel_y,
    mouse,
    colors,
    game_state,
    constants,
):
    logging.debug(
        f"render_all called. fov_recompute: {fov_recompute}, game_state: {game_state}"
    )
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                try:
                    if visible:
                        if wall:
                            apply_color(con, x, y, colors.get("wall_base"))
                        else:
                            apply_color(con, x, y, colors.get("floor_base"))
                        apply_color(con, x, y, colors.get("light_overlay"))
                        game_map.tiles[x][y].explored = True
                    elif game_map.tiles[x][y].explored:
                        if wall:
                            apply_color(con, x, y, colors.get("wall_base"))
                        else:
                            apply_color(con, x, y, colors.get("floor_base"))
                        apply_color(con, x, y, colors.get("dark_overlay"))
                except Exception as e:
                    logging.error(f"Error rendering tile at ({x}, {y}): {e}")

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map, game_map)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(
            panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text
        )
        y += 1

    render_bar(
        panel,
        1,
        1,
        bar_width,
        "HP",
        player.fighter.hp,
        player.fighter.max_hp,
        libtcod.light_red,
        libtcod.darker_red,
    )
    libtcod.console_print_ex(
        panel,
        1,
        3,
        libtcod.BKGND_NONE,
        libtcod.LEFT,
        f"Dungeon level: {game_map.dungeon_level}",
    )

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(
        panel,
        1,
        0,
        libtcod.BKGND_NONE,
        libtcod.LEFT,
        get_names_under_mouse(mouse, entities, fov_map),
    )

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = (
                "Press the key next to an item to use it, or Esc to cancel.\n"
            )
        else:
            inventory_title = (
                "Press the key next to an item to drop it, or Esc to cancel.\n"
            )

        inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)

    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(
            con,
            "Level up! Choose a stat to raise:",
            player,
            40,
            screen_width,
            screen_height,
        )

    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)

    elif game_state == GameStates.DEBUG_MENU:
        debug_options = [
            f'FOV Algorithm: {constants["fov_algorithm"]}',
            "Heal Player",
            "Kill All Monsters",
            "Add Experience",
            "Toggle God Mode",
            "Reveal Map",
        ]
        debug_menu(con, "Debug Menu", debug_options, 30, screen_width, screen_height)


def clear_all(con, entities):
    logging.debug(f"clear_all called for {len(entities)} entities")
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map, game_map):
    logging.debug(f"draw_entity called for {entity.name} at ({entity.x}, {entity.y})")
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or (
        entity.stairs and game_map.tiles[entity.x][entity.y].explored
    ):
        try:
            libtcod.console_set_default_foreground(con, entity.color)
            libtcod.console_put_char(
                con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE
            )
        except Exception as e:
            logging.error(
                f"Error drawing entity {entity.name} at ({entity.x}, {entity.y}): {e}"
            )


def clear_entity(con, entity):
    logging.debug(f"clear_entity called for {entity.name} at ({entity.x}, {entity.y})")
    try:
        libtcod.console_put_char(con, entity.x, entity.y, " ", libtcod.BKGND_NONE)
    except Exception as e:
        logging.error(f"Error clearing entity at ({entity.x}, {entity.y}): {e}")
