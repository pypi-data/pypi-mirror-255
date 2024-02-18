try:
    import turtle as tu
except ImportError:
    print("Imports failed!")


class Shape:

    Last_Shape = []
    Last_Item_Index = 0
    Item_Number = 0

    @staticmethod
    def Remove_Shape(Index=Last_Item_Index):
        if Index != Shape.Last_Item_Index:
            Shape.Last_Shape.sort()
            shape = Shape.Last_Shape.pop(Index)[1]
            Shape.Last_Shape.sort()
            shape.clear()
            Shape.Last_Shape.sort()
            print(Shape.Last_Shape)
        elif Shape.Last_Shape:
            Shape.Last_Shape.sort()
            shape = Shape.Last_Shape.pop(Index)[1]
            Shape.Last_Shape.sort()
            shape.clear()
            Shape.Last_Shape.sort()
            print(Shape.Last_Shape)

    @staticmethod
    def Star(Size=20, DoFill=False, Color="Black", FillColor="Yellow", pos1=100, pos2=100):
        star = tu.Turtle()
        Shape.Item_Number += 1
        data = [Shape.Item_Number, star]
        Shape.Last_Shape.append(data)
        Shape.Last_Item_Index = len(Shape.Last_Shape) - 1
        star.penup()
        star.goto(pos1, pos2)
        star.pencolor(Color)
        star.pendown()
        if DoFill:
            star.begin_fill()
            star.fillcolor(FillColor)
            for i in range(5):
                star.forward(Size)
                star.left(54)
                star.forward(Size)
                star.right(126)
            star.end_fill()
        elif not DoFill:
            for i in range(5):
                star.forward(Size)
                star.left(54)
                star.forward(Size)
                star.right(126)

    @staticmethod
    def Hexagon(Size=20, DoFill=False, Color="Black", FillColor="Black", pos1=100, pos2=100):
        hexagon = tu.Turtle()
        Shape.Item_Number += 1
        data = [Shape.Item_Number, hexagon]
        Shape.Last_Shape.append(data)
        hexagon.penup()
        hexagon.goto(pos1, pos2)
        hexagon.pencolor(Color)
        hexagon.pendown()
        if DoFill:
            hexagon.begin_fill()
            hexagon.fillcolor(FillColor)
            for _ in range(6):
                hexagon.forward(Size)
                hexagon.left(60)
            hexagon.end_fill()
        elif not DoFill:
            for _ in range(6):
                hexagon.forward(Size)
                hexagon.left(60)

    @staticmethod
    def Square(Size=20, DoFill=False, Color="Black", FillColor="Black", pos1=100, pos2=100):
        square = tu.Turtle()
        Shape.Item_Number += 1
        data = [Shape.Item_Number, square]
        Shape.Last_Shape.append(data)
        square.penup()
        square.goto(pos1, pos2)
        square.pencolor(Color)
        square.pendown()
        if DoFill:
            square.begin_fill()
            square.fillcolor(FillColor)
            for _ in range(4):
                square.forward(Size)
                square.left(90)
            square.end_fill()
        elif not DoFill:
            for _ in range(4):
                square.forward(Size)
                square.left(90)

    @staticmethod
    def Triangle(Size=20, DoFill=False, Color="Black", FillColor="Black", pos1=100, pos2=100):
        triangle = tu.Turtle()
        Shape.Item_Number += 1
        data = [Shape.Item_Number, triangle]
        Shape.Last_Shape.append(data)
        triangle.penup()
        triangle.goto(pos1, pos2)
        triangle.pencolor(Color)
        triangle.pendown()
        if DoFill:
            triangle.fillcolor(FillColor)
            triangle.begin_fill()
            for _ in range(3):
                triangle.forward(Size)
                triangle.left(120)
            triangle.end_fill()
        elif not DoFill:
            for _ in range(3):
                triangle.forward(Size)
                triangle.left(120)