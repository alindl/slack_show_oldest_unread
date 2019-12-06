#!/usr/bin/python3
"""
Show the n oldest starred messages,
including colors, age of message,
permalink, the message and sassy teasing.


Usage: python3 show_oldest_saved.py <number of oldest starred> <Slack token>
"""

import webbrowser

import sys
from datetime import datetime
import argparse
import inspect
from colorama import Fore, Style
import slack

PARSER = argparse.ArgumentParser(description='Show oldest N starred messages.')
PARSER.add_argument('count', metavar='N', type=int,
                    help='The number of oldest messages you want to be printed')
PARSER.add_argument('slack_token', metavar='slack_token', type=str,
                    help="The Slack token you can get from " +
                    "https://api.slack.com/custom-integrations/legacy-tokens")

ARGS = PARSER.parse_args()
SLACK_BOT_TOKEN = ARGS.slack_token
COUNT = int(ARGS.count) + 1


def get_stars(self):
    """
    Gets the list of starred messages.

    API CALL conversations.history has a limit of 50 per minute
    It is used about twice, at most thrice

    Documentation says that the response should include the next cursor.
    It doesn't though.
    """
    res = self.stars_list(count=200)
    stars = []
    if not res.get('ok'):
        print(inspect.currentframe().f_code.co_name)
        return False
    page_num = res.get('paging').get('page')
    page_sum = res.get('paging').get('pages')
    json_list = res.get('items')
    for item in json_list:
        stars.append(item)

    while page_num <= page_sum:
        page_num += 1
        res = self.stars_list(count=200, page=page_num)
        if not res.get('ok'):
            print(inspect.currentframe().f_code.co_name)
        else:
            page_num = res.get('paging').get('page')
            json_list = res.get('items')
            for item in json_list:
                stars.append(item)
    return stars


def output_of_the_schwifty_stuff(data, team_id):
    """
    Prints the good stuff, including pretty colors and sassy messages.

    """
    message = data.get('message')
    then = datetime.fromtimestamp(int(float(message.get('ts'))))
    print("This message is from: ", then)
    now = datetime.now()
    delta = now - then
    print("Which means, it's ", delta.days, "days old.")
    if delta.days > 365:
        print(Fore.RED + "More than a year? Did the banana bunchy top virus get you?")
    if 365 >= delta.days > 180:
        print(Fore.MAGENTA + "More than half a year? Get your veggies together dude.")
    if 180 >= delta.days > 30:
        print(Fore.YELLOW + "More than a month? Meh.")
    if 30 >= delta.days > 14:
        print(Fore.GREEN + "More than two weeks? Okay, I guess.")
    if delta.days <= 14:
        print(Fore.CYAN + "Two weeks or less? Are you going back to drinking coffee?")

    print(Fore.BLUE + "https://app.slack.com/client/" + team_id +"/" +
          data.get('channel') + "/thread/" + data.get('channel') +
          "-" + message.get('ts'))
    # What the veggy Slack? Why call the thing permalink and have it be useless?

    # message.get('permalink') + "?thread_ts=" + message.get('ts') +
    # "&cid=" + data.get('channel'))

    print(Fore.LIGHTWHITE_EX + "---------------------------------------------------")
    print(Style.RESET_ALL)
    print(message.get('text'), "\n")
    print(Fore.LIGHTWHITE_EX + "---------------------------------------------------")
    print(Style.RESET_ALL)


# Initialize the connection to the slackbot
SLACK_CLIENT = slack.WebClient(token=SLACK_BOT_TOKEN)
STARS = get_stars(SLACK_CLIENT)
TEAM_INFO = SLACK_CLIENT.team_info()
TEAM_ID = TEAM_INFO.get('team').get('id')
# pylint: disable=C0103
usr_input = ''
if COUNT < 1:
    print("Don't be cheeky, this just spams your terminal.")
    sys.exit()
if COUNT == 1:
    print("Seriously, what did you expect?")
MAX_RUNS = len(STARS[:-COUNT:-1])
if STARS:
    num_run = 0
    for star in STARS[:-COUNT:-1]:
        output_of_the_schwifty_stuff(star, TEAM_ID)
        num_run += 1
        if num_run < MAX_RUNS:
            print("\n\n")
        if COUNT == 2:
            while usr_input.lower() not in ['y', 'n']:
                usr_input = input("Do you wanna just open the thing? [Y/n] : ")
                if usr_input.lower() == 'y' or '\n':
                    webbrowser.open("https://app.slack.com/client/" + TEAM_ID +
                                    "/" + star.get('channel') + "/thread/" +
                                    star.get('channel') + "-" + star.get('message').get('ts'))
                    #star.get('message').get('permalink') + "?thread_ts=" +
                    #star.get('message').get('ts') +
                    #"&cid=" + star.get('channel'))
                    break
                elif usr_input.lower() != 'n':
                    print("Instructions. Can you read them?")
