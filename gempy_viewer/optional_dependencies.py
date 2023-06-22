def require_gempy():
    try:
        import gempy as gp
    except ImportError:
        raise ImportError("The gempy package is required to run this function.")
    return gp


def require_gempy_plugins():
    try:
        import gempy.plugins
    except ImportError:
        raise ImportError("The gempy.plugins package is required to run this function.")
    return gempy.plugins
    
