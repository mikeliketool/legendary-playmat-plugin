from gimpfu import (pdb, gimp, RGBA_IMAGE, NORMAL_MODE, GRAYA_IMAGE, register, main, RGB, CHANNEL_OP_SUBTRACT,
                    BUCKET_FILL_BG, LAYER_MODE_NORMAL, PF_IMAGE, PF_COLOR, STROKE_LINE, PF_INT, PF_BOOL,
                    PF_FILENAME, CHANNEL_OP_REPLACE, FILL_WHITE, gimpcolor, TEXT_JUSTIFY_CENTER, PF_STRING)

WHITE = gimpcolor.RGB(255, 255, 255)
CELL_WIDTH = 375
CELL_HEIGHT = 525
LABEL_HEIGHT = 65
THICKNESS = 3
LARGE_CELL_HEIGHT = 600
LARGE_CELL_WIDTH = 2070
ROW_GAP = 85
COLUMN_GAP = 70
OUTSIDE_GAP = 115
MAIN_SECTION_GAP = 162.5
SINGLE_CELL_WITH_LABEL_HEIGHT = CELL_HEIGHT + LABEL_HEIGHT
SECOND_ROW_Y = OUTSIDE_GAP + SINGLE_CELL_WITH_LABEL_HEIGHT + ROW_GAP
THIRD_ROW_Y = SECOND_ROW_Y + SINGLE_CELL_WITH_LABEL_HEIGHT + ROW_GAP
SECOND_COLUMN_X = OUTSIDE_GAP + CELL_WIDTH + COLUMN_GAP


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


def set_bg_stack(new_color):
    color_push_bg(gimp.get_background())
    gimp.set_background(new_color)


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
def draw_label(image, group, color, label_text, font_size, top_left_x, top_left_y, width, height):
    cell_label_layer = pdb.gimp_text_layer_new(image, label_text, 'Percolator Medium', font_size, 0)
    pdb.gimp_image_insert_layer(image, cell_label_layer, group, 0)
    pdb.gimp_text_layer_set_antialias(cell_label_layer, 1)
    pdb.gimp_text_layer_set_justification(cell_label_layer, TEXT_JUSTIFY_CENTER)
    pdb.gimp_text_layer_set_color(cell_label_layer, WHITE)
    pdb.gimp_text_layer_resize(cell_label_layer, width, height)
    pdb.gimp_layer_set_offsets(cell_label_layer, top_left_x, top_left_y)
    pdb.gimp_drawable_set_visible(cell_label_layer, True)
    do_text_outline(image, cell_label_layer, color, THICKNESS, 0)


def finish_selection(image, layer, fill=True):
    pdb.gimp_drawable_edit_stroke_selection(layer)
    if fill:
        pdb.gimp_drawable_edit_fill(layer, FILL_WHITE)
    clear_selection(image)


def draw_cell(image, group, label_text, top_left_x, top_left_y):
    # build out the cell with a border and have it bucket filled. Make it opaque so oyu can still see the picture layer
    # below
    radius = 30
    cell_layer = gimp.Layer(image, "{}_cell".format(label_text), image.width, image.height, get_layer_type(image),
                            100, NORMAL_MODE)
    pdb.gimp_image_insert_layer(image, cell_layer, group, 1)
    pdb.gimp_image_select_round_rectangle(image, CHANNEL_OP_REPLACE, top_left_x, top_left_y + LABEL_HEIGHT,
                                          CELL_WIDTH, CELL_HEIGHT, radius, radius)
    finish_selection(image, cell_layer)
    pdb.plug_in_autocrop_layer(image, cell_layer)


def create_group_layer(image, text):
    group = gimp.GroupLayer(image)
    group.name = "{}_group".format(text)
    pdb.gimp_image_insert_layer(image, group, None, 0)
    return group


def draw_single_cell_with_label(image, label_text, top_left_x, top_left_y, color):
    group = create_group_layer(image, label_text)
    if len(label_text) > 0:
        draw_label(image, group, color, label_text, 54, top_left_x, top_left_y, CELL_WIDTH, LABEL_HEIGHT)
    draw_cell(image, group, label_text, top_left_x, top_left_y)


def draw_large_cell(image, color, text, top_left_x, top_left_y):
    group = create_group_layer(image, text)
    large_layer = gimp.Layer(image, '{}_cell'.format(text), image.width, image.height, get_layer_type(image),
                             100, NORMAL_MODE)
    pdb.gimp_image_insert_layer(image, large_layer, group, 0)
    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE, top_left_x, top_left_y,
                                    LARGE_CELL_WIDTH, LARGE_CELL_HEIGHT)
    finish_selection(image, large_layer)
    draw_label(image, group, color, text, 150, top_left_x, top_left_y, LARGE_CELL_WIDTH, 150)
    return large_layer, group


def draw_city(image, color, city_x, city_y):
    city_layer, group = draw_large_cell(image, color, 'City', city_x, city_y)
    city_space_size = LARGE_CELL_WIDTH / 5
    label_y_position = city_y + LARGE_CELL_HEIGHT * 0.75
    current_x_pos = city_x
    for i in range(0, 4):
        current_x_pos += city_space_size
        pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE, current_x_pos, city_y, 1, LARGE_CELL_HEIGHT)
        finish_selection(image, city_layer)

    gimp.progress_update(0.80)
    label_box_height = LARGE_CELL_HEIGHT / 4
    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE, city_x, label_y_position,
                                    LARGE_CELL_WIDTH, label_box_height)
    finish_selection(image, city_layer, False)
    pdb.plug_in_autocrop_layer(image, city_layer)

    city_labels = ['Bridge', 'Streets', 'Rooftops', 'Bank', 'Sewers']
    gimp.progress_update(0.90)
    current_x_pos = city_x
    for city_label in city_labels:
        draw_label(image, group, color, city_label, 54, current_x_pos, label_y_position + label_box_height / 3,
                   city_space_size, label_box_height)
        current_x_pos += city_space_size


def initialize(image, opacity, filename):
    pdb.gimp_context_set_foreground(WHITE)
    pdb.gimp_context_set_opacity(opacity)
    pdb.gimp_context_set_paint_mode(LAYER_MODE_NORMAL)
    pdb.gimp_context_set_stroke_method(STROKE_LINE)
    pdb.gimp_context_set_line_width(3)
    pdb.gimp_context_set_antialias(1)
    gimp.progress_init("Drawing playmat")
    load_pic_and_transform_perspective(image, filename)
    progress = 0.10
    return progress


def draw_single_cells(image, single_cells, color, progress):
    for single_cell in single_cells:
        draw_single_cell_with_label(image, single_cell[0], single_cell[1], single_cell[2], color)
        progress += 0.05
        gimp.progress_update(progress)


def draw_hq_and_city(image, color, large_cell_x):
    hq_y = image.height - OUTSIDE_GAP - LARGE_CELL_HEIGHT
    draw_large_cell(image, color, 'HQ', large_cell_x, hq_y)
    gimp.progress_update(0.75)
    city_y = hq_y - ROW_GAP - LARGE_CELL_HEIGHT
    draw_city(image, color, large_cell_x, city_y)
    gimp.progress_update(1)


def draw_legendary_playmat_28_by_14(image, filename, opacity, color, include_extra_cell):
    LAST_COLUMN_X = image.width - OUTSIDE_GAP - CELL_WIDTH
    SECOND_LAST_COLUMN_X = LAST_COLUMN_X - CELL_WIDTH - COLUMN_GAP
    progress = initialize(image, opacity, filename)
    gimp.progress_update(progress)

    single_cells = [('', OUTSIDE_GAP, OUTSIDE_GAP,), ('Mastermind', OUTSIDE_GAP, SECOND_ROW_Y,),
                    ('Scheme', OUTSIDE_GAP, THIRD_ROW_Y,), ('Escaped', SECOND_COLUMN_X, OUTSIDE_GAP,),
                    ('Strikes', SECOND_COLUMN_X, SECOND_ROW_Y,), ('Twists', SECOND_COLUMN_X, THIRD_ROW_Y,),
                    ('Bystanders', LAST_COLUMN_X, OUTSIDE_GAP,), ('S.H.E.I.L.D.', LAST_COLUMN_X, SECOND_ROW_Y,),
                    ('Sidekicks', LAST_COLUMN_X, THIRD_ROW_Y,), ('Wounds', SECOND_LAST_COLUMN_X, OUTSIDE_GAP,),
                    ('Villian Deck', SECOND_LAST_COLUMN_X, SECOND_ROW_Y,),
                    ('Hero Deck', SECOND_LAST_COLUMN_X, THIRD_ROW_Y,)]
    if include_extra_cell is False:
        single_cells.pop(0)
    draw_single_cells(image, single_cells, color, progress)
    large_cell_x = OUTSIDE_GAP + CELL_WIDTH * 2 + COLUMN_GAP + MAIN_SECTION_GAP
    draw_hq_and_city(image, color, large_cell_x)


def draw_legendary_playmat_24_by_14(image, filename, opacity, color):
    LAST_COLUMN_X = image.width - OUTSIDE_GAP - CELL_WIDTH
    SECOND_LAST_COLUMN_X = LAST_COLUMN_X - CELL_WIDTH - COLUMN_GAP
    THIRD_COLUMN_X = SECOND_COLUMN_X + CELL_WIDTH + COLUMN_GAP

    progress = initialize(image, opacity, filename)
    gimp.progress_update(progress)

    single_cells = [('Scheme', OUTSIDE_GAP, OUTSIDE_GAP,), ('Mastermind', OUTSIDE_GAP, SECOND_ROW_Y,),
                    ('S.H.E.I.L.D.', OUTSIDE_GAP, THIRD_ROW_Y,), ('Twists', SECOND_COLUMN_X, OUTSIDE_GAP,),
                    ('Strikes', SECOND_COLUMN_X, SECOND_ROW_Y,), ('Sidekicks', SECOND_COLUMN_X, THIRD_ROW_Y,),
                    ('Bystanders', LAST_COLUMN_X, OUTSIDE_GAP,), ('Villian Deck', LAST_COLUMN_X, SECOND_ROW_Y,),
                    ('Hero Deck', LAST_COLUMN_X, THIRD_ROW_Y,), ('Wounds', SECOND_LAST_COLUMN_X, OUTSIDE_GAP,),
                    ('Escaped', THIRD_COLUMN_X, OUTSIDE_GAP,)]
    draw_single_cells(image, single_cells, color, progress)
    large_cell_x = OUTSIDE_GAP + CELL_WIDTH * 2 + COLUMN_GAP * 2 + 15
    draw_hq_and_city(image, color, large_cell_x)


def redraw_single_cell_layer_group(image, new_cell_label_text, color):
    active_layer_group = pdb.gimp_image_get_active_layer(image)
    print(active_layer_group.name)
    child_ids = pdb.gimp_item_get_children(active_layer_group)[1]
    print(child_ids)
    label_layer = gimp.Item.from_id(child_ids[0])
    print(label_layer.name)
    print(label_layer.offsets)
    x, y = label_layer.offsets
    pdb.gimp_image_remove_layer(image, active_layer_group)
    draw_single_cell_with_label(image, new_cell_label_text, x, y, color)


register(
  "draw-28in-by-14in-legendary-playmat",                    # procedure name for whatever
  "Draw 28in x 14in Playmat",                               # blurb
  "Generate a Legendary playmat.",                          # help message
  "Mike F", "Mike F", "Sept 2021",                          # author, copyright, year
  "Draw 28in x 14in Playmat",                               # menu name
  "*",                                                      # type of images we accept
  [                                                         # Parameters
      (PF_IMAGE, "image", "Takes current image", None),
      (PF_FILENAME, "filename", "Filename", None),
      (PF_INT, "opacity", "Opacity of Cells", 20),
      (PF_COLOR, "color", "Label Text Outline Color", (0, 0, 0)),
      (PF_BOOL, 'include_extra_cell', "Include Extra Cell in Top Left", True)
  ],
  [],                                                      # output / return parameters
  draw_legendary_playmat_28_by_14,                         # python function that will be called
  menu="<Image>/Filters/Legendary"
)


register(
  "draw-24in-by-14in-legendary-playmat",                            # procedure name for whatever
  "Draw 24in x 14in Playmat",                               # blurb
  "Generate a Legendary playmat.",                          # help message
  "Mike F", "Mike F", "Sept 2021",                          # author, copyright, year
  "Draw 24in x 14in Playmat",                               # menu name
  "*",                                                      # type of images we accept
  [                                                         # Parameters
      (PF_IMAGE, "image", "Takes current image", None),
      (PF_FILENAME, "filename", "Filename", None),
      (PF_INT, "opacity", "Opacity of Cells", 15),
      (PF_COLOR, "color", "Label Text Outline Color", (0, 0, 0))
  ],
  [],                                                      # output / return parameters
  draw_legendary_playmat_24_by_14,                         # python function that will be called
  menu="<Image>/Filters/Legendary"
)


register(
  "replace-single-cell-layer-group",                                # procedure name for whatever
  "Replace a single cell layer group",                              # blurb
  "Replace a single cell layer group (ie change the name)",         # help message
  "Mike F", "Mike F", "Sept 2021",                                  # author, copyright, year
  "Replace Single Cell Layer Group",                                # menu name
  "*",                                                              # type of images we accept
  [                                                                 # Parameters
      (PF_IMAGE, "image", "Takes current image", None),
      (PF_STRING, 'new_cell_label_text', 'New Cell Label Text', ''),
      (PF_COLOR, "color", "Label Text Outline Color", (0, 0, 0))
  ],
  [],                                                               # output / return parameters
  redraw_single_cell_layer_group,                                   # python function that will be called
  menu="<Image>/Filters/Legendary"
)


main()
