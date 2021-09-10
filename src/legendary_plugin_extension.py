from gimpfu import (pdb, gimp, RGBA_IMAGE, NORMAL_MODE, GRAYA_IMAGE, register, main, RGB, CHANNEL_OP_SUBTRACT,
                    BUCKET_FILL_BG, LAYER_MODE_NORMAL, PF_IMAGE, PF_DRAWABLE, PF_COLOR,
                    PF_INT, PF_FILENAME)


# get the type we want for our layer
def get_layer_type(image):
    if image.base_type is RGB:
        return RGBA_IMAGE
    return GRAYA_IMAGE


# finds layer position in a layer group
def get_layer_stack_position(layer, group):
    iterator_pos = 0

    if type(group) is tuple:
        for layer_id in group:
            if gimp.Item.from_id(layer_id) == layer:
                return iterator_pos
            iterator_pos = iterator_pos + 1
    else:
        for group_layer in group:
            if group_layer == layer:
                return iterator_pos
            iterator_pos = iterator_pos + 1

    return 0  # for some reason we didn't find proper position of layer in the stack


# add a new layer under given layer
def add_layer_below(image, layer, preserveCmd=False, argumentPass='()=>skip'):
    stack_pos = 0

    if layer.parent:
        # parent is a group layer (= we're inside a group layer)
        # this returns a tuple: (parent id, (<child ids>)). We want child ids.
        sublayers = pdb.gimp_item_get_children(layer.parent)[1]
        stack_pos = get_layer_stack_position(layer, sublayers)
    else:
        # parent is not a group layer (e.g. selected layer is on top level)
        stack_pos = get_layer_stack_position(layer, image.layers)

    if preserveCmd:
        new_name = layer.name
    else:
        new_name = layer.name.split('()=>')[0]

    layer_out = gimp.Layer(image, "outline::{}{}".format(new_name, argumentPass),
                           image.width, image.height, get_layer_type(image), 100, NORMAL_MODE)

    # if img.active_layer.parent doesn't exist, it adds layer to top group. Otherwise
    # the layer will be added into current layer group
    pdb.gimp_image_insert_layer(image, layer_out, layer.parent, stack_pos + 1)

    return layer_out


__saved_colors_bg = []


def color_push_bg(color):
    __saved_colors_bg.append(color)


def color_pop_bg():
    return __saved_colors_bg.pop()


def set_bg_stack(newColor):
    color_push_bg(gimp.get_background())
    gimp.set_background(newColor)


def restore_bg_stack():
    gimp.set_background(color_pop_bg())


def clear_selection(image):
    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_SUBTRACT, 0, 0, image.width, image.height)


def create_selection(image, layer, thickness, feather):
    # Select the text
    pdb.gimp_selection_layer_alpha(layer)

    # Grow the selection
    pdb.gimp_selection_grow(image, thickness)

    # Feather it
    if (feather > 0):
        pdb.gimp_selection_feather(image, feather)


def paint_selection(layer):
    pdb.gimp_edit_bucket_fill_full(layer, BUCKET_FILL_BG, LAYER_MODE_NORMAL, 100, 0, 0, 1, 0, 1, 1)


def do_text_outline(image, drawable, color, thickness, feather):
    clear_selection(image)
    layer = image.active_layer

    set_bg_stack(color)

    create_selection(image, layer, thickness, feather)
    outline_layer = add_layer_below(image, layer)
    paint_selection(outline_layer)

    restore_bg_stack()

    # clear selection and restore background color
    clear_selection(image)


def build_legendary_playmat(image, drawable, filename, color, thickness, feather):
    layer = pdb.gimp_file_load_layer(image, filename)
    pdb.gimp_image_insert_layer(image, layer, None, 0)
    pdb.gimp_item_transform_perspective(layer, 0, 0, image.width, 0, 0, image.height, image.width, image.height)


register(
  "draw-full-legendary-playmat",                            # procedure name for whatever
  "Draw Playmat",                                           # blurb
  "Generate a Legendary playmat.",                          # help message
  "Mike F", "Mike F", "Sept 2021",                          # author, copyright, year
  "Draw Playmat",                                           # menu name
  "*",                                                      # type of images we accept
  [                                                         # Parameters
      (PF_IMAGE, "image", "takes current image", None),
      (PF_DRAWABLE, "drawable", "Input layer", None),
      (PF_FILENAME, "filename", "Filename", None),
      (PF_COLOR, "color", "Outline color", (0, 0, 0)),
      (PF_INT, "thickness", "Outline thickness", 3),
      (PF_INT, "feather", "Feather", 0)
  ],
  [],                                                      # output / return parameters
  build_legendary_playmat,                                 # python function that will be called
  menu="<Image>/Filters/Legendary"
)


main()
