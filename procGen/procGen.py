# Script for proect configuration of simple rectangles

import random
import argparse
from collections import namedtuple
import matplotlib.pyplot as plt

# Named tuples so our code is more readable
Size = namedtuple("Size", ["width", "height"])
Coordinate = namedtuple("Coordinate", ["x", "y"])

# Default values
DEFAULT_MAP_SIZE = Size(100, 100)  # Size of the map
DEFAULT_DENSITY = 0.8  # Density of the rectangles around the middle of the map


def generate_rectangles(
    map: dict[Coordinate, int], size: Size, density: float
) -> dict[Coordinate, int]:
    """
    Generate rectangles in the map. Returns the map with the rectangles.
    """

    # Generate a rectangle in the middle of the map
    middle = Coordinate(size.width // 2, size.height // 2)

    num_rectangulars = int(size.width * size.height * density)
    # based on density, we calculate a circle radius and generate rectangles around the middle, within the
    # circle radius
    circle_radius = int((size.width + size.height) / (4 * density)) // 4

    print(circle_radius, num_rectangulars)
    for i in range(num_rectangulars):
        x = random.randint(0, size.width - 1)
        y = random.randint(0, size.height - 1)

        if (x - middle.x) ** 2 + (y - middle.y) ** 2 < circle_radius**2:
            map[Coordinate(x, y)] = 1

    return map


def generate_buildings(
    size: Size, density: float, limit_count: int = 1000
) -> set[tuple[Coordinate, Coordinate]]:

    # interpret density as the number of buildings
    epsilon = 0
    max_buildings = (size.width) + epsilon

    num_buildings = int(max_buildings * density)  # 20 max buildings
    # based on density, we can calculate a "spread" of the buildings
    circle_radius = int((size.width + size.height) / (4 * density)) // 2
    center = Coordinate(size.width // 2, size.height // 2)

    generated = set()

    print(f"{circle_radius=} {num_buildings=}")

    for i in range(num_buildings):
        if len(generated) >= limit_count:
            break

        # building start_loc
        x = random.randint(center.x - circle_radius, center.x + circle_radius - 1)
        y = random.randint(center.y - circle_radius, center.y + circle_radius - 1)

        # building size
        width = random.randint(1, 10)
        height = random.randint(1, 10)

        # check if building is within the map
        if x + width >= size.width or y + height >= size.height:
            continue

        if x < 0 or y < 0:
            continue

        generated.add((Coordinate(x, y), Coordinate(x + width, y + height)))

    return generated


def print_map(map: dict[Coordinate, int], size: Size) -> None:
    for y in range(size.height):
        for x in range(size.width):
            print(map[Coordinate(x, y)], end="")
        print()


def convert_to_set_of_rectangles(
    map: dict[Coordinate, int], size: Size
) -> set[tuple[Coordinate, Coordinate]]:
    # any sequence of 1s in the map is a rectangle
    rectangles = set()
    for y in range(size.height):
        for x in range(size.width):
            if map[Coordinate(x, y)] == 1:
                x1 = x
                while x1 < size.width and map[Coordinate(x1, y)] == 1:
                    x1 += 1
                y1 = y
                while y1 < size.height and map[Coordinate(x, y1)] == 1:
                    y1 += 1

                # Check if the current rectangle overlaps with any existing rectangle
                overlaps = False
                for rectangle in rectangles:
                    if (
                        x1 > rectangle[0].x
                        and x < rectangle[1].x
                        and y1 > rectangle[0].y
                        and y < rectangle[1].y
                    ):
                        # keep the rectangle with the smallest x, y and the largest x1, y1
                        overlaps = True
                        break
                    # partial overlaps
                    # if (
                    #     (x1 > rectangle[0].x and x < rectangle[1].x)
                    #     or (y1 > rectangle[0].y and y < rectangle[1].y)
                    # ):
                    #     # merge the rectangles
                    #     # rectangles.remove(rectangle)
                    #     # x = min(x, rectangle[0].x)
                    #     # y = min(y, rectangle[0].y)
                    #     # x1 = min(x1, rectangle[1].x)
                    #     # y1 = min(y1, rectangle[1].y)
                    #     # rectangles.add((Coordinate(x, y), Coordinate(x1, y1)))
                    #     overlaps = True
                    #     break

                # If the current rectangle does not overlap, add it to the set of rectangles
                if not overlaps:
                    rectangles.add((Coordinate(x, y), Coordinate(x1, y1)))

    print(rectangles)
    return rectangles


def visualize_map(rectangles: set[tuple[Coordinate, Coordinate]], size: Size) -> None:
    fig, ax = plt.subplots()
    for rectangle in rectangles:
        x = rectangle[0].x
        y = rectangle[0].y
        width = rectangle[1].x - rectangle[0].x
        height = rectangle[1].y - rectangle[0].y
        ax.add_patch(
            plt.Rectangle((x, y), width, height, edgecolor="black", facecolor="gray")
        )
    ax.set_xlim(0, size.width)
    ax.set_ylim(0, size.height)
    plt.gca().invert_yaxis()
    plt.show()


def get_empty_map(size: Size) -> dict[Coordinate, int]:
    map = {}
    for x in range(size.width):
        for y in range(size.height):
            map[Coordinate(x, y)] = 0
    return map


def main(args: argparse.Namespace) -> None:
    map_size = Size(args.map_size[0], args.map_size[1])
    density = args.density
    map = get_empty_map(map_size)

    map = generate_buildings(map_size, density)
    visualize_map(map, map_size)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--map-size",
        type=int,
        nargs=2,
        default=DEFAULT_MAP_SIZE,
        help="Size of the map",
    )
    parser.add_argument(
        "--density",
        type=float,
        default=DEFAULT_DENSITY,
        help="Density of the rectangles around the middle of the map",
    )
    args = parser.parse_args()
    main(args)
