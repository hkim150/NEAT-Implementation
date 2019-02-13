import random


class Genome:
    INPUT, HIDDEN, OUTPUT = 0, 1, 2
    nextId = 0
    disable_chance = 0.7
    mutation_chance = 0.8
    perturbation_chance = 0.9
    nextInnovationNumber = 0

    def __init__(self):
        self.nodes = []
        self.connections = []

    def mutate(self):
        for connection in self.connections:
            random_val = random.random()*4 - 2
            if random.random() < Genome.perturbation_chance:
                connection.weight *= random_val
            else:
                connection.weight = random_val

    def add_node_mutation(self):
        connection = random.choice(self.connections)
        self.add_node(connection)

    def add_node(self, connection):
        outNodeId = connection.outNode
        middleNodeId = Genome.nextId
        inNodeId = connection.inNode
        weight = connection.weight

        connection.expressed = False
        self.nodes.append(NodeGene(middleNodeId, Genome.HIDDEN))
        Genome.nextId += 1

        self.add_connection(outNodeId, middleNodeId, 1)
        self.add_connection(middleNodeId, inNodeId, weight)

    def add_connection_mutation(self):
        while True:
            node1, node2 = random.sample(self.nodes, 2)
            if node1.type == node2.type:
                continue
            outNodeId = node1.id if node1.id < node2.id else node2.id
            inNodeId = node2.id if node1.id < node2.id else node1.id
            if not self.check_connection_exists(outNodeId, inNodeId):
                break

        self.add_connection(self, outNodeId, inNodeId, random.random)

    def add_connection(self, outNodeId, inNodeId, weight):
        self.connections.append(ConnectionGene(outNodeId, inNodeId, weight, Genome.nextInnovationNumber, True))
        Genome.nextInnovationNumber += 1

    def check_connection_exists_from_node_ids(self, id1, id2):
        for connection in self.connections:
            if connection.outNode == id1 and connection.inNode == id2:
                return True

        return False

    def __contains__(self, value):
        for connection in self.connections:
            if connection.innovationNumber == value:
                return True

        return False

    def get_connection_gene(self, innovationNumber):
        for connection in self.connections:
            if connection.innovationNumber == innovationNumber:
                return connection

    @staticmethod
    def cross_over(parent1, parent2):
        child = Genome()
        child.nodes = [node.copy() for node in parent1.nodes]

        for connection in parent1.connections:
            if connection.innovationNumber in parent2:
                par2_connection = parent2.get_connection_gene(connection)
                inherited_connection = connection.copy() if random.randint(0,1) == 0 else par2_connection.copy()
                if connection.expressed != par2_connection.expressed:
                    inherited_connection.expressed = False if random.random < Genome.disable_chance else True
                child.connections.append(inherited_connection)
            else:
                child.connections.append(connection.copy())

        return child

    @staticmethod
    def get_compatibility_distance(genome1, genome2, c1, c2, c3, n=1):
        set1 = set()
        set2 = set()
        for connection in genome1.connections:
            set1.add(connection.innovationNumber)
        max1 = max(set1)

        for connection in genome2.connections:
            set2.add(connection.innovationNumber)
        max2 = max(set2)

        E = 0
        excess_point = min(max1, max2)

        intersection_set = set1.intersection(set2)
        union_set = set1.union(set2)
        diff_set = union_set.difference(intersection_set)

        for num in diff_set:
            if num > excess_point:
                E += 1

        D = len(diff_set) - E

        weight_diff_sum = 0.0
        for num in intersection_set:
            weight1 = genome1.get_connection_gene(num).weight
            weight2 = genome2.get_connection_gene(num).weight
            weight_diff_sum += abs(weight1 - weight2)

        W = weight_diff_sum / len(intersection_set)

        E, D, W = Genome.get_compatibility_distance_parameters(genome1, genome2)

        return (c1*E + c2*D)/n + c3*W



class ConnectionGene:
    def __init__(self, outNodeId, inNodeId, weight, innovationNumber, expressed=False):
        self.outNodeId = outNodeId
        self.inNodeId = inNodeId
        self.weight = weight
        self.innovationNumber = innovationNumber
        self.expressed = expressed

    def copy(self):
        return ConnectionGene(self.outNodeId, self.inNodeId, self.weight, self.innovationNumber, self.expressed)


class NodeGene:
    def __init__(self, id, type):
        self.id = id
        self.type = type

    def copy(self):
        return NodeGene(self.id, self.type)
