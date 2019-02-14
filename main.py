from game import *


def main():
    initial_organism_count = 10
    max_generations = 100

    game = Game()
    gen = Generation()
    initial_genome = Genome(Game.NUM_INPUT, Game.NUM_ACTIONS)
    initial_genome.add_connection_mutation()

    for _ in range(initial_organism_count):
        new_genome = initial_genome.copy()
        new_genome.mutate()
        gen.add_organism(Organism(new_genome))

    for _ in range(max_generations):
        print("generation: " + str(Generation.nextGenerationNumber) + ", population: " + str(gen.population))
        print("num species: " + str(len(gen.species)))
        show = False
        if Generation.nextGenerationNumber > max_generations * 0.0:
            if not show:
                game.win = pg.display.set_mode((Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT))
                show = True
        for s in gen.species:
            for organism in s.organisms:
                print("num_nodes: " + str(len(organism.genome.nodes)) + " num_connections: " + str(len(organism.genome.connections)))
                game.game_start(organism, show)

        gen = gen.get_next_generation()


if __name__ == '__main__': main()
