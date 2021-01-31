import client
import ast
import random
import time


class Agent:
    def __init__(self):
        self.c = client.Client('127.0.0.1', 50001)
        self.res = self.c.connect()
        random.seed()  # To become true random, a different seed is used! (clock time)
        self.goalNodePos = (0, 0)
        self.state = (0, 0)
        self.reward = 0
        self.qTable = {}

    def getGoalPosition(self):
        return ast.literal_eval(self.c.execute("info", "goal"))

    def getSelfPosition(self):
        return ast.literal_eval(self.c.execute("info", "position"))

    def getRewards(self):
        return ast.literal_eval(self.c.execute("info", "rewards"))

    def getRewardDict(self, rewards, max_coord):
        rewards_dict = {}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                rewards_dict[str((x, y))] = rewards[x][y]
        return rewards_dict

    def getConnection(self):
        return self.res

    def getMaxCoord(self):
        return ast.literal_eval(self.c.execute("info", "maxcoord"))

    def getTargets(self):
        return ast.literal_eval(self.c.execute("info", "targets"))

    def getListTargets(self, targets, max_coord):
        targets_list = []
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                if targets[x][y] == 1:
                    targets_list.append((x, y))
        return targets_list

    def initializeQTable(self, maxCoord):
        q_table = self.qTable
        for x in range(maxCoord[0]):
            for y in range(maxCoord[1]):
                self.qTable[str((x, y))] = [0, 0, 0, 0]
        # print("QTable initialized: ", q_table)
        return q_table

    def drawArrows(self, qTable):
        maxCoord = self.getMaxCoord()
        x = 0
        y = 0
        while x < maxCoord[0]:
            while y < maxCoord[1]:
                key = (x, y)
                l = qTable.get(str(key))
                m = max(l)
                ind = l.index(m)
                if ind == 0:
                    self.c.execute("marrow", "north" + "," + str(y) + "," + str(x))
                elif ind == 1:
                    self.c.execute("marrow", "east" + "," + str(y) + "," + str(x))
                elif ind == 2:
                    self.c.execute("marrow", "west" + "," + str(y) + "," + str(x))
                else:
                    self.c.execute("marrow", "south" + "," + str(y) + "," + str(x))
                y += 1
                time.sleep(0.15)
            y = 0
            x += 1

    def randomSearch(self, explorations):
        directions = ["north", "east", "west", "south"]
        i = 1
        maxCoord = self.getMaxCoord()
        t = self.getTargets()
        goalPosition = self.getGoalPosition()
        positions = [self.getSelfPosition()]
        listaSecreta = []
        rewards = self.getRewardDict(self.getRewards(), self.getMaxCoord())
        qTable = self.initializeQTable(maxCoord)
        gamma = 0.9
        while i <= explorations:
            state = random.randint(0, 3)
            lastPosition = self.getSelfPosition()
            self.c.execute("command", directions[state])
            positions.append(self.getSelfPosition())
            if positions[len(positions)-2] != positions[len(positions)-1]:
                listaSecreta.append((positions[len(positions)-2], positions[len(positions)-1], directions[state], rewards[str(lastPosition)], rewards[str(self.getSelfPosition())]))
            if self.getSelfPosition() == goalPosition or self.getSelfPosition() in self.getListTargets(t, maxCoord):
                if i != explorations:
                    self.c.execute("command", "home")
                positions = [self.getSelfPosition()]
                i += 1
                listaSecreta = listaSecreta[::-1]
                x = 0
                while x < len(listaSecreta):
                    if x == 0:
                        if qTable.get(str(listaSecreta[x][0]))[directions.index(listaSecreta[x][2])] < listaSecreta[x][3] + gamma * listaSecreta[x][4]:
                            qTable.get(str(listaSecreta[x][0]))[directions.index(listaSecreta[x][2])] = listaSecreta[x][3] + gamma * listaSecreta[x][4]
                    else:
                        if qTable.get(str(listaSecreta[x][0]))[directions.index(listaSecreta[x][2])] < listaSecreta[x][3] + gamma * qTable.get(str(listaSecreta[x-1][0]))[directions.index(listaSecreta[x-1][2])]:
                            qTable.get(str(listaSecreta[x][0]))[directions.index(listaSecreta[x][2])] = listaSecreta[x][3] + gamma * qTable.get(str(listaSecreta[x-1][0]))[directions.index(listaSecreta[x-1][2])]
                    x += 1
                listaSecreta = []
        print("QTable new values:", qTable)
        self.drawArrows(qTable)
        input("")


def main():
    print("Starting client!")
    ag = Agent()
    if ag.getConnection() != 1:
        ag.randomSearch(50)


if __name__ == '__main__':
    main()
