def interp(x, x1, x2, y1, y2) -> float:
    """Interpolate between two points.

    Parameters
    ----------
    x : float
        The x value to interpolate to.
    x1 : float
        The x value of the first point.
    x2 : float
        The x value of the second point.
    y1 : float
        The y value of the first point.
    y2 : float
        The y value of the second point.

    Returns
    -------
    float
        The interpolated value.
    """
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)
