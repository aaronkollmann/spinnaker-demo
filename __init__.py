# -*- coding: utf-8 -*-
import logging
import os
import sys
import time
from datetime import datetime

import ts3

stop_countdown_signal = False

# get necessary environment variables
try:
    # query connection to server
    ev_username = os.environ["TS3BOT_USERNAME"]
    ev_pw = os.environ["TS3BOT_PASSWORD"]
    ev_server_url = os.environ["TS3BOT_URL"]
    ev_server_port = os.environ["TS3BOT_PORT"]
    ev_protocol = os.environ["TS3BOT_PROTOCOL"]
    ev_vserver_id = os.environ["TS3BOT_VIRTUAL_SID"]


    # required for basic bot functionality
    ev_group_afk = os.environ["TS3BOT_AFK_GID"]
    ev_group_newbie = os.environ["TS3BOT_NEWBIE_GID"]
    ev_welcome_msg = os.environ["TS3BOT_NEWBIE_WELCOME_MESSAGE"]


except KeyError:
    logging.error("Required environment variables not set properly")
    raise


try:
    ev_domain_name = os.environ["TS3BOT_DOMAIN_NAME"]
except KeyError:
    ev_domain_name = ev_server_url

try:
    ev_wtg_url = os.environ["TS3BOT_W2G_URL"]
except KeyError:
    ev_wtg_url = "https://w2g.tv/"

#
# ========================================> FUNCTIONS <================================================
#

def handle_event(event):
    if event.event == "notifycliententerview":

        # client in default group joins
        if event[0]["client_servergroups"] == ev_group_newbie:
            # poke client with message ~Welcome to this TS3, while using it you agree to the rules~
            ts3conn.exec_("clientpoke", clid=event[0]["clid"],
                          msg=ev_welcome_msg)
            logging.info("User in default group joined: Poked him with message.")

    elif event.event == "notifytextmessage":
        possible_commands = {"!commands", "!wtg", "!status", "!reverse", "!countdown", "!ip", "!welcome", "!info"}
        if event[0]["msg"].lower() == "!commands":
            ts3conn.exec_("sendtextmessage", targetmode=3, target="1",
                          msg=possible_commands)
        if event[0]["msg"].lower() == "!wtg":
            ts3conn.exec_("sendtextmessage", targetmode=3, target="1",
                          msg=ev_wtg_url)
        if event[0]["msg"].lower() == "!status":
            ts3conn.exec_("sendtextmessage", targetmode=3, target="1", msg="I am online.")
        if event[0]["msg"].lower()[:8] == "!reverse":
            ts3conn.exec_("sendtextmessage", targetmode=3, target="1", msg=event[0]["msg"][:8:-1])
        if event[0]["msg"].lower() == "!ip":
            ts3conn.exec_("sendtextmessage", targetmode=3, target="1", msg=ev_domain_name)
        if event[0]["msg"].lower()[:10] == "!countdown":
            try:
                limit = int(event[0]["msg"][10:])
                if limit < 1:
                    raise
            except BaseException or IOError:
                ts3conn.exec_("sendtextmessage", targetmode=3, target="1", msg="usage: !countdown <Zahl größer als 0>")
            else:
                while not stop_countdown_signal and limit != -1:
                    ts3conn.exec_("sendtextmessage", targetmode=3, target="1", msg=str(limit))
                    time_before = datetime.now()

                    try:

                        possible_stop_command = ts3conn.wait_for_event(timeout=1)

                    except ts3.query.TS3TimeoutError:
                        continue
                    else:
                        time_delta = datetime.now() - time_before
                        if time_delta.total_seconds() <= 1:
                            time.sleep(1 - time_delta.total_seconds())
                        if possible_stop_command.event == "notifytextmessage":
                            if possible_stop_command[0]["msg"].lower() == "!stop":
                                ts3conn.exec_("sendtextmessage", targetmode=3, target="1",
                                              msg="Countdown stopped")
                                break
                    limit -= 1
        if event[0]["msg"].lower()[:10] == "!welcome":
            ts3conn.exec_("sendtextmessage", targetmode=3, target="1", msg=ev_welcome_msg)
        if event[0]["msg"].lower()[:10] == "!info":
            ts3conn.exec_("sendtextmessage", targetmode=3, target="1", msg="I am currently welcoming users with GID " + ev_group_newbie + " the following message: "+ ev_welcome_msg)
            ts3conn.exec_("sendtextmessage", targetmode=3, target="1", msg="This servers domain name is " + ev_domain_name)
            ts3conn.exec_("sendtextmessage", targetmode=3, target="1", msg="I am using " + ev_protocol)





def main(ts3conn):
    # register for events on TS
    ts3conn.exec_("servernotifyregister", event="server")
    ts3conn.exec_("servernotifyregister", event="textserver")

    while True:
        ts3conn.send_keepalive()
        try:
            event = ts3conn.wait_for_event(timeout=5)
        except ts3.query.TS3TimeoutError:  # when timeout of ts3conn.wait_for_event() just continue and send empty query

            # FIXME code only gets executed if timeout occurs, could be skipped if everytime event happens in 5 mins, should be in own thread
            for client in ts3conn.exec_("clientlist"):
                if client["client_type"] == "0":  # select non query clients
                    client_info_str = ts3conn.exec_("clientinfo", clid=client["clid"])

                    if int(client_info_str[0]["client_idle_time"]) >= 600000 and ev_group_afk not in client_info_str[0]["client_servergroups"]:
                        ts3conn.exec_("servergroupaddclient", sgid=int(ev_group_afk),
                                      cldbid=client["client_database_id"])
                    elif int(client_info_str[0]["client_idle_time"]) < 600000 and ev_group_afk in client_info_str[0]["client_servergroups"]:
                        ts3conn.exec_("servergroupdelclient", sgid=int(ev_group_afk),
                                      cldbid=client["client_database_id"])

            continue
        else:
            handle_event(event)


if __name__ == "__main__":
    # init logging
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR,
                        format="%(asctime)s %(levelname)s - %(name)s - %(message)s", datefmt='%d.%m.%Y %H:%M:%S')

    logging.info("Starting TS3BOT")

    connection_string = f"{ev_protocol}://{ev_username}:{ev_pw}@{ev_server_url}:{ev_server_port}"

    # create connection to TS
    with ts3.query.TS3ServerConnection(connection_string) as ts3conn:
        ts3conn.exec_("use", sid=int(ev_vserver_id))
        main(ts3conn)
