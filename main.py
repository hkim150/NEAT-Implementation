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

    show = False
    for curr_g in range(max_generations):
        pop = gen.population
        num_sp = len(gen.species)
        if gen.generation_number > max_generations * 0.0:
            game.win = pg.display.set_mode((Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT))
            show = True
        for curr_s, s in enumerate(gen.species):
            for curr_o, organism in enumerate(s.organisms):
                info = [curr_g + 1, pop, num_sp, curr_s + 1, curr_o + 1]
                info.extend(organism.genome.get_genome_info())
                game.game_start(organism, show, info)

        gen.next_generation()


if __name__ == '__main__': main()
