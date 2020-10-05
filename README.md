# Turtle Killer

This is a helper script to try and delete every possible related items to the infamous Turtle Plugin.

# The Goal
The Turtle Plugin is a virus for most pipelines, and I am sure that most studios and pipelines have their own ways to address the issue, so here is my own that I use if I ever come across this annoying plugin.

The main function will:
1. Finding all nodes in the scene and deleting them
2. Unloading the plugin if it is loaded
3. Looks for the mll plugin and deletes it.
4. Deletes the shelf inside Maya
5. Deletes the shelf mel file from disk

To run it, simple call:
```python
kill_the_turtle()
```

Optionially, you can call individual functions to use in your own way:

## Example 1:
If you only wanted to delete the turtle shelf
```python
delete_turtle_maya_shelve()
```

## Example 2:
If you only wanted to find all the turtle nodes in the scene
```python
find_turtle_nodes()
```
