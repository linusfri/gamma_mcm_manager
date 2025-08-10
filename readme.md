# GAMMA MCM MANAGER

## What is it?
A simple tool to be able to store certain settings in a json file and merge these with new versions of MCM settings. This allows you to keep certain mod settings pinned while allowing other mod settings to be updated.

## Why?
For me it's bothering to keep up to speed with new changes to the MCM values for different GAMMA mods everytime GAMMA is updated. On one hand i don't want to redo my mod settings everytime a new GAMMA version is released, but i also don't want to overwrite everything with my old MCM values. There are certain settings i always change but these are a small subset of all the mod settings available. So i'd rather keep these settings in a separate json file and merge these with each new version of MCM values.

## How to use
1. Download latest release and unzip to a folder
2. Place ``axr_options.ltx`` and ``settings.json`` in the ``mcm_manager`` folder which you created in step 1 **(see example folder in this repo for ``settings.json`` reference)**. The axr_options.ltx can be found in your gamma install path under ``mods/G.A.M.M.A. MCM values - Rename to keep your personal changes/gamedata/configs`` ![Files](/images/file_hierarchy.png)

3. Run mcm_manager.exe
4. Make sure the settings are written to axr_options.ltx
5. Rename the ``G.A.M.M.A. MCM values - Rename to keep your personal changes`` to ``G.A.M.M.A. MCM values - Saved``
6. Place the merged ``axr_options.ltx`` file in ``mods/G.A.M.M.A. MCM values - Saved/gamedata/configs``

## To generate a json settings file based on the difference between your existing axr_options.ltx file and the default one
1. Place the default axr_options.ltx and your edited **axr_options_saved.ltx** file in the same directory. As of now the file has to be named **axr_options_saved.ltx**. Will make the tool more flexible in the future.
2. Goto the section "How to use" above.

## What does it do?
It's a simple script that reads the ``settings.json`` file and then looks for corresponding settings in ``axr_options.ltx``. If it finds a corresponding setting in ``axr_options.ltx``, it will be overwritten with the setting in ``setting.json``.

If a setting in ``settings.json`` doesn't exist in ``axr_options.ltx``, then that setting will be appended to the ``[mcm]-section`` in ``axr_options.ltx``.

Everytime the program is run, a backup is created with a datetime stamp. This way you always have a file to go back to if things go wrong.