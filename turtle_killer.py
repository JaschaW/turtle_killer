import os
import shutil

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om

def kill_the_turtle():
    """
    This will try and find and delete everything relating to the turtle plugin.
    This includes:
    1. Finding all nodes in the scene and deleting them.
    2. Unloading the plugin if it is loaded.
    3. Looks for the mll plugin and deletes it.
    4. Deletes the shelf inside Maya.
    5. Deletes the shelf mel file from disk.

    :return: None (Well, a happy Pipeline)
    """

    # -- look in scene if there are any turtle nodes
    turtle_nodes = find_turtle_nodes()
    counter = 0
    for turtle in turtle_nodes:
        try:
            unlock_and_delete(turtle)
            counter += 1
        except Exception as e:
            if e:
                om.MGlobal.displayError("Could not delete {0} successfully.".format(turtle))

    om.MGlobal.displayInfo("Found and deleted {0} Turtle Nodes.".format(counter))

    # -- check if it is loaded and unload it
    unload_turtle_plugin()

    # -- find where the turtle rests, and take him out.
    hunt_down_turtle_path()

    # -- delete the shelf if there is one.
    delete_turtle_maya_shelve()

    # -- delete the saved turtle shelf
    delete_saved_turtle_shelf()

def find_turtle_nodes():
    """
    find all possible Turtle nodes within the current maya scene.

    :return: a list of all turtle nodes found

    """

    return [turtle for turtle in cmds.ls("Turtle*")]

def unlock_and_delete(turtle):
    """
    turtle nodes are locked by default, we unlock the node and then we can delete it.

    :param turtle: turtle node that has been found in the scene
    :return:
    """

    # -- unlock the node before it can be deleted.
    cmds.lockNode(turtle, lock=False)
    # -- delete the node
    cmds.delete(turtle)

    om.MGlobal.displayInfo("Deleted {0} successfully.".format(turtle))

    return True

def unload_turtle_plugin():
    """
    Check if the node is currently loaded, if we do operations such as delete on the node while still loaded,
    could cause corrupt scenes down the line.

    :return: True or False
    """

    # -- check if the plugin is loaded
    if cmds.pluginInfo("Turtle.mll", query=True, loaded=True):
        cmds.unloadPlugin("Turtle.mll", force=True)

    return True

def hunt_down_turtle_path():
    """
    Try and find the path from the node (can only be done if loaded).
    As an extra precautionary step we look in the maya bin folder for the node (normal installation destination)
    Because we cannot delete items unless we have admin rights, we move the turtle file to a custom directory that does
    not need admin rights and delete the node off of the machine.

    :return: None
    """

    turtle_path = None
    move_path = join_file_path(os.path.expanduser("~"), "maya")
    # -- we try and query the node for the path
    try:
        turtle_path = cmds.pluginInfo("Turtle.mll", query=True, path=True)
    except Exception as e:
        if e:
            om.MGlobal.displayInfo("Could not find the path from the node.")

    # -- if turtle path is still None, we try and look in the maya bin directory
    if not turtle_path:
        turtle_path = join_file_path(get_maya_bin_plugin_path(), "Turtle.mll")

    # -- if the path has been found we hunt it down
    if turtle_path:
        if os.path.exists(turtle_path):
            if os.path.isfile(turtle_path):
                try:
                    # -- move the node
                    move_file_desitination(turtle_path, move_path)
                    om.MGlobal.displayInfo("Moved the Turtle node to: {0}".format(move_path))
                    # -- delete the node
                    os.remove(os.path.join(move_path, "Turtle.mll"))
                    om.MGlobal.displayInfo("Turtle node has been deleted.")
                except Exception as e:
                    if e:
                        om.MGlobal.displayError("Could not delete the turtle plugin.")

    return

def delete_turtle_maya_shelve():
    """
    We try and delete the TURTLE shelf if it is loaded.

    :return: None
    """

    try:
        # -- finally, if there is a shelf, delete it!!
        top_level_shelves = mel.eval("$tmpVar=$gShelfTopLevel")
        shelves = cmds.tabLayout(top_level_shelves, query=True, childArray=True)
        if "TURTLE" in shelves:
            cmds.deleteUI("TURTLE")
    except Exception as e:
        if e:
            om.MGlobal.displayError("Could not delete the turtle shelf.")

    return

def move_file_desitination(path, move_path):
    """
    Helper function to move files from one destination to another.

    :param path: source path to get file from
    :param move_path: destination path to move the file to

    :return: True if successful
    """

    shutil.move(path, move_path)

    return True

def join_file_path(path, *kwargs):
    """
    Helper function to join user defined file paths correctly.

    :param path: main path that the user would start with
    :param kwargs: optional extra items to add to the final path

    :return: string of normalized file path
    """

    return os.path.normpath(os.path.join(path, *kwargs))

def get_maya_bin_plugin_path():
    """
    We know that the turtle plugin path gets installed in the bin directory,
    we get the maya plugin path and target the bin directory.

    :return: string of plugin path or None
    """

    # -- iterate over all plugin paths found
    for path in os.environ['MAYA_PLUG_IN_PATH'].split(";"):
        if "bin" not in path:
            continue

        return path or None

def delete_saved_turtle_shelf():
    """
    We look for the shelf that has been saved by the turtle and delete it off of the machine.

    :return: None
    """

    # -- default shelf name
    turtle_shelf = "shelf_TURTLE.mel"
    path = join_file_path(os.path.expanduser("~"), "maya", cmds.about(version=True), "prefs", "shelves")

    for shelves in os.listdir(path):
        if shelves == turtle_shelf:
            os.remove(os.path.join(path, turtle_shelf))
            om.MGlobal.displayInfo("Turtle Shelf has been deleted from disk.")

    return
