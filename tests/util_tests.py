from gempy_viewer import GemPyToVista


def check_image_hash(plot3d: GemPyToVista, hash:str):
    import imagehash
    from PIL import Image
    img = Image.fromarray(plot3d.p.last_image)
    hash_ = str(imagehash.colorhash(img))
    assert hash_ == hash, f"Image hash is not correct: {hash_}"
