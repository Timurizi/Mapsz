def point_coords_to_string(x, y):
    return f"{x},{y},comma"

def list_of_points_to_req_param(list_of_points):
    return '~'.join(list_of_points)
