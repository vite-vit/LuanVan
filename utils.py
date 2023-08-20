def normalize_box(bbox: list, width: float, height: float) -> list:
    return [
        int(bbox[0] * 1000 / width),
        int(bbox[1] * 1000 / height),
        int(bbox[2] * 1000 / width),
        int(bbox[3] * 1000 / height),
    ]  


def unnorm_box(bbox: list, width: float, height: float) -> list:
    return [
        bbox[0] * width / 1000,
        bbox[1] * height / 1000,
        bbox[2] * width / 1000,
        bbox[3] * height / 1000,
    ]