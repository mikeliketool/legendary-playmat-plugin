# legendary-playmat-plugin
Welcome!. This plugin will allow you to create either 28in x 14in or 24in x 14in Legendary playmats.

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
Right now there are two available options for download that are already in xcf format: [24 by 14](https://legendary-playmat-templates.s3.amazonaws.com/24_by_14_base_template.xcf) and [28 by 14](https://legendary-playmat-templates.s3.amazonaws.com/28_by_14_base_template.xcf).

## Drawing a full playmat
1. Open GIMP and select File > Open. Select an xcf file
2. From the menu in GIMP select Filters > Legendary > Draw 28in x 14in Playmat (or the 24 inch option if you prefer)
3. Next to the Filename widget select the file icon. Browse to an image file on your system and select it. Click save.
4. You may update how opaque you want your cells (1-100)
5. You may pick a font for your playmat.
6. Select the colour you want for the text outline for the cell labels (Scheme, Mastermind, etc)
7. Click OK
8. Once the playmat is rendered select File > Export. Give your file a name and make sure it's ok jpg extension.
9. Enjoy!

## Replacing a Layer Group
You may want to change the text of a single cell lable. To do so do the following:
1. Select the layer group you want to replace
2. Select Filters > Legendary > Replace Single Cell Layer Group
3. Enter the new name you want.
4. You may also change the outline color and the font if you like.
4. Click OK


[Manual Creation Instructions](./docs/manual_creation.md)
