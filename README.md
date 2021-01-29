# CalibMagnetCalc
Tools to calculate the magnetic field of the Hall probe [calibration magnet](https://gmw.com/product/3474/).

## FEMM/
Scripts to calculate _|B|_ in calibration magnet using axisymmetric geometries.

**Caution: The Yoke geometry is not actually axisymmetric.**

### First time setup steps:
- Install [FEMM 4.2](https://www.femm.info/wiki/HomePage) (Windows native, Wine on Linux)
- If running Wine, the directories may be confusing to navigate, so it is useful to add a symbolic link to the scripts directory in the Wine "Favorties" directory
    ```
    cd ~/.wine/drive_c/users/`whoami`/Favorites
    ln -s REPO_PATH/FEMM/scripts CalibMagnetCalc
    ```
    - When in FEMM, `File->Open Lua Script`, click `Favorites`, and you should now see the scripts directory, named `CalibMagnetCalc`
- Ensure Python and following packages are installed (preferably in a virtual environment):
    -  `numpy`, `matplotlib`, `ezdxf` 

### Run Calculation
1. Generate geometry and main Lua script ("run.lua") using python script:
    - `python scripts/prepare_B_vs_I.py`
    - Commandline Flags (defaults): -g pole gap (75 mm), -i initial current (0 A), -f final current (200 A), -d current increment (20 A)
2. Start FEMM and `File->Open Lua Script`, open `Favorites/CalibMagnetCalc/run.lua`
3. Output CSV data saved to [data](https://github.com/FMS-Mu2e/CalibMagnetCalc/data/) (data files not synced to Github)
