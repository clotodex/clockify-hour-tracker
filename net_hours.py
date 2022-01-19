#!/usr/bin/python3

"""
calls curl and converts output if successful to json
curl -H "content-type: application/json" -H "X-Api-Key: yourAPIkey" -X GET https://api.clockify.me/api/v1/user
"""

import argparse
import datetime
import json
import subprocess
import sys
from typing import List

import pandas as pd
import yaml

API_KEY = open("./clockify.api.key").read().strip()


def to_date(date: str) -> pd.Timestamp:
    return pd.to_datetime(date, format="%d/%m/%Y")


def api_call(endpoint):
    # silent
    cmd = [
        "curl",
        "-s",
        "-H",
        "content-type: application/json",
        "-H",
        f"X-Api-Key: {API_KEY}",
        "-X",
        "GET",
        f"https://api.clockify.me/api/v1{endpoint}",
    ]

    try:
        output = subprocess.check_output(cmd)
        result = json.loads(output)
        return result

    except subprocess.CalledProcessError as e:
        print("error:", e)
        exit(1)


def main(
    weekly_hours: int,
    start_date: str,
    workspace_name: str,
    client_name: str,
    project_list: List[str],
    whitelist: bool = False,
):

    start_date = to_date(start_date)

    # get logged in user
    user = api_call("/user")
    user_id = user["id"]

    # get all workspaces
    workspaces = api_call("/workspaces")
    print("workspaces:")
    for w in workspaces:
        print("-", w["name"])
    ws_id = workspaces[0]["id"]

    # get all clients
    clients = api_call("/workspaces/" + ws_id + "/clients")

    # get id of client_name
    client_id = None
    for c in clients:
        if c["name"] == client_name:
            client_id = c["id"]
            print(f"found client: {c['name']}")
            break
    else:
        print(f"ERROR: could not find client: {client_name}")
        exit(1)

    # get all projects of client_name
    projects = api_call("/workspaces/" + ws_id + "/projects?clients=" + client_id)
    print(f"Projects for {client_name}")
    for p in projects:
        print("-", p["name"])

    # remove or keep project list, depending on whitelist variable
    if whitelist:
        projects = [p for p in projects if p["name"] in project_list]
    else:
        projects = [p for p in projects if p["name"] not in project_list]

    # get all time entries of the projects
    all_entries = []

    page = 1
    while True:
        print(f"page: {page}")
        entries = api_call(
            f'/workspaces/{ws_id}/user/{user_id}/time-entries?{"&".join("project=" + p["id"] for p in projects)}&page={page}'
        )
        all_entries += entries
        page += 1
        if not entries:
            break

    print(f"{len(all_entries)} time entries")

    print(f"latest entry: {all_entries[0]['description']}")

    # aggregate the time of all time entries
    hours_worked = 0.0
    for e in all_entries:
        d = e["timeInterval"]["duration"]
        if d is None:
            print("skipping NONE")
            continue
        # convert d from PT2H4M23S format to fractions of hours
        d = d.replace("PT", "")
        d = d.replace("H", "*60+")
        d = d.replace("M", "+")
        d = d.replace("S", "*(1/60)")
        d = d.rstrip("+")
        d = eval(d) / 60
        hours_worked += d

    print()
    print("#######")
    print("SUMMARY")
    print("#######")
    print()
    # weeks (in float) between start_date and now
    weeks = (datetime.datetime.now() - start_date).days / 7
    print(f"weeks worked: {weeks}")

    print(f"hours worked: {hours_worked}")

    # hours I should have worked from start_date to now
    hours_goal = weeks * weekly_hours
    print(f"hours goal: {hours_goal}")

    # how many hours I should have worked
    hours_net = hours_goal - hours_worked
    print(f"NET hours: {hours_net}")

    # how many hours I should have worked until the end of the year
    hours_left = (
        (
            datetime.datetime(datetime.datetime.today().year, 12, 31)
            - datetime.datetime.now()
        ).days
        / 7
        * weekly_hours
    )
    print(f"Hours until end of year: {hours_left}")
    print(f"NET hours until end of year: {hours_left + hours_net}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--weekly-hours", type=float, default=40)
    parser.add_argument("--start-date", type=str, help="dd/mm/YYYY")
    parser.add_argument("--workspace", type=str, help="Your Workspace")
    parser.add_argument("--client", type=str, help="Your Client")
    parser.add_argument("--project-list", type=str, nargs="*", default=[])
    parser.add_argument("--whitelist", action="store_true")
    args = parser.parse_args()

    main(
        weekly_hours=args.weekly_hours,
        start_date=args.start_date,
        workspace_name=args.workspace,
        client_name=args.client,
        project_list=args.project_list,
        whitelist=args.whitelist,
    )
