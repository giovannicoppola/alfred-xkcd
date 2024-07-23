# alfred-xkcd
A browser for xkcd comics
![](src/xkcd.png)
If you are an xkcd fan and have ever tried to remember or find a particular comic, you might find this Workflow helpful. 

<a href="https://github.com/giovannicoppola/alfred-xkcd/releases/latest/">
<img alt="Downloads"
src="https://img.shields.io/github/downloads/giovannicoppola/alfred-xkcd/total?color=purple&label=Downloads"><br/>
</a>

# Usage
- Search (default keyword: `xkcd`) or hotkey: list and search xkcd comics. `❤️` will denote favorite, `•` unread comics. 
- Favorite (default keyword: `xk::favs`) or hotkey: favorite xkcd comics in grid view. 
- Random (default keyword: `xk::random`) or hotkey: one random unread xkcd comic. 
- Recent (default keyword: `xk::recent`) or hotkey: recently viewed xkcd comics in grid view. 
 

## While in list, random, or favorite view:
- <kbd>↩️</kbd> show in text view (comic will be marked as read)
-  <kbd>⇧</kbd><kbd>↩️</kbd>: copy comic image to clipboard
- <kbd>⇧</kbd> (QuickLook): QuickLook image (`⇧` or `space` to quit). Using the arrow keys you can quickly review multiple comics (will not be marked as read)
- <kbd>^</kbd><kbd>↩️</kbd>: toggle favorite status
- <kbd>⌘</kbd><kbd>↩️</kbd>: open on `xkcd.com`
-  <kbd>⌥</kbd><kbd>↩️</kbd>: open on `explainxkcd.com` (which has also larger images)

# Updating
- `alfred-xkcd` will download the titles of new comics based on the number of days specified in the `Workflow Configuration` (Refresh Rate variable)
- refresh can be forced with `xk::refresh`


 

# Feedback
... is welcome!
https://github.com/giovannicoppola/alfred-xkcd/issues


# Changelog
- 2024-07-21 version 0.2 added search by comic #ID
- 2024-07-21 version 0.1


