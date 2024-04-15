# **Wine-Runner**

Command line wrapper around [WINE](https://www.winehq.org/) and [UMU](https://github.com/Open-Wine-Components/umu-launcher) for running Windows applications.

# **Usage**

Create a configuration file for the application at the wine-runner configuration directory (usually at **$HOME/.config/wine-runner/profiles**, can be changed to somewhere else by specifying the **WRUNNER_CONFIG_DIR** environment variable).

Configuration file example:

```toml
# /home/user/.config/wine-runner/profiles/example_file

[profile]
profile_id = "example"
wine_directory = "$HOME/.local/opt/wine-tkg-valve-exp-bleeding/usr/bin"
application_directory = "$XDG_DATA_HOME/Games/example"

[profile.environment_variables]
WINEDEBUG = "-all"
WINEFSYNC = "1"

[profile.executables_aliases]
launcher = "$XDG_DATA_HOME/Games/example/pfx/drive_c/Program Files (x86)/Launcher/Launcher.exe"
```

**Add Wine-Runner to the PATH environment variable**

Autocomplete and whatnot depends on being able to find the **wrunner** command, in other words wine-runner directory must be reachable from the **PATH** environment variable (change the path accordingly):

```sh
export PATH="$PATH:$HOME/.local/opt/wine-runner"
```

Add it to the .bashrc, .zshrc, etc to make it automatically sourced at startup.

**Wine-Runner's syntax**

The syntax for running it usually goes like:

```sh
wrunner <profile_id_here> <verb>/<flags> <aliases> <args>

```

For a extensive list of possibilities run:

```sh
wrunner --help
```

**Creating the prefix**

```sh
wrunner <profile_id_here> init
```

**Running the launcher**
The "example" is the profile_id specified in the configuration file.

```sh
wrunner <profile_id_here> --run <executable_alias_here> <args_if_any>
```

**Installing DXVK**

```sh
wrunner <profile_id_here> install-dxvk
```

# **Autocomplete**

For now there's only autocomplete for Bash and ZSH.

**Bash**

Call **source** to the path of the bash version of the autocomplete:

```sh
source $HOME/.local/opt/wine-runner/completion/bash/_wrunner
```

Add the command above the **.bashrc** to make it automatically sourced at startup.

**ZSH**

Add the path of the autocomplete to the Zsh's **fpath** environment variable and source the file:

```sh
fpath=($HOME/.local/opt/wine-runner/completion/zsh $fpath)
source $HOME/.local/opt/wine-runner/completion/zsh/_wrunner
```

Or simply add it to the **.zshrc** to make it automatically sourced at startup:

```sh
fpath=($HOME/.local/opt/wine-runner/completion/zsh $fpath)
autoload -U compinit
compinit
```
