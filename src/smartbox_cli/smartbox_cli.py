from smartbox.sb_tracker import SmartBoxTracker
import curses


tracker = SmartBoxTracker()

def display_help(stdscr):
	help_message = ""
	for key, descr in KEY_BINDINGS:
		help_message += "{}: {}\n".format(key, descr)
	stdscr.addstr(0, 0, help_message)

def display_info(stdscr):
	ew_position = tracker.get_ew_position()
	ew_angle = tracker.get_ew_angle()
	ns_position = tracker.get_ns_position()
	ns_angle = tracker.get_ns_angle()

	ns_moving = "MOVING" if tracker.is_ns_moving() else ""
	ew_moving = "MOVING" if tracker.is_ew_moving() else ""

	stdscr.addstr(15, 0, "NS position: {}\tangle: {}\t{}".format(ns_position, ns_angle, ns_moving))
	stdscr.addstr(16, 0, "EW position: {}\tangle: {}\t{}".format(ew_position, ew_angle, ew_moving))

def handle_key(stdscr, key_press):
	stdscr.addstr(0, 70, key_press)
	stdscr.refresh()
	if key_press in FUNCTION_BINDINGS:
		FUNCTION_BINDINGS[key_press](stdscr)

def move_north(stdscr):
	stdscr.addstr(0, 70, "North")
	stdscr.refresh()
	tracker.move_north()

def move_south(stdscr):
	stdscr.addstr(0, 70, "South")
	stdscr.refresh()
	tracker.move_south()

def move_east(stdscr):
	stdscr.addstr(0, 70, "East")
	stdscr.refresh()
	tracker.move_east()

def move_west(stdscr):
	stdscr.addstr(0, 70, "West")
	stdscr.refresh()
	tracker.move_west()

def stop(stdscr):
	stdscr.addstr(0, 70, "Stop")
	stdscr.refresh()
	tracker.stop()

def get_float_input(stdscr):
	stdscr.addstr(25, 0, " " * 80)
	stdscr.refresh()
	curses.echo()
	user_input = stdscr.getstr(25, 0, 15)
	while True:
		try:
			value = float(user_input)
			curses.noecho()
			return value
		except ValueError:
			stdscr.addstr(15, 0, "Invalid input, must be convertible to a numerical value")
			stdscr.refresh()

def move_to_linear_position(stdscr):
	stdscr.addstr(24, 0, "Please type the NS linear position (0 - 6 inches)")
	stdscr.refresh()
	ns_pos = get_float_input(stdscr)

	stdscr.addstr(24, 0, "Please type the EW linear position (0 - 12 inches)")
	stdscr.refresh()
	ew_pos = get_float_input(stdscr)
	stdscr.addstr(24, 0, " " * 80)
	stdscr.addstr(25, 0, " " * 80)
	stdscr.addstr(5, 70, str(ns_pos))
	stdscr.addstr(6, 70, str(ew_pos))
	stdscr.refresh()
	tracker.move_to_linear_position(ns_pos, ew_pos)


def move_to_angular_position(stdscr):
	stdscr.addstr(24, 0, "Please type the NS angular position (0 - 180)")
	stdscr.refresh()
	ns_pos = get_float_input(stdscr)


	stdscr.addstr(24, 0, "Please type the EW angular position (0 - 180)")
	stdscr.refresh()
	ew_pos = get_float_input(stdscr)
	stdscr.addstr(24, 0, " " * 80)
	stdscr.addstr(25, 0, " " * 80)
	stdscr.addstr(5, 70, str(ns_pos))
	stdscr.addstr(6, 70, str(ew_pos))
	stdscr.refresh()
	tracker.move_to_angular_position(ns_pos, ew_pos)

def draw_screen(stdscr):
	stdscr.clear()
	stdscr.erase()
	display_help(stdscr)
	display_info(stdscr)
	stdscr.refresh()

def get_key(stdscr):
	try:
		return stdscr.getkey()
	except:
		return "None"

def main(stdscr):
	curses.halfdelay(1)
	draw_screen(stdscr)
	key_press = get_key(stdscr)
	while key_press != "q":
		draw_screen(stdscr)
		handle_key(stdscr, key_press)
		key_press = get_key(stdscr)

KEY_BINDINGS = [
	["q", "Quit"],
	["n or up arrow", "Move panel north"],
	["s or down arrow", "Move panel south"],
	["e or right arrow", "Move panel east"],
	["w or left arrow", "Move panel west"],
	["p", "Move panel actuators to linear position"],
	["a", "Move panel to angular position"],
]

FUNCTION_BINDINGS = {
	"n": move_north,
	"s": move_south,
	"e": move_east,
	"w": move_west,
	"KEY_UP": move_north,
	"KEY_DOWN": move_south,
	"KEY_RIGHT": move_east,
	"KEY_LEFT": move_west,
	"p": move_to_linear_position,
	"a": move_to_angular_position,
	" ": stop
}

if __name__ == "__main__":
	curses.wrapper(main)
