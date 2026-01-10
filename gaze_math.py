def get_horizontal_ratio(landmarks, eye_indices, iris_index):
    inner = landmarks[eye_indices[0]]
    outer = landmarks[eye_indices[1]]
    iris = landmarks[iris_index]
    eye_width = abs(inner.x - outer.x)
    if eye_width == 0: return 0.5
    return abs(inner.x - iris.x) / eye_width

def get_vertical_ratio(landmarks, lid_indices, iris_index):
    top = landmarks[lid_indices[0]]
    bottom = landmarks[lid_indices[1]]
    iris = landmarks[iris_index]
    eye_height = abs(top.y - bottom.y)
    if eye_height == 0: return 0.5
    return abs(top.y - iris.y) / eye_height

def get_eye_openness(landmarks, lid_indices, corner_indices):
    top = landmarks[lid_indices[0]]
    bottom = landmarks[lid_indices[1]]
    left = landmarks[corner_indices[0]]
    right = landmarks[corner_indices[1]]
    height = abs(top.y - bottom.y)
    width = abs(left.x - right.x)
    if width == 0: return 0.0
    return height / width