from os import getcwd


def get_build_env_image_digests():
    # TODO : Get build_env images from Docker Registry, & cache them somehow
    print(getcwd())
    with open("tools/digests", "r") as digests:
        digests = digests.readlines()

    return digests
