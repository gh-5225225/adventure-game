import sys
import json

from messages import getmsg


class room():
    def __init__(self, pos, items, things, name):
        self.pos = pos
        self.items = items
        self.things = things
        self.name = name


def search(searchlist, item):
    for index, i in enumerate(searchlist):
        if item == i:
            return index


def do_action(action, thing, ITEM):
    #The thing and item are needed to be able to rerun functions using MATCH
    #Do_action is only done a few times in the code, so this shouldn't be too
    #bad, but a better way would be preferable

    for item in action.split(";"):
        act = item.split(" ")
        if act[0] == "TAKE":
            try:
                inventory.remove(" ".join(act[1:]))
                print(getmsg("TAKE-ACT").format(
                    thing["name"], " ".join(act[1:])))
            except ValueError:
                print(getmsg("TAKE-ACT-FAILED").format(
                    thing["name"], " ".join(act[1:])))
        elif act[0] == "GIVE":
            inventory.append(" ".join(act[1:]))
            print(getmsg("GIVE-ACT").format(thing["name"], " ".join(act[1:])))
        elif act[0] == "TELEPORT":
            global playerpos
            playerpos = tuple(map(int, act[1].split(",")))
            print(getmsg("TELE-ACT").format(thing["name"]))
        elif act[0] == "MATCH":
            prompt = " ".join(act[1:]).split(",")[0]
            value = " ".join(act[1:]).split(",")[1]
            instr = input(prompt)
            actions = thing["actions"]
            if instr == value:
                do_action(actions["_{}_yes".format(ITEM)], thing, ITEM)
            else:
                do_action(actions["_{}_no".format(ITEM)], thing, ITEM)
        elif act[0] == "COMP":
            prompt = " ".join(act[1:]).split(",")[0]
            value = " ".join(act[1:]).split(",")[1]
            instr = input(prompt)
            try:
                actions = thing["actions"]
                if int(instr) > int(value):
                    do_action(actions["_{}_high".format(ITEM)], thing, ITEM)
                elif int(instr) < int(value):
                    do_action(actions["_{}_low".format(ITEM)], thing, ITEM)
                elif int(instr) == int(value):
                    do_action(actions["_{}_equal".format(ITEM)], thing, ITEM)
                else:
                    #This REALLY should never happen
                    assert False
            except ValueError:
                print(getmsg("NAN"))
        elif act[0] == "SAY":
            print(" ".join(act[1:]))


def findroom(pos):
    for item in rooms:
        if item.pos == list(pos):
            return item


def roomexists(pos):
    if findroom(pos) is None:
        return False
    else:
        return True


def moveplayer(ppos, pos):  # Movement is reletive to current position
    new = (ppos[0] + pos[0], ppos[1] + pos[1])
    if roomexists(new):
        global playerpos
        playerpos = new
        return True  # Not an ideal way of returning a status, but it'll do.
    else:
        return False

playerpos = (0, 0)
rooms = []
inventory = []

with open("rooms.dat") as roomfile:
    for r in json.loads(roomfile.read()):
        rooms.append(room(r["pos"], r["items"], r["things"], r["name"]))

try:
    with open("save.json") as savefile:
        savedata = json.load(savefile)
        playerpos = savedata["pos"]
        inventory = savedata["items"]
except FileNotFoundError:
    pass
    #No save file, don't bother creating one yet

while True:
    instr = input(": ").split(" ")
    #Oh joy, text parsing code
    if instr == [""]:
        pass
    #Moving player
    elif instr[0] in ("move", "go"):
        try:
            if instr[1] in ("north", "up"):
                direction = [0, 1]
            if instr[1] in ("east", "right"):
                direction = [1, 0]
            if instr[1] in ("south", "down"):
                direction = [0, -1]
            if instr[1] in ("west", "left"):
                direction = [-1, 0]

            if moveplayer(playerpos, direction):
                print(getmsg("NEW-ROOM"))
            else:
                print(getmsg("NO-DOOR"))
        except IndexError:
            print(getmsg("NO-DIR"))
        except NameError:
            print(getmsg("INVALID-DIR"))
    #Getting items
    elif instr[0] in ("take"):
        if len(instr) == 1:
            print(getmsg("NO-ITEM"))
        else:
            room = findroom(playerpos)
            if instr[1] in ("all", "everything"):
                for item in room.items:
                    inventory.append(item)
                room.items = []
            else:
                for item in room.items:
                    if item == " ".join(instr[1:]):
                        inventory.append(item)
                        room.items.remove(item)
                        break
                else:
                    print(getmsg("NO-ITEM"))
    elif instr[0] in ("inv", "inventory"):
        for item in inventory:
            print (item)

    elif instr[0] in ("search", "look"):
        print(getmsg("LOOK-NAME").format(findroom(playerpos).name))
        print(getmsg("LOOK-ITEMS"))
        for item in findroom(playerpos).items:
            print(" " + item)
        print(getmsg("LOOK-THINGS"))
        for item in findroom(playerpos).things:
            print(" " + item["name"])

    elif instr[0] in ("use"):
        if " ".join(instr[1:search(instr, "on")]) in inventory:
            ITEM = " ".join(instr[1:search(instr, "on")])
            thing = ""
            for item in findroom(playerpos).things:
                if item["name"] == " ".join(instr[search(instr, "on") + 1:]):
                    thing = item
                    break
            if thing == "":
                print(getmsg("NO-THING"))
            else:
                try:
                    action = thing["actions"][ITEM]
                    do_action(action, thing, ITEM)
                except KeyError:
                    pass
                    #This thing can't handle this item
    elif instr[0] in ("help"):
        print(getmsg("HELPTEXT"))
    elif instr[0] in ("quit"):
        with open("save.json", "w") as savefile:
            savedat = {"pos": playerpos, "items": inventory}
            json.dump(savedat, savefile)
        sys.exit(0)
    else:
        print(getmsg("INVALID-COMMAND").format(" ".join(instr)))
        pass
