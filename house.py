def main():
    x, y = 300, 400
    width, height = 200, 300

    draw_house(x, y, width, height)


def draw_house(x, y, width, height):
    """
    Нарисовать дом
    :param x: середина дома
    :param y: середина низа фундамента
    :param width: полная ширина дома (фундамент и вылет крыши включены)
    :param height: полная высота дома
    :return:
    """
    print('Типа рисую дом...', x, y, width, height)
    foundation_height = 0.05 * height  # высота фундамента
    walls_width = 0.9 * width  # ширина стен
    walls_height = 0.5 * height  # высота стен
    roof_height = height - foundation_height - walls_height  # высота крыши

    draw_foundation_height(x, y, width, foundation_height)
    draw_house_walls(x, y - foundation_height, walls_width, walls_height)
    draw_house_roof(x, y - foundation_height - walls_height, width, roof_height)


def draw_foundation_height(x, y, width, height):
    """
    Нарисовать фундамент
    :param x: середина фундамента
    :param y: середина низа фундамента
    :param width: полная ширина фундамента
    :param height: полная высота фундамента
    """
    print('типа рисую фундамент...', x, y, width, height)
    pass


def draw_house_walls(x, y, width, height):
    """
    Нарисовать стены
    :param x: середина стены
    :param y: середина низа стены
    :param width: полная ширина стены
    :param height: полная высота стены
    """
    print('типа рисую стены...', x, y, width, height)
    pass


def draw_house_roof(x, y, width, height):
    """
    Нарисовать крышу
    :param x: середина крыши
    :param y: середина низа крыши
    :param width: полная ширина крыши
    :param height: полная высота крыши
    """
    print('типа рисую крышу...', x, y, width, height)
    pass

if __name__ == '__main__':
    main()
