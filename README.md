# legendary-playmat-plugin
Welcome!. This plugin is a work in progress and will be completed in several steps. Manual creation files for a 24 by 14 playmat are in place now. Next step is to create a plugin to allow creation and placement of layers for any playmat size.

### Setup
1. Might have to fix plugins for Ubuntu 20.04: https://bugs.launchpad.net/ubuntu/+source/gimp/+bug/1881684
2. Install the font for Legendary: https://fontzone.net/font-download/percolator
    Instructions for Linux are here Installed the fonts as here: https://linuxconfig.org/how-to-install-fonts-on-ubuntu-20-04-focal-fossa-linux/

## Adding the plugin to GIMP
1. Download the src/legendary_plugin_extenion.py file from the repo.
2. Inside GIMP program, go to Edit -> Preferences -> Folders -> Plug-Ins and see the folder/path listed.
3. Copy/Move the py file to one of one of those folders.
4. If you're on Linux, you'll have to browse to the file and right click on it, the Properties, Permissions Tab, Allow Execute as Program (to make it executable).
5. Restart GIMP.

## Picking a starting base
Right now there are two available options for download that are already in xcf format: [24 by 14](https://legendary-playmat-templates.s3.amazonaws.com/24_by_14_base_template.xcf) and [28 by 14](https://legendary-playmat-templates.s3.amazonaws.com/28_by_14_base_template.xcf). You can always download another sized template from inked gaming and convert it to an xcf file by importing it into gimp.

## Drawing a full playmat
1. Open GIMP and select File > Open. Select an xcf file
2. From the menu in GIMP select Filters > Legendary > Draw 28in x 14in Playmat
3. Next to the Filename widget select the file icon. Browse to an image file on your system and select it. Click save.
4. Select the colour you want for the text outline for the cell labels (Scheme, Mastermind, etc)
4. Click OK

Right now what should happen is that the file is added to a layer and transformed to fill to the edge of the overall image.
It should also draw the rightmost column.

`PLUGIN TO BE CONTINUED`

[Manual Creation Instructions](./docs/manual_creation.md)
