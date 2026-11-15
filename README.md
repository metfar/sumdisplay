# sumdisp — SUM Display

*X11/RandR output manager, designed for visual comfort. A Python executable with optional symbolic links.*

**Status:** Alpha, functional, and evolving.
**License:** GNU GPL, version 2 or later.

## 1. Project Origin

`sumdisp` was born from a specific need: to adjust displays on various Linux machines for a comfortable, consistent viewing experience, without relying on heavy, resource-intensive tools or permanently altering the physical resolution.

The starting point was the Bash scripts `pantalla`/`disp` and `ajustaBrillo`, which let you query or adjust display settings via `xrandr`. Specifically, `disp` offered different scaling modes—**large** (`1920x1080`), **slim** (`1800x900`), and **normal** (`1:1`)—while `ajustaBrillo` managed brightness and gamma to tailor the visual output to each monitor.

The evolution into `sumdisp` consolidated these operations into a single Python executable. It preserved the original names via aliases, introduced persistent profiles, and added three interaction modes: **CLI, TUI, and GUI**. It was subsequently integrated with `sumUI`, `sumTUI`, and `sumGUI` as part of the SUM ecosystem—a collection of lightweight, reusable tools well-suited even for modest hardware.

The primary objective remains **visual comfort**, rather than replacing the system's default monitor management utility.

## 2. Key Features

- Detects connected outputs using `xrandr --query`, prioritizing the active primary output. If multiple outputs are active, the interfaces provide a monitor selector.
- Displays the **physical mode or resolution** for informational purposes; in the TUI and GUI, only the **logical resolution** is modified via XRandR transformations.
- Allows for a return to **Default** (a `1:1` scale) without misinterpreting `1x1` as a physical resolution. - Adjusts software-based brightness and RGB gamma per output; visual brightness controls support values ​​between **−5 and +5**, while gamma controls use increments of `0.05`.
- Re-applies gamma and brightness settings after any changes to logical scaling, helping to minimize calibration loss caused by geometry adjustments.
- Supports saving and loading **profiles**; prompts for confirmation before overwriting or deleting profiles via the interface.
- Retains the name of the active profile as long as its settings match the current configuration—persisting even across application restarts.
- Maintains an **MRU** (*most recently used*) history of logical resolutions, alongside a separate list of user-defined custom resolutions.
- Provides a local catalogue of known resolutions, featuring descriptive names and sorted by total pixel count.
- Available in **English, French, or Spanish**; English is the default language.
- Includes an `install.sh` script, Python packaging configuration (`pyproject.toml`), and compatibility aliases.

## 3. Requirements and Scope

- GNU/Linux with an **X11** session and access to the X server.
- Python **3.9 or later** (based on the current packaging).
- `xrandr` (typically provided by the `x11-xserver-utils` package on Debian/Ubuntu).
- **CLI:** Operates without requiring a graphical or terminal-based user interface.
- **TUI:** Requires compatible versions of `sumUI`, `sumTUI`, and their dependencies (including the *Rich* library).
- **GUI:** Requires compatible versions of `sumUI`, `sumGUI`, and *Pygame*.

`sumdisp` is **not** a native Wayland display driver, an ICC calibration tool, or a mechanism for controlling physical panel brightness or backlight intensity. The `xrandr --brightness` command modifies the digital output signal; specific behaviour may vary depending on the X server, graphics driver, and compositor in use. > **Important:** The CLI retains the explicit `mode` command for historical compatibility. This command **can** change the physical mode, provided that XRandR reports it as available. TUI/GUI interfaces and profile loading do not modify it.


## 4. Installation

### 4.1 Recommended installer

From the distribution folder:

```sh
./install.sh
```

This installs the executable to `~/bin/sumdisp` (or to the directory defined by `SUMDISP_BIN_DIR`). If `~/bin` is not in your `PATH`, you will need to add it to your shell configuration.

To also install legacy aliases:

```sh
./install.sh --aliases
```

The additional names are `sumdisplay`, `disp`, `pantalla`, `setBright`, and `ajustaBrillo`. The installer avoids overwriting existing files when creating these aliases.

Using a custom destination:

```sh
SUMDISP_BIN_DIR="$HOME/.local/bin" ./install.sh --aliases
```

### 4.2 Manual installation

```sh
install -m755 sumdisp "$HOME/bin/sumdisp"
cd "$HOME/bin"
ln -sfn sumdisp disp
ln -sfn sumdisp pantalla
ln -sfn sumdisp ajustaBrillo
ln -sfn sumdisp setBright
```

### 4.3 Installation as a Python package

```sh
python3 -m pip install --user --no-deps --no-build-isolation .
```

Alternatively, use `./install.sh --pip`. On distributions that enforce **PEP 668**, it is recommended to use `./install.sh` or a virtual environment, rather than modifying the system-managed Python.

The package is published under the Python name **`sumdisplay`** and provides the aforementioned commands. Installation via `pip` does not automatically ensure that the compatible SUM libraries are installed; please check the TUI/GUI requirements.

### 4.4 Initial verification

```sh
sumdisp --version
sumdisp status
sumdisp list
```

The `status` command reports the configuration registered by `sumdisp`; It should not be interpreted as an independent measurement of external changes made by other tools.

## 5. Command-line usage

### 5.1 Status, monitors, and explicit selection

```sh
sumdisp status
sumdisp list
sumdisp --output HDMI-2 status
sumdisp --output eDP-1-1 scale 1600x800
```

`--output` identifies an XRandR output. If omitted, the active primary output is selected—or, failing that, another active/connected output.

### 5.2 Logical resolution

```sh
sumdisp scale 1600x800
sumdisp scale 1920x1080
sumdisp normal
sumdisp restore
```

`scale WIDTHxHEIGHT` uses the XRandR logical scale (`--scale-from`). `normal` and `restore` both reset the scale to `1:1`.

Commands from the legacy scripts are also supported:

```sh
disp grande     # logical scale 1920x1080
disp delgada    # logical scale 1800x900
disp normal     # scale 1:1
```

These can also be executed as `sumdisp` commands.

### 5.3 Gamma and brightness

```sh
sumdisp gamma 0.8:0.85:0.95
sumdisp setbright 0.8
ajustaBrillo 0.8
setBright 0.8
```

The three gamma components correspond to **red:green:blue**. The CLI validation allows gamma values ​​between `0.1` and `10.0`, while the interface sliders cover the practical range of `0.1`–`2.0`. The program supports brightness values from `−5` to `+5`. **Historical reference values, visually adjusted for each device** (these do not constitute a scientific calibration):

```sh
# Main device
sumdisp gamma 0.8:0.85:0.95

# Small device: run this there
sumdisp gamma 0.7:0.7:0.65
```

Negative brightness values may cause the image to appear inverted in certain XRandR configurations. **This is not a guaranteed palette-inversion feature for all drivers.**

To explicitly reset scale, gamma, and brightness to their neutral values:

```sh
sumdisp reset
```

Unlike `normal`, `reset` uses a scale of `1:1`, gamma of `1:1:1`, and brightness of `1.0`.

### 5.4 Profiles

```sh
sumdisp save lectura
sumdisp load lectura
sumdisp delete-profile lectura
```

`save` records the **last applied and saved configuration**; it does not save any pending changes currently in the interface controls.

`load` applies scale, gamma, and brightness, but **ignores any physical `mode` field** present in an older profile.

`delete-profile` via the CLI removes the specified file **without an interactive confirmation prompt**; in the TUI/GUI, confirmation is requested. Deleting a profile does not alter the currently applied display settings.

Profile names may contain ASCII letters, digits, `_`, and `-`, with a maximum length of **64 characters**.

### 5.5 Custom Resolutions

```sh
sumdisp define-scale 1500x850
```

Registers a custom logical resolution, making it available for selection without applying it immediately. Custom resolutions defined within profiles can also be included among the available options.

### 5.6 CLI Support for Physical Mode

```sh
sumdisp mode 1600x900
```

**Advanced/legacy command:** changes the physical mode, provided it is supported by XRandR for that output. This is not part of the standard visual comfort workflow and does not appear in the TUI/GUI.

## 6. TUI and GUI Interfaces

```sh
sumdisp --tui
sumdisp --gui
sumdisp --cli
```

When run without arguments from an interactive terminal, `sumdisp` defaults to the TUI. The `--cli` flag retrieves the current status without launching the interface.

### 6.1 Languages

```sh
sumdisp --tui --lang en
sumdisp --tui --language es
sumdisp --gui --lang fr
```

Supported codes: `en`, `fr`, `es`. The default value is **` en`**. The translation of some messages originating from XRandR or external dependencies may be incomplete.

### 6.2 Editor Layout

The main form uses the same functional structure, whether in a terminal (TUI) or graphical mode:

```text
Display: [eDP-1-1 ▼]             Physical mode: 1366x768 (read-only)

Profile: [Default ▼] [Load]

Resolution: [1600x800 ▼]
[ ] Show resolution catalogue (by size)

Brightness  [==========|---------] 1.40
Gamma R     [========|-----------] 0.80
Gamma G     [========|-----------] 0.80
Gamma B     [=========|----------] 0.90

[ Apply ] [ Save ] [ Delete ] [ Exit ]
```

The display output appears as a selection option only when more than one device is active. Selecting a different monitor or profile from a dropdown menu (ComboBox) **does not automatically apply changes**. Profiles must be loaded using the **Load** button; pending adjustments are applied by clicking **Apply**.

### 6.3 Profiles via the Interfaces

- **Load:** Applies the selected profile.
- **Save:** Opens a dialogue displaying existing profiles, along with an editable name field. Selecting an existing profile copies its name into the field; overwriting a profile requires confirmation.
- **Delete:** Opens a dialogue listing profiles that can be deleted; this requires both a selection and confirmation.
- **Exit:** Closes the application. In the TUI (terminal) version, other actions are designed to keep the editor open.

The label **Current / Actuel / Actual** indicates that the currently applied settings do not match the associated active profile; it does not automatically create a new profile with that name. If the applied settings continue to match the profile, the profile name is retained after clicking **Apply** or restarting the application. ### 6.4 History and Resolution Catalogue

With the **Show resolution catalogue ** checkbox disabled, the selector displays:

1. Custom resolutions that have been used, sorted by most recent use.
2. Predefined resolutions that have been used, also sorted by most recent use.
3. Custom resolutions that have been defined but not yet used.

Headers and separators are for informational purposes only and cannot be applied as resolutions. The MRU (Most Recently Used) history has a hard-coded limit of **24 entries** per output.

Enabling the checkbox reveals a **local catalogue ** of common resolutions (VGA, WXGA, Full HD, QHD, 4K UHD, etc.), sorted by total pixel count (descending), with dimensions used as a tie-breaker. This is a **curated, non-exhaustive** catalogue; there is **no guarantee** that a given monitor will support these sizes as physical display modes.

The **Default** value corresponds to a `1:1` scale. Checking the box or selecting an option from the dropdown menu does not automatically apply the transformation.

### 6.5 Confirmation of Scaling Changes

The graphical editor includes a temporary confirmation step for scaling changes, providing a **15-second** window; if no confirmation is received, the system attempts to revert the changes. The exact behaviour depends on whether the dialogue window remains functional during the geometry update; it is advisable to keep a terminal accessible to run `sumdisp normal` if necessary.

## 7. Configuration and Persistence

Default directory:

```text
~/.config/sumdisp/
├── config.json
└── perfiles/
├── Defecto.json
├── lectura.json
└──...
```

If `XDG_CONFIG_HOME` is defined, `$XDG_CONFIG_HOME/sumdisp/` is used instead.

The configuration stores, among other data, visual settings indexed by **computer name and display output**, resolution history, custom resolutions, and the active profile. Profiles are saved as individual JSON files.

**Do not edit configuration files while `sumdisp` is writing to them.** If monitor settings are modified via another tool, the data stored by `sumdisp` may become out of sync with the actual display state.

## 8. Application Order and Operational Safety

The engine's execution sequence is as follows:

1. Physical mode (applied **only if explicitly requested via the CLI**).
2. Logical scaling transformation (if changed).
3. A brief pause (`0.25 s`) for stabilization.
4. Application of available RGB gamma and brightness settings. 
In the event of a scaling change, colour settings are applied a second time after an additional pause (`0.65 s`).

This two-step application process helps mitigate the loss of gamma/brightness settings that can occur when changing the logical resolution (scaling). It does not, however, replace an actual read of the X server's LUTs (Look-Up Tables).

**Best Practices:**

- Use `sumdisp status` to verify the current state and save it as a known profile.
- Keep a terminal window accessible to run `sumdisp normal` in case a scaling change makes the interface difficult to use.
- Avoid using the `mode` CLI command unless you specifically need to change the physical resolution.
- Note that `reset` restores both gamma and brightness settings, whereas `normal` does not.
- Do not confuse software-based brightness adjustments with hardware-level monitor brightness controls.

## 9. Testing and Diagnostics

The `0.1a19` release includes automated tests for language/output, profile persistence, profile deletion, and mouse events in the TUI:

```sh
python3 test_language_monitors.py
python3 test_profile_persistence.py
python3 test_profile_deletion.py
python3 test_tui_mouse.py
```

These tests use simulations or component-level checks; they **do not** replace actual mouse interaction testing in a real terminal, nor do they substitute for an XRandR hardware verification.

Component version diagnostics:

```sh
python3 - <<'PY'
import inspect;
import sumtui;
import sumgui;
from sumtui.widgets import ComboBox;
from sumgui import easy;
print("sumTUI:", sumtui.__file__);
print("ComboBox:", inspect.signature(ComboBox.__init__));
print("sumGUI:", sumgui.__file__);
print("Slider:", inspect.signature(easy.slider));
PY
```

A common incompatibility arises when installing a new `sumdisp` without first updating the required SUM components. If an interface fails during widget import or creation, verify the paths and the signatures shown above before modifying the application.

## 10. Historical Evolution

This timeline consolidates the development README files; it describes the changes at each stage but **does not** imply that all older implementations remain valid.

| Version | Key Milestone |
|---|---|
| **0.1a01** | First Python executable: XRandR detection, CLI and Bash aliases, local configuration, profiles; text-based TUI and a provisional GUI using Tkinter. |
| **0.1a02** | Preliminary fix for the order of operations and restoration of gamma/brightness settings after scaling. |
| **0.1a03** | Physical resolution hidden within the interfaces; previous profiles no longer trigger changes to the physical mode. |
| **0.1a04** | Initial native interfaces for sumTUI/sumGUI; improvements to the independent application of scaling, gamma, and brightness. |
| **0.1a05** | Sliders for brightness and gamma; first scaling selectors in SUM. |
| **0.1a06** | First graphical dropdown ComboBox with a scroll bar. |
| **0.1a07** | TUI remains persistent after applying, saving, or loading. |
| **0.1a08** | Local catalogue, resolution history, brightness range from −5 to +5. |
| **0.1a09** | History organized into three sections, unapplied custom definitions, and a selector for existing profiles. |
| **0.1a10–0.1a11** | Progressive integration of shared SUM components and compatibility fixes. |
| **0.1a12** | Identification of the active profile and an editable save dialogue. |
| **0.1a13** | Profile and load button positioned above the form; primary actions located below. |
| **0.1a14** | Association of the active profile when applied values ​​match. |
| **0.1a15** | Save dialogs with synchronized selection; `install.sh` and packaging via pip. |
| **0.1a16** | Fixes for graphical dialogue titles and secure profile deletion. |
| **0.1a17** | Support for `en/fr/es` languages, consistent resolution labelling, and selection of multiple outputs. |
| **0.1a18** | Delete button in the main interface; additional translations and an initial attempt to fix click handling in the TUI. |
| **0.1a19** | Further refinement of click detection in the TUI based on the rendered row; simulated tests conducted with varying terminal heights. |

## 11. SUM Architecture and Integration

`sumdisp` acts as a **consumer** of components within the SUM ecosystem:

- **sumUI:** Shared models and contracts for controls and selection.
- **sumTUI:** Terminal-based controls, including lists, ComboBoxes, sliders, dialogues, and keyboard/mouse event handling.
- **sumGUI:** Graphical controls for Pygame, such as dropdown ComboBoxes and sliders.
- **sumdisp:** XRandR detection, scaling logic, persistence, and profile management.

The objective is for a given control to maintain consistent **semantics** across both TUI and GUI environments, avoiding the need to duplicate application logic for each interface.

## 12. Proposed features, not yet implemented in 0.1a19

The following ideas have been discussed and accepted as a direction for future development, but they **should not be confused with options currently available**:

- Configuring and listing themes via `sumdisp` using `--set-theme`, `--theme`, `--show-theme`, and `--list-themes`, with a fallback to the default theme if the selected one does not exist.
- Extending `sumtheme` to define the visual style of sliders using `atstart`, `actual`, and `toend` characters; only **single-cell-wide** characters are supported for the TUI.
- Using a filtered **Character Chart** as an optional selector for slider characters.
- Sorting roles alphabetically in `sumtheme` and maintaining the current selection and scroll position after editing.
- Standardizing and unifying the interfaces for editable ComboBoxes, search functions, validators, grouped lists, and other widgets across sumUI, sumTUI, and sumGUI.
- Generalizing the Save/Load/Delete dialogues for use in other SUM applications.

**Note:** The `--set-theme` and `--list-themes` commands **are not present in the argument parser for `0.1a19`**. They are not documented as currently functional features.

## 13. Known limitations

- This is an **alpha** version: certain aspects of widget integration and mouse event handling require validation across various terminal emulators and X11 environments.
- The simulated mouse test in `0.1a19` does not, by itself, guarantee that the issue is resolved across all terminals.
- External changes to gamma or brightness are not automatically reflected in the persisted state.
- The selection of logical scales does not imply physical support for all listed resolutions. - The translation covers the application texts and integrations, but internal errors originating from dependencies may appear in their original language.
- The persistent theme system and its editing via `sumdisp` are not implemented in this version.

## 14. License

Copyright © 2018–2026 William Martinez Bas.

Free software distributed under the terms of the **GNU General Public License**, version 2 or, at the user's discretion, any later version (**GPL-2.0-or-later**). Please refer to the program's license header and the full text of the corresponding GPL.

<p align=center><b>- oOo -</b></p>

