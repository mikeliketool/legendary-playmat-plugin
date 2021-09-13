from gimpfu import (pdb, gimp, RGBA_IMAGE, NORMAL_MODE, GRAYA_IMAGE, register, main, RGB, CHANNEL_OP_SUBTRACT,
                    BUCKET_FILL_BG, LAYER_MODE_NORMAL, PF_IMAGE, PF_COLOR, STROKE_LINE, PF_INT,
                    PF_FILENAME, CHANNEL_OP_REPLACE, FILL_WHITE, gimpcolor, TEXT_JUSTIFY_CENTER)

WHITE = gimpcolor.RGB(255, 255, 255)
CELL_WIDTH = 375
CELL_HEIGHT = 525
LABEL_HEIGHT = 65
THICKNESS = 3
HQ_HEIGHT = 600


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


def do_text_outline(image, layer, color, thickness, feather):
    clear_selection(image)

    set_bg_stack(color)

    create_selection(image, layer, thickness, feather)
    outline_layer = add_layer_below(image, layer)
    paint_selection(outline_layer)

    restore_bg_stack()

    # clear selection and restore background color
    clear_selection(image)


def load_pic_and_transform_perspective(image, filename):
    layer = pdb.gimp_file_load_layer(image, filename)
    pdb.gimp_image_insert_layer(image, layer, None, 0)
    pdb.gimp_item_transform_perspective(layer, 0, 0, image.width, 0, 0, image.height, image.width, image.height)


# build out the cell label using the Percolator font and outline the text
def draw_label(image, group, label_text, font_size, top_left_x, top_left_y, width, height):
    cell_label_layer = pdb.gimp_text_layer_new(image, label_text, 'Percolator Medium', font_size, 0)
    pdb.gimp_image_insert_layer(image, cell_label_layer, group, 0)
    pdb.gimp_text_layer_set_antialias(cell_label_layer, 1)
    pdb.gimp_text_layer_set_justification(cell_label_layer, TEXT_JUSTIFY_CENTER)
    pdb.gimp_text_layer_set_color(cell_label_layer, WHITE)
    pdb.gimp_text_layer_resize(cell_label_layer, width, height)
    pdb.gimp_layer_set_offsets(cell_label_layer, top_left_x, top_left_y)
    pdb.gimp_drawable_set_visible(cell_label_layer, True)
    return cell_label_layer


def draw_cell(image, group, label_text, top_left_x, top_left_y):
    # build out the cell with a border and have it bucket filled. Make it opaque so oyu can still see the picture layer
    # below
    radius = 30
    cell_layer = gimp.Layer(image, "{}_cell".format(label_text), image.width, image.height, get_layer_type(image),
                            100, NORMAL_MODE)
    pdb.gimp_image_insert_layer(image, cell_layer, group, 1)
    pdb.gimp_image_select_round_rectangle(image, CHANNEL_OP_REPLACE, top_left_x, top_left_y + LABEL_HEIGHT,
                                          CELL_WIDTH, CELL_HEIGHT, radius, radius)

    pdb.gimp_drawable_edit_stroke_selection(cell_layer)
    pdb.gimp_drawable_edit_fill(cell_layer, FILL_WHITE)
    pdb.plug_in_autocrop_layer(image, cell_layer)
    clear_selection(image)


def draw_single_cell_with_label(image, label_text, top_left_x, top_left_y, color):
    group = gimp.GroupLayer(image)
    group.name = "{}_group".format(label_text)
    pdb.gimp_image_insert_layer(image, group, None, 0)

    if len(label_text) > 0:
        cell_label_layer = draw_label(image, group, label_text, 54, top_left_x, top_left_y, CELL_WIDTH, LABEL_HEIGHT)
        do_text_outline(image, cell_label_layer, color, THICKNESS, 0)
    draw_cell(image, group, label_text, top_left_x, top_left_y)


def draw_hq(image, color, top_left_x, top_left_y):
    HQ_WIDTH = 2070
    group = gimp.GroupLayer(image)
    group.name = "HQ_group"
    pdb.gimp_image_insert_layer(image, group, None, 0)
    hq_layer = gimp.Layer(image, "HQ", image.width, image.height, get_layer_type(image),
                          100, NORMAL_MODE)
    pdb.gimp_image_insert_layer(image, hq_layer, group, 0)
    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE, top_left_x, top_left_y,
                                    HQ_WIDTH, HQ_HEIGHT)
    pdb.gimp_drawable_edit_stroke_selection(hq_layer)
    pdb.gimp_drawable_edit_fill(hq_layer, FILL_WHITE)
    pdb.plug_in_autocrop_layer(image, hq_layer)
    clear_selection(image)
    hq_label_layer = draw_label(image, group, 'HQ', 150, top_left_x, top_left_y, HQ_WIDTH, 150)
    do_text_outline(image, hq_label_layer, color, THICKNESS, 0)


def draw_legendary_playmat_28_by_14(image, filename, opacity, color):
    ROW_GAP = 85
    COLUMN_GAP = 70
    OUTSIDE_GAP = 115
    MAIN_SECTION_GAP = 162.5
    SINGLE_CELL_WITH_LABEL_HEIGHT = CELL_HEIGHT + LABEL_HEIGHT
    FIRST_COLUMN_X = 115
    FIRST_ROW_Y = 115
    SECOND_ROW_Y = FIRST_ROW_Y + SINGLE_CELL_WITH_LABEL_HEIGHT + ROW_GAP
    THIRD_ROW_Y = SECOND_ROW_Y + SINGLE_CELL_WITH_LABEL_HEIGHT + ROW_GAP
    SECOND_COLUMN_X = FIRST_COLUMN_X + CELL_WIDTH + COLUMN_GAP
    LAST_COLUMN_X = image.width - OUTSIDE_GAP - CELL_WIDTH
    SECOND_LAST_COLUMN_X = LAST_COLUMN_X - CELL_WIDTH - COLUMN_GAP
    gimp.progress_init("Drawing playmat")
    load_pic_and_transform_perspective(image, filename)
    gimp.progress_update(0.10)
    pdb.gimp_context_set_foreground(WHITE)
    pdb.gimp_context_set_opacity(opacity)
    pdb.gimp_context_set_paint_mode(LAYER_MODE_NORMAL)
    pdb.gimp_context_set_stroke_method(STROKE_LINE)
    pdb.gimp_context_set_line_width(3)
    pdb.gimp_context_set_antialias(1)
    draw_single_cell_with_label(image, '', FIRST_COLUMN_X, FIRST_ROW_Y, color)
    draw_single_cell_with_label(image, 'Mastermind', FIRST_COLUMN_X, SECOND_ROW_Y, color)
    draw_single_cell_with_label(image, 'Scheme', FIRST_COLUMN_X, THIRD_ROW_Y, color)
    gimp.progress_update(0.20)
    draw_single_cell_with_label(image, 'Escaped', SECOND_COLUMN_X, FIRST_ROW_Y, color)
    draw_single_cell_with_label(image, 'Strikes', SECOND_COLUMN_X, SECOND_ROW_Y, color)
    draw_single_cell_with_label(image, 'Twists', SECOND_COLUMN_X, THIRD_ROW_Y, color)
    gimp.progress_update(0.40)
    draw_single_cell_with_label(image, 'Bystanders', LAST_COLUMN_X, FIRST_ROW_Y, color)
    draw_single_cell_with_label(image, 'S.H.E.I.L.D.', LAST_COLUMN_X, SECOND_ROW_Y, color)
    draw_single_cell_with_label(image, 'Sidekicks', LAST_COLUMN_X, THIRD_ROW_Y, color)
    gimp.progress_update(0.60)
    draw_single_cell_with_label(image, 'Wounds', SECOND_LAST_COLUMN_X, FIRST_ROW_Y, color)
    draw_single_cell_with_label(image, 'Villian Deck', SECOND_LAST_COLUMN_X, SECOND_ROW_Y, color)
    draw_single_cell_with_label(image, 'Hero Deck', SECOND_LAST_COLUMN_X, THIRD_ROW_Y, color)
    gimp.progress_update(0.80)
    hq_x = OUTSIDE_GAP + CELL_WIDTH * 2 + COLUMN_GAP + MAIN_SECTION_GAP
    hq_y = image.height - OUTSIDE_GAP - HQ_HEIGHT
    draw_hq(image, color, hq_x, hq_y)
    gimp.progress_update(1)


register(
  "draw-full-legendary-playmat",                            # procedure name for whatever
  "Draw 28in x 14in Playmat",                               # blurb
  "Generate a Legendary playmat.",                          # help message
  "Mike F", "Mike F", "Sept 2021",                          # author, copyright, year
  "Draw 28in x 14in Playmat",                               # menu name
  "*",                                                      # type of images we accept
  [                                                         # Parameters
      (PF_IMAGE, "image", "Takes current image", None),
      (PF_FILENAME, "filename", "Filename", None),
      (PF_INT, "opacity", "Opacity of Cells", 15),
      (PF_COLOR, "color", "Label Outline Color", (0, 0, 0))
  ],
  [],                                                      # output / return parameters
  draw_legendary_playmat_28_by_14,                         # python function that will be called
  menu="<Image>/Filters/Legendary"
)


main()
