## Using the manual creation files in gimp
First thing to note here is that there are some example images I created under the `example_images` folder. I do not own any of these images and will remove them at the request of the creator or gladely link to their page. All were borrowed off of HD wallpaper pages.

### Setup
1. Install the text outline plugin here: https://github.com/tamius-han/gimp-outline
2. Might have to fix plugins for Ubuntu 20.04: https://bugs.launchpad.net/ubuntu/+source/gimp/+bug/1881684
3. Install the font for Legendary: https://fontzone.net/font-download/percolator
    Instructions for Linux are here Installed the fonts as here: https://linuxconfig.org/how-to-install-fonts-on-ubuntu-20-04-focal-fossa-linux/

### Using your own image
1. Open up `manual_creation/xmen.xcf` file.
2. Create a new layer for your image and transform it to cover the edges of the page. Make sure this is above the xmen layer and under the play area layers.
3. Export to jpeg

**Note** If you move any of the play area layers or change the text you may need to delete the text-outline layer and recreate it.