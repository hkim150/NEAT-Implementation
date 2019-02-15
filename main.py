from game import *


def main():
    initial_organism_count = 10
    max_generations = 50

    game = Game()
    gen = Generation()
    initial_genome = Genome(Game.NUM_INPUT, Game.NUM_ACTIONS)
    initial_genome.add_connection_mutation()

    for _ in range(initial_organism_count):
        new_genome = initial_genome.copy()
        new_genome.mutate()
        gen.add_organism(Organism(new_genome))

    for _ in range(max_generations):
        show = False
        if gen.generation_number > max_generations * 0.8:
            game.win = pg.display.set_mode((Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT))
            show = True
        s_num = 0
        for s in gen.species:
            s_num += 1
            o_num = 0
            for organism in s.organisms:
                o_num += 1
                print("generation: " + str(gen.generation_number) + ", population: " + str(
                    gen.population) + ", num species: " + str(len(gen.species)) + ", species: " + str(
                    s_num) + ", organism: " + str(o_num))
                #print("num_nodes: " + str(len(organism.genome.nodes)) + " num_connections: " + str(len(organism.genome.connections)))
                game.game_start(organism, show)

        gen.next_generation()


if __name__ == '__main__': main()
