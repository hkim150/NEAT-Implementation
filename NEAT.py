import random
from math import exp


class Genome:
    c1, c2, c3 = 1.0, 1.0, 0.4
    d_t = 2.5
    disable_chance = 0.75
    weight_mutation_chance = 0.8
    add_node_mutation_chance = 0.08
    add_connection_mutation_chance = 0.15
    perturbation_chance = 0.9

    def __init__(self, num_input_nodes=0, num_output_nodes=0):
        self.nodes = []
        self.connections = []
        for _ in range(num_input_nodes):
            self.nodes.append(NodeGene(NodeGene.nextId, NodeGene.INPUT))
            NodeGene.nextId += 1

        for _ in range(num_output_nodes):
            self.nodes.append(NodeGene(NodeGene.nextId, NodeGene.OUTPUT))
            NodeGene.nextId += 1

    def mutate(self):
        if random.random() < Genome.weight_mutation_chance:
            self.weight_mutation()
        if random.random() < Genome.add_node_mutation_chance:
            self.add_node_mutation()
        if random.random() < Genome.add_connection_mutation_chance:
            self.add_connection_mutation()

    def weight_mutation(self):
        for connection in self.connections:
            random_val = random.random()*4 - 2
            if random.random() < Genome.perturbation_chance:
                connection.weight *= random_val
            else:
                connection.weight = random_val

    def add_node_mutation(self):
        if len(self.connections) < 1:
            return
        
        connection = random.choice(self.connections)
        self.add_node(connection)

    def add_node(self, connection):
        outNodeId = connection.outNodeId
        middleNodeId = NodeGene.nextId
        inNodeId = connection.inNodeId
        weight = connection.weight

        connection.expressed = False
        self.nodes.append(NodeGene(middleNodeId, NodeGene.HIDDEN))
        NodeGene.nextId += 1

        self.add_connection(outNodeId, middleNodeId, 1)
        self.add_connection(middleNodeId, inNodeId, weight)

    def add_connection_mutation(self):
        while True:
            node1, node2 = random.sample(self.nodes, 2)
            if node1.type == node2.type:
                continue
            outNodeId = node1.id if node1.id < node2.id else node2.id
            inNodeId = node2.id if node1.id < node2.id else node1.id
            if not self.check_connection_exists_from_node_ids(outNodeId, inNodeId):
                break

        self.add_connection(outNodeId, inNodeId, random.random()*2 - 1)

    def add_connection(self, outNodeId, inNodeId, weight):
        self.connections.append(ConnectionGene(outNodeId, inNodeId, weight, ConnectionGene.nextInnovationNumber, True))
        ConnectionGene.nextInnovationNumber += 1

    def check_connection_exists_from_node_ids(self, id1, id2):
        for connection in self.connections:
            if connection.outNodeId == id1 and connection.inNodeId == id2:
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

    def copy(self):
        newGenome = Genome()
        for node in self.nodes:
            newGenome.nodes.append(node.copy())

        for connection in self.connections:
            newGenome.connections.append(connection.copy())

        return newGenome

    @staticmethod
    def cross_over(parent1, parent2):
        child = Genome()
        child.nodes = [node.copy() for node in parent1.nodes]

        for connection in parent1.connections:
            if connection.innovationNumber in parent2:
                par2_connection = parent2.get_connection_gene(connection.innovationNumber)
                inherited_connection = connection.copy() if random.randint(0,1) == 0 else par2_connection.copy()
                if connection.expressed != par2_connection.expressed:
                    inherited_connection.expressed = False if random.random() < Genome.disable_chance else True
                child.connections.append(inherited_connection)
            else:
                child.connections.append(connection.copy())

        return child

    @staticmethod
    def get_compatibility_distance(genome1, genome2, n=1):
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

        W = weight_diff_sum / max(len(intersection_set), 1)

        return (Genome.c1*E + Genome.c2*D)/n + Genome.c3*W


class ConnectionGene:
    nextInnovationNumber = 0

    def __init__(self, outNodeId, inNodeId, weight, innovationNumber, expressed=False):
        self.outNodeId = outNodeId
        self.inNodeId = inNodeId
        self.weight = weight
        self.innovationNumber = innovationNumber
        self.expressed = expressed

    def copy(self):
        return ConnectionGene(self.outNodeId, self.inNodeId, self.weight, self.innovationNumber, self.expressed)


class NodeGene:
    nextId = 0
    INPUT, HIDDEN, OUTPUT = 0, 1, 2

    def __init__(self, id, type):
        self.id = id
        self.type = type

    def copy(self):
        return NodeGene(self.id, self.type)


class Generation:
    nextGenerationNumber = 0
    max_population = 50
    clone_chance = 0.25
    mate_chance = 0.75

    def __init__(self):
        self.generation_number = Generation.nextGenerationNumber
        Generation.nextGenerationNumber += 1
        self.species = []
        self.population = 0

    def add_organism(self, organism):
        self.population += 1
        if self.population > 1:
            for s in self.species:
                if Genome.get_compatibility_distance(organism.genome, s.representative.genome) < Genome.d_t:
                    s.add_organism(organism)
                    return
        self.species.append(Species(organism))

    def get_next_generation(self):
        species_and_avg_fitness = []
        sum_avg_fitness = 0.0
        for s in self.species:
            avg_fitness = s.get_average_fitness()
            sum_avg_fitness += avg_fitness
            species_and_avg_fitness.append([s, avg_fitness])

        nextGeneration = Generation()
        for s, avg in species_and_avg_fitness:
            max_offspring_num = round((avg/max(sum_avg_fitness,1))*Generation.max_population)
            offspring = s.get_offsprings(max_offspring_num)
            nextGeneration.species.append(offspring)
            nextGeneration.population += offspring.population

        return nextGeneration


class Species:
    def __init__(self, organism=None):
        self.organisms = [organism]
        self.population = len(self.organisms)
        self.representative = organism

    def add_organism(self, organism):
        self.organisms.append(organism)
        self.population += 1

    def get_average_fitness(self):
        fitness_sum = 0.0
        for organism in self.organisms:
            fitness_sum += organism.fitness

        return fitness_sum / self.population

    def get_offsprings(self, max_offspring_num):
        rank = sorted(self.organisms, key=lambda x: x.fitness, reverse=True)
        champion = rank[0]
        offsprings = Species(champion.copy())
        survivors = rank[:len(rank)//2]
        num_offspring = min(self.population, max_offspring_num)

        for survivor in random.sample(survivors, round(num_offspring*Generation.clone_chance)):
            offsprings.add_organism(survivor.copy())

        for _ in range(round(num_offspring*Generation.mate_chance)-1):
            parent1, parent2 = random.sample(survivors, 2)
            if parent1.fitness > parent2.fitness:
                offsprings.add_organism(Organism(Genome.cross_over(parent1.genome, parent2.genome)))
            else:
                offsprings.add_organism(Organism(Genome.cross_over(parent2.genome, parent1.genome)))

        for organism in offsprings.organisms:
            organism.genome.mutate()

        return offsprings


class Organism:
    def __init__(self, genome=None):
        self.genome = genome
        self.fitness = 1

    def copy(self):
        return Organism(self.genome.copy())

    def choose_action(self, state):
        input_ids = {}
        output_value = {}
        idx = 0
        output_node_ids = []
        for node in self.genome.nodes:
            if node.type == NodeGene.INPUT:
                output_value[node.id] = state[idx]
                idx += 1
            elif node.type == NodeGene.OUTPUT:
                output_node_ids.append(node.id)

        for connection in self.genome.connections:
            if connection.expressed:
                if connection.inNodeId in input_ids:
                    input_ids[connection.inNodeId].append(connection)
                else:
                    input_ids[connection.inNodeId] = [connection]

        while len(input_ids) > 0:
            to_del = []
            for node_id, connections in input_ids.items():
                output = 0.0
                know_all_input_values = True
                for connection in connections:
                    if connection.outNodeId in output_value:
                        output += output_value[connection.outNodeId] * connection.weight
                    else:
                        know_all_input_values = False
                        break

                if know_all_input_values:
                    output_value[node_id] = 1 / (1 + exp(output))
                    to_del.append(node_id)

            for node_id in to_del:
                del input_ids[node_id]

        best_action = -1
        max_val = None

        for id in output_node_ids:
            if id in output_value:
                if best_action == -1:
                    max_val = output_value[id]
                    best_action = id
                else:
                    if output_value[id] > max_val:
                        max_val = output_value[id]
                        best_action = id

        return best_action
