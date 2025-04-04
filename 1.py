
def main():
    x, y = 300, 400
    width, height = 200, 300

    draw_house(x, y, width, height)

def draw_house(x, y, width, height):
    """ width - ширина,  height - высота"""
    print('типа рисую дом...',x, y, width, height)
    foundation_height = 0.05 * height  # высота фундамента
    walls_width = 0.9 * width # ширина стен
    walls_height = 0.5 * height # высота стен
    roof_height = height - foundation_height - walls_height # высота крыши

    foundation_height(x, y, width, foundation_height)
    draw_house_walls(x, y - foundation_height, walls_width , walls_height)
    draw_house_roof(x, y - foundation_height - walls_height, width, roof_height)

def foundation_height(x, y, width, height):
    print('типа рисую фундамент...', x, y, width, height)
    pass

def draw_house_walls(x, y, width, height):
    print('типа рисую стены...', x, y, width, height)
    pass

def draw_house_roof(x, y, width, height):
    print('типа рисую крышу...', x, y, width, height)
    pass

main()


