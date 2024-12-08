import math
import random

# 1) Characteristics Of SlopeGeometry Attribute
HEIGHT = 12
WATER_HEIGHT_LEFT = 10
WATER_HEIGHT_RIGHT = 4
SLOPE = 1 / 2.6
SIDE_SMALL = (0.2 * HEIGHT) + 3
SIDE_BIG = SIDE_SMALL + ((2 * HEIGHT) / SLOPE)
BETA = math.atan(SLOPE)
MAX_RANGE = HEIGHT / math.tan(BETA)  # start
HEIGHT_DIV_SLOPE = HEIGHT / SLOPE
SIDE_SMALL_SUM_HEIGHT_DIV_SLOPE = SIDE_SMALL + HEIGHT_DIV_SLOPE  # end


# 2) Properties Materials
class PropertiesMaterials:
    def __init__(self, gamma_sat, gs, drained_cohesion, drained_frictio_angle, bedrock_height):
        # a = (20, 2.8, 50, 8, 25)
        self.gamma_watter = 9.81
        self.gamma_sat = gamma_sat
        self.gs = gs
        self.drained_cohesion = drained_cohesion  # c_prime
        self.drained_frictio_angle = drained_frictio_angle  # phi_prime
        self.bedrock_height = bedrock_height

        self.gamma_sat_div_gamma_watter = self.gamma_sat / self.gamma_watter


# 3.1) Slip Surface
class SlipSurface:
    def __init__(self, size_x, size_y, x_center_circle, y_center_circle, radius, teta):
        self.size_x = size_x
        self.size_y = size_y
        # self.x_center_circle = random.randint(10, self.size_x)
        self.x_center_circle = x_center_circle
        self.y_center_circle = y_center_circle
        # self.y_center_circle = random.randint(0, self.size_y)
        self.radius = radius
        self.teta=teta

# 3.2) Important Coordinates Circle
class ImportantCoordinatesCircle:
    def __init__(self):
        self.ss = None
        self.intersection_horizontal_axis_and_slip_surface_left = 0
        self.intersection_horizontal_axis_and_slip_surface_right = 0
        self.intersection_embankment_and_slip_surface = 0

    def computing(self, size_x, size_y, x_center_circle, y_center_circle,radius):
        self.ss = SlipSurface(size_x, size_y, x_center_circle, y_center_circle,radius)
        try:
            intersection_horizontal_axis_and_slip_surface = \
                math.sqrt(self.ss.radius ** 2 - self.ss.y_center_circle ** 2) + self.ss.x_center_circle
        except ValueError:
            return 0

        self.intersection_horizontal_axis_and_slip_surface_left = intersection_horizontal_axis_and_slip_surface - 40
        self.intersection_horizontal_axis_and_slip_surface_right = intersection_horizontal_axis_and_slip_surface

        intersection_embankment_and_slip_surface = \
            math.sqrt(self.ss.radius ** 2 - ((HEIGHT - self.ss.x_center_circle) ** 2))

        intersection_embankment_and_slip_surface1 = -intersection_embankment_and_slip_surface + self.ss.x_center_circle
        intersection_embankment_and_slip_surface2 = intersection_embankment_and_slip_surface + self.ss.x_center_circle

        if HEIGHT_DIV_SLOPE < intersection_embankment_and_slip_surface1 < SIDE_SMALL_SUM_HEIGHT_DIV_SLOPE:
            self.intersection_embankment_and_slip_surface = intersection_embankment_and_slip_surface1

        if HEIGHT_DIV_SLOPE < intersection_embankment_and_slip_surface2 < SIDE_SMALL_SUM_HEIGHT_DIV_SLOPE:
            self.intersection_embankment_and_slip_surface = intersection_embankment_and_slip_surface2

    def get_intersections(self, x_center_circle, y_center_circle,radius):
        while True:
            self.computing(15, 15, x_center_circle, y_center_circle)
            if MAX_RANGE < self.intersection_horizontal_axis_and_slip_surface_right < MAX_RANGE + SIDE_SMALL:
                return

    def get_valid_circles(self,radius):
        valid_circles = []
        for x in range(10, 20):
            for y in range(20):
                self.computing(15, 15, x, y, radius)
                if MAX_RANGE < self.intersection_horizontal_axis_and_slip_surface_right < MAX_RANGE + SIDE_SMALL:
                    valid_circles.append((x, y))
        return valid_circles

    def is_valid_circle(self):
        if MAX_RANGE < self.intersection_horizontal_axis_and_slip_surface_right < MAX_RANGE + SIDE_SMALL:
            return True
        return False


# 4) Number Of Slices
class NumberOfSlices:
    def __init__(self, number_slices_first_piece, number_slices_second_piece, number_slices_third_piece):
        self.number_slices_first_piece = number_slices_first_piece
        self.number_slices_second_piece = number_slices_second_piece
        self.number_slices_third_piece = number_slices_third_piece
        self.number_of_slices = number_slices_first_piece + number_slices_second_piece + number_slices_third_piece


# 5.1) Width Slices
class WidthSlices:
    def __init__(self, x_center_circle, y_center_circle,radius):
        self.icc = ImportantCoordinatesCircle()
        self.icc.computing(15, 15, x_center_circle, y_center_circle,radius)
        self.nos = NumberOfSlices(3, 3, 1)
        self.__computing()

    def __computing(self):
        if not self.icc.is_valid_circle():
            return
        numerator_first_piece = 0 - self.icc.intersection_horizontal_axis_and_slip_surface_left
        numerator_second_piece = HEIGHT / math.tan(BETA)
        numerator_third_piece = self.icc.intersection_embankment_and_slip_surface - numerator_second_piece

        self.width_first_piece = numerator_first_piece / self.nos.number_slices_first_piece
        self.width_second_piece = numerator_second_piece / self.nos.number_slices_second_piece
        self.width_third_piece = numerator_third_piece / self.nos.number_slices_third_piece


# 5.2)
class EndCoordinatesOfSlices:
    def __init__(self, x_center_circle, y_center_circle,radius):
        self.x_indexes = []
        self.y_indexes = []
        self.y2_indexes = []
        self.y3_indexes = []
        self.results = []
        self.ws = WidthSlices(x_center_circle, y_center_circle,radius)
        self.wsw = WetSpecificWeight()
        self.computing()

    def computing(self):
        if not self.ws.icc.is_valid_circle():
            return
        x_index = self.ws.icc.intersection_horizontal_axis_and_slip_surface_left
        y_index, alpha_index, delta_index, force_horizontal = 0, 0, 0, 0
        for indexSlice in range(self.ws.nos.number_of_slices):
            if x_index < 0:
                x_index = self.ws.icc.intersection_horizontal_axis_and_slip_surface_left + (
                        (indexSlice + 1) * self.ws.width_first_piece)

                sqr = self.ws.icc.ss.radius ** 2 - x_index - self.ws.icc.ss.x_center_circle ** 2
                y1_index = math.sqrt(sqr) + self.ws.icc.ss.y_center_circle
                y2_index = -1 * y1_index

                y_index = 0
                if y1_index < 0 and y2_index < 0:
                    return 0
                elif y1_index >= 0 > y2_index:
                    y_index = y2_index
                elif y2_index >= 0 > y1_index:
                    y_index = y1_index
                elif y1_index >= 0 and y2_index >= 0:
                    y_index = min(y1_index, y2_index)

                if indexSlice == 0:
                    area_index = y_index / 2 * self.ws.width_first_piece
                    alpha_index = math.atan(y_index / x_index)
                else:
                    area_index = (self.y_indexes[-1] + y_index) / 2 * self.ws.width_first_piece
                    alpha_index = math.atan((y_index - self.y_indexes[-1]) / (x_index - self.x_indexes[-1]))

                delta_index = self.ws.width_first_piece / math.cos(alpha_index)
                force_horizontal = self.wsw.gamma_wet * area_index

            elif 0 <= x_index < MAX_RANGE:
                x_index = x_index + self.ws.width_second_piece

                sqr = self.ws.icc.ss.radius ** 2 - x_index - self.ws.icc.ss.x_center_circle ** 2
                y1_index = math.sqrt(sqr) + self.ws.icc.ss.y_center_circle
                y2_index = -1 * y1_index
                y12_index = SLOPE * x_index

                y_index = 0
                if y1_index < 0 and y2_index < 0:
                    return 0
                elif y1_index >= 0 > y2_index:
                    y_index = y2_index
                elif y2_index >= 0 > y1_index:
                    y_index = y1_index
                elif y1_index >= 0 and y2_index >= 0:
                    y_index = min(y1_index, y2_index)

                if not self.y2_indexes:
                    area_index = (y_index / 2 * self.ws.width_second_piece) + (y12_index / 2 * self.ws.width_second_piece)
                    alpha_index = math.atan(y_index / x_index)
                else:
                    area_index = (self.y_indexes[-1] + y_index) / 2 * self.ws.width_second_piece +\
                                 (self.y2_indexes[-1] + y12_index) / 2 * self.ws.width_second_piece
                    alpha_index = math.atan((y_index - self.y_indexes[-1]) / (x_index - self.x_indexes[-1]))

                delta_index = self.ws.width_first_piece / math.cos(alpha_index)
                force_horizontal = self.wsw.gamma_wet * area_index
                self.y2_indexes.append(y12_index)

            elif x_index >= MAX_RANGE:
                x_index = x_index + self.ws.width_third_piece

                sqr = self.ws.icc.ss.radius ** 2 - x_index - self.ws.icc.ss.x_center_circle ** 2
                y1_index = math.sqrt(sqr) + self.ws.icc.ss.y_center_circle
                y2_index = -1 * y1_index
                y12_index = SLOPE * x_index

                y_index = 0
                if y1_index < 0 and y2_index < 0:
                    return 0
                elif y1_index >= 0 > y2_index:
                    y_index = y2_index
                elif y2_index >= 0 > y1_index:
                    y_index = y1_index
                elif y1_index >= 0 and y2_index >= 0:
                    y_index = min(y1_index, y2_index)

                if not self.y3_indexes:
                    area_index = (y_index / 2 * self.ws.width_third_piece) + (
                                y12_index / 2 * self.ws.width_third_piece)
                    try:
                        alpha_index = math.atan(y_index / x_index)
                    except:
                        print(3)
                else:
                    area_index = (self.y_indexes[-1] + y_index) / 2 * self.ws.width_third_piece + \
                                 (self.y3_indexes[-1] + y12_index) / 2 * self.ws.width_third_piece
                    alpha_index = math.atan((y_index - self.y_indexes[-1]) / (x_index - self.x_indexes[-1]))

                delta_index = self.ws.width_first_piece / math.cos(alpha_index)
                force_horizontal = self.wsw.gamma_wet * area_index
                self.y3_indexes.append(y12_index)

            self.x_indexes.append(x_index)
            self.y_indexes.append(y_index)
            self.results.append((alpha_index, delta_index, force_horizontal))


# 6) Wet Specific Weight
class WetSpecificWeight:
    def __init__(self):
        self.pms = PropertiesMaterials(1, 2, 3, 4, 5)
        self.gs = 2
        self.__computing()

    def __computing(self):
        self.__porosity_ratio_numerator = self.gs - self.pms.gamma_sat_div_gamma_watter
        self.__porosity_ratio_denominator = self.pms.gamma_sat_div_gamma_watter - 1
        self.porosity_ratio = self.__porosity_ratio_numerator / self.__porosity_ratio_denominator
        self.moisture_soil = self.porosity_ratio / self.gs
        self.gamma_wet = (self.gs * (1 + self.moisture_soil) / (1 + self.porosity_ratio)) * self.pms.gamma_watter


# 9) Forces
class Forces:
    def __init__(self):
        self.wsw = WetSpecificWeight()
        self.force_horizontal = self.wsw.gamma_wet
        self.force_vertical = 0


# 10) Main Function
class Coast:
    def __init__(self, x_center_circle, y_center_circle,radius):
        self.pm = PropertiesMaterials(1, 2, 3, 4, 5)
        self.ecs = EndCoordinatesOfSlices(x_center_circle, y_center_circle,radius)

    def get_q(self, alpha, delta, force_horizontal, theta, F):
        if not self.ecs.ws.icc.is_valid_circle():
            return False
        force_vertical = 0
        part1 = -force_vertical * math.sin(alpha) - force_horizontal * math.cos(alpha)
        part2 = self.pm.drained_cohesion * delta / F
        part3 = -force_vertical * math.cos(alpha) - force_horizontal * math.sin(alpha) + delta
        part4 = math.tan(self.pm.drained_frictio_angle) / F
        part5 = math.cos(alpha - theta)
        part6 = math.sin(alpha - theta) * math.tan(self.pm.drained_frictio_angle) / F
        q = (part1 - part2 + part3 * part4) / (part5 + part6)
        return q

    def total_q(self):
        i = 1
        f = 1
        while f < 2:
            q_total = 0
            for res in self.ecs.results:
                q = self.get_q(res[0], res[1], res[2], -0.56, f)
                # print("Q"+str(i)+"= ", q)
                if not q:
                    return 1000
                q_total += q
                i += 1
            if -0.1 < q_total < 0.1:
                # print("x center: ", self.ecs.ws.icc.ss.x_center_circle)
                # print("y center: ", self.ecs.ws.icc.ss.y_center_circle)
                # print("sigma Q =: ", q_total)
                # print("f= ", f)
                break
            f += 0.001
        # print("x, y = ", self.ecs.ws.icc.ss.x_center_circle, self.ecs.ws.icc.ss.y_center_circle)
        # print("*" * 70)
        return f
        # print("sigma Q =: ", q_total)


def coast_function(position):
    cost = Coast(position[0], position[1])
    f = cost.total_q()
    return f


if __name__ == "__main__":
    # icc = ImportantCoordinatesCircle()
    # cir = icc.get_valid_circles()
    # print(len(cir))
    # print(cir)
    # fs = []
    # cir2 = []
    # for i in range(len(cir)):
    #     ws = EndCoordinatesOfSlices(cir[i][0], cir[i][1])
    #     cost = Coast(cir[i][0], cir[i][1])
    #     f1, x, y = cost.total_q()
    #     fs.append(f1)
    #     cir2.append((x, y))
    # print(min(fs), cir2[fs.index(min(fs))])

    # cost = Coast(19, 5.21322787)
    cost = Coast(13.6151313, 4.05684604,16)
    print(cost.total_q())

