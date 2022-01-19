# Clockify hour tracker

This script helps you to track your weekly hours for [clockify.me](clockify.me).
Given your weekly hours and from when you want to start tracking it will give you your NET hours that you still have to work, or are in overtime.
It supports calculating in the holidays with the [holidays library](https://github.com/dr-prodigy/python-holidays).
You can configure the workspace, client and a white or blacklist of projects.

## Usage

```bash
python3 clockify_time_tracker.py --weekly-hours 20 --start-date 01/01/2022 --workspace "Your Workspace" --client "Your Client" --project-list "Project 1" "Project 2" --whitelist
```

* `--weekly-hours`: how many hours you should work on the client project per week
* `--start-date`: the date from which you want to track your time
* `--workspace`: your clockify workspace (uses default if not specified)
* `--client`: your client name
* `--project-list`: a list of project names that you want to track
* `--whitelist`: if `True` all projects except the ones in `--project-list` are ignored
* `--holidays-country`: 2 letters of the country where you want to count holidays
* `--holidays-prov`: the province shortform
* `--holidays-state`: the state shortform

## Config

You can store your configuration in a `config.yaml` file in the same folder as the script. A default config will be generated when you run the script the first time.
The config can be overwritten by the cli args descibed above.

```yaml
weekly_hours: 20
start_date: 01/01/2022
workspace: Your Workspace
client: Your Client
project_list:
  - Project 1
  - Project 2
whitelist: false
holidays_country: DE
holidays_prov: BY
holidays_state: Bavaria
```

## License

This software is licensed under the [MIT License](LICENSE).
