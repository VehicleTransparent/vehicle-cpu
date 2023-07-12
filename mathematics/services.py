def calculate_area(top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    """calculate area based on (top_left_corner) and (bottom_right_corner) coordinates"""
    width = round(abs(bottom_right_x - top_left_x))
    height = round(abs(bottom_right_y - top_left_y))
    return width * height


def calculate_rectangle_center(top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    """Calculate center of a rectangle based on (top_left_corner) and (bottom_right_corner) coordinates"""
    center_x = round((top_left_x + bottom_right_x) / 2)
    center_y = round((top_left_y + bottom_right_y) / 2)
    center = (center_x, center_y)
    return center


def map_values_ranges(input_value, input_range_min=180, input_range_max=0, output_range_min=2, output_range_max=12):
    """
    Name        :   map_values_ranges
    Description :   Mapping input value from range to another range the relation is linear equation.
    Return      :   The mapped value after changing range of input to range of output.
    Arguments   :   - input_value:      value to be modified based on ranges.
                :    - input_range_min:  value of the minimum of input range.
                :    - input_range_max:  value of the maximum of input range.
                :    - output_range_min: value of the minimum of output range.
                :    - output_range_max: value of the maximum of output range.
    """
    return (input_value - input_range_min) * (output_range_max - output_range_min) / (
            input_range_max - input_range_min) + output_range_min

