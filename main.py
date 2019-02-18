from game import *


def main():
    user_mode = False

    window = pg.display.set_mode((Game.window_width, Game.window_height))
    game = Game()

    initial_organism_count = 10
    max_generations = 200

    gen = Generation()
    initial_genome = Genome(Game.num_inputs, Game.num_actions)
    initial_genome.add_connection_mutation()

    for _ in range(initial_organism_count):
        new_genome = initial_genome.copy()
        new_genome.mutate()
        gen.add_organism(Organism(new_genome))

    for curr_g in range(max_generations):
        pop = gen.population
        num_sp = len(gen.species)
        organisms = gen.get_all_organisms()
        info = [curr_g + 1, pop, num_sp]
        #info.extend(organism.genome.get_genome_info())
        game.game_start(window, organisms, info, user_mode)

        gen.next_generation()


if __name__ == '__main__': main()
