import os
import random
import logging
import pandas as pd
from copy import deepcopy
from models import Result, PropertyType
from . import Node, Cross, Leaf, Member, Fitness


class GeneticAlgorithm:
    """
    Initialise the random population
    Loop until generations complete:
        Calculate fitness of all member
        Log tree and trades of M fittest members
        Build next generation based on crossover, mutation and random new members

    Crossover using roulette wheel selection

    Roulette wheel selection:
        Calculate fitness
        Sort by fitness DESC
        Normalise fitness values
        Calculate cumulative fitness
    """
    identifier = None # use for logging and communication of results
    _population:list = None
    _generation:int = 0
    _best_fitness:float = 0
    _population_size:int = 0

    _max_depth: int = 6
    _max_size: int = 100

    # For each node type:
    # Type
    # Min depth
    # Selection probability
    # Edges
    # Number of input fields
    available_node_types = ['Leaf', 'GreaterThan', 'LessThan', 'Cross']
    input_compatibilities = None
    available_inputs = None
    _remaining_node_types = None
    _crossover_prob = 0.8

    _last_best_generation = 0
    _generations_without_fitness_increase = 50

    _training_dataset_path = ''
    _training_dataset = None
    _testing_dataset = None
    _fitness = None

    _logger = None
    _on_generation_finish = None

    def __init__(self,
                 identifier:int,
                 fitness:Fitness,
                 training_dataset:pd.DataFrame,
                 testing_dataset:pd.DataFrame,
                 input_compatibilities:dict,
                 pop_size:int = 200,
                 logger=None,
                 on_generation_finish=None):
        """
        :param input_compatibilities: A dictionary of lists with each key being an input field and each element of the
        corresponding list giving an compatible field name for a node

        For example:
        df = pd.read_csv('strategytrees/input_compatibility.csv', sep=';', index_col=None)
        compatibilities = {k : [c for c in df.columns if df[df['field']==k][c].values == 1] for k in df['field'].values}

        Possible entries:
        'close': ['bollinger_hband', 'bollinger_lband', 'bollinger_mavg', 'ema', 'macd', 'sma_8', 'sma_14', 'wma']

        Note, fields in the compatible fields lists that are prefixed with the following strings will be interpreted as follows:
        {int} the characters proceding this string will be cast to an integer. E.g. {int}90 = 90
        """
        self.identifier = identifier
        self.input_compatibilities = input_compatibilities
        self.available_inputs = list(self.input_compatibilities.keys())
        self._population_size = pop_size
        self._fitness = fitness
        self._training_dataset = training_dataset
        self._testing_dataset = testing_dataset
        self._on_generation_finish = on_generation_finish

        self._logger = logger

    def _log(self, message, level):
        if self._logger is None:
            return 

    def next_generation(self):
        """

        """
        new_pop = []
        while len(new_pop) < self._population_size:
            if random.random() < 0.15:
                m = Member(self.create_tree())
                new_pop.append(m)
                continue

            if random.random() < self._crossover_prob:
                p1 = self._random_member()
                p2 = self._random_member()
                c1, c2 = self.crossover(p1, p2)

                new_pop.append(c1)
                new_pop.append(c2)
            else:
                new_pop.append(self._random_member())

        # Mutation
        for i, p in enumerate(new_pop):
            if random.random() < 0.04:
                new_pop[i] = self.mutate(p.tree)

        # Sanitise all population members by cleaning
        # duplicate or redundant nodes
        for i, m in enumerate(new_pop):

            if type(m) == Leaf:
                m = self._random_member()

            m.tree = m.tree.sanitise()
            new_pop[i] = m

        self._population = new_pop

    def run(self, max_generations:int=200):
        """

        :param max_generations:
        :return:
        """
        self._reset_population()
        for g in range(max_generations):
            # Get fitness values for all members
            self.fitness()

            training_results = self.get_member_fitness(self._population[0], self._training_dataset)

            fns = str(f"{int(training_results.fitness):,}").replace(',', ' ')
            l = f"Generation {(g + 1)} Fitness {fns} Success {training_results.success:.2f} " \
                f"Trades {training_results.trades} pips {training_results.pips:.2f} size {training_results.tree.size} "

            result = Result()
            result.job_id = self.identifier
            result.generation = (g + 1)
            result.best_tree = f"tree = {training_results.tree.compile()}"
            result.add_property(PropertyType.TrainingFitness, training_results.fitness)
            result.add_property(PropertyType.TrainingSuccess, training_results.success)
            result.add_property(PropertyType.TrainingTrades, training_results.trades)
            result.add_property(PropertyType.TrainingPips, training_results.pips)
            result.add_property(PropertyType.Size, training_results.tree.size)
            result.add_property(PropertyType.BestExitType, training_results.exit_type.value)
            result.add_property(PropertyType.BestTP, training_results.tp)
            result.add_property(PropertyType.BestSL, training_results.sl)

            # Get fitness of the best member against the test dataset
            best = self.get_member_fitness(self._population[0], self._testing_dataset)

            result.add_property(PropertyType.TestingFitness, best.fitness)
            result.add_property(PropertyType.TestingSuccess, best.success)
            result.add_property(PropertyType.TestingTrades, best.trades)
            result.add_property(PropertyType.TestingPips, best.pips)
            
            fns_t = str(f"{int(best.fitness):,}").replace(',', ' ')
            l += f"test_fitness {fns_t} test_success {best.success:.2f} test_trades {best.trades} test_pips {best.pips:.2f}"
            self._log(logging.INFO, l)

            # save best and calback
            if not self._on_generation_finish is None:
                self._on_generation_finish(result.to_dict())

            if training_results.fitness > self._best_fitness:
                self._best_fitness = training_results.fitness
                self._last_best_generation = g
            else:
                if g - self._last_best_generation > self._generations_without_fitness_increase:
                    return

            self.next_generation()
        
    def fitness(self):
        """

        """
        # for i, m in enumerate(self._population):
        #     self._population[i].fitness = self._fitness.get_fitness(m.tree, self._dataset)
        #     self._population[i].success = self._fitness._success
        #     self._population[i].trades = self._fitness._total_trades
        #     self._population[i].pips = self._fitness._total_pips
        for i, m in enumerate(self._population):
            self._population[i] = self.get_member_fitness(m, self._training_dataset)
        k = sum([v.fitness for v in self._population])
        if k == 0:
            k = 0.000001
        self._population.sort(key=lambda x: x.fitness, reverse=True)
        t = 0
        for i, m in enumerate(self._population):
            t += self._population[i].fitness / k
            self._population[i].cumulated_fitness = t

    def get_member_fitness(self, m:Member, dataset:pd.DataFrame) -> Member:
        """

        :param m:
        :param dataset:
        :return:
        """
        s = self._copy_member(m)
        s.fitness = self._fitness.get_fitness(s, dataset)
        s.success = self._fitness._success
        s.trades = self._fitness._total_trades
        s.pips = self._fitness._total_pips
        return s

    def validate_member(self, member: Node) -> bool:
        """
            - Max depth
            - Max size
            - Has buy
            - Has sell
            - Contradictions
        :param memer:
        :return:
        """
        if member.depth > self._max_depth:
            return False
        if member.size > self._max_size:
            return False
        s = member.__str__()
        if s.find('BUY') == -1:
            return False
        if s.find('SELL') == -1:
            return False
        return True

    def mutate(self, tree:Node) -> Member:
        """
        Updates 161023:
        Mutate should, based on a random value, either:
            1. Replace a node or branch with a new random node or branch of each size
            2. Change the input feature to one of the node functions (GT, LT, etc.)
            3. Change the function of a specific node
        :param tree:
        :return:
        """
        p = random.random()

        # 1. Replace a node or branch with a new random node or branch of each size
        if p < 0.35:
            if tree.size <= 2:
                self._log(logging.ERROR, f"Cannot mutate tree of size {tree.size}")
                return tree
            try:
                mutation_point = random.randint(1, tree.size - 1)
                _, n = tree.find(mutation_point, 1)
                r = self.create_tree_of_depth(n.depth)
                tree.find(mutation_point, 1, r)
            except:
                pass
        # 2. Change the input feature to one of the node functions (GT, LT, etc.)
        elif p < 0.7:
            self._reset_node_types()
            mutation_point = random.randint(0, tree.size - 1)
            try:
                _, n = tree.find(mutation_point, 0)
                if type(n) is Leaf:
                    n = self._get_random_leaf()
                else:
                    if type(n) == Cross:
                        n.field_b = self._get_field('close_ask')
                    else:
                        n.field_b = self._get_field(n.field_a)
                    if n.field_b.find('{int}') >= 0:
                        n.field_b = int(n.field_b[5:])

                _ = tree.find(mutation_point, 0, n)
            except:
                pass
        # 3. Change the function of a specific node
        else:
            pass

        # Mutate the exit functions
        m = Member(tree)

        return m

    def random_crossover(self, member_a: Member, member_b: Member) -> (Member, Member):
        """

        :param member_a:
        :param member_b:
        :return:
        """
        # Do not perform crossover on the root node.
        if member_a.tree.size > 1:
            point_a, part_a = member_a.tree.find(random.randint(1, member_a.tree.size-1), 0)
        else:
            point_a = 1
            part_a = member_a.tree

        try:
            point_b, part_b = self._get_random_child_node_by_depth(member_b.tree, part_a.depth)
        except TypeError as e:
            self._log(logging.ERROR, f"ERROR: {e}")
            #raise e
            return member_a, member_b

        offspring_a = self._copy_member(deepcopy(member_a))
        offspring_b = self._copy_member(deepcopy(member_b))

        offspring_a.tree.find(point_a, 0, deepcopy(part_b))
        offspring_b.tree.find(point_b, 0, deepcopy(part_b))
        return offspring_a, offspring_b

    def crossover(self, member_a: Member, member_b: Member) -> (Member, Member):
        """

        :param member_a:
        :param member_b:
        :return:
        """
        offspring_a, offspring_b = self.random_crossover(member_a, member_b)
        return offspring_a, offspring_b

    def create_tree_of_depth(self, depth: int) -> object:
        """

        :param depth:
        :return:
        """
        return self.create_tree(self._max_depth - depth)

    def create_tree(self, current_depth:int=0)->Node:
        """
        Tree creation algo:
        Create_tree(current_depth)
          Reinitialise the list of available node types
          new_tree = Randomly select a node type, and remove it from the list of available types
          While it is not possible to add the new node to the tree without exceeding max depth
              new_tree = Select a different node type, and remove it from the list of available types
          Get number of edges for new node and empty inputs list
          For each edge from the node
              new_node = Create_tree(current_depth+1)
              add new_node to inputs list
          instantiate new_tree with inputs list
          return new_tree
        :param current_depth:
        """
        self._reset_node_types()
        if current_depth == 0:
            del (self._remaining_node_types[0]) # Remove the node type Leaf from the initial round

        inpts = []
        while (nd := self._get_random_node_type()).min_depth + current_depth > self._max_depth:
            continue

        nxt_dept = current_depth + 1
        for e in range(nd.edges):
            inpts.append(self.create_tree(nxt_dept))

        if nd is Cross:
            r = nd('open', 'close_ask', self._get_field('close_ask'), *inpts)
        elif nd is Leaf:
            r = self._get_random_leaf()
        else:
            field_a = self._get_field()
            field_b = self._get_field(field_a)
            r = nd(field_a, field_b, *inpts)

        return r

    def _copy_member(self, member:Member)->Member:
        m = Member(member.tree)
        m.exit_type = member.exit_type
        m.tp = member.tp
        m.sl = member.sl
        m.leverage = member.leverage
        return m

    def _reset_population(self):
        """

        """
        self._population = []
        for i in range(self._population_size):
            m = Member(self.create_tree())
            self._population.append(m)

    def _random_member(self)->Member:
        """

        :return:
        """
        # roulette selection
        r = random.random()
        if r > self._population[len(self._population)-1].cumulated_fitness:
            return Member(self.create_tree())
        m = next(v for v in self._population if v.cumulated_fitness > r)
        return m

    def _reset_node_types(self):
        """

        """
        self._remaining_node_types = self.available_node_types.copy()

    def _get_field(self, compatible_with:str=None):
        """

        :param compatible_with:
        :return:
        """
        t_arr = self.available_inputs
        if not compatible_with is None:
            t_arr = self.input_compatibilities[compatible_with]
        r = random.randint(0, len(t_arr) - 1)
        return t_arr[r]

    def _get_random_node_type(self)->Node:
        """

        :return:
        """
        r = random.randint(0, len(self._remaining_node_types) - 1)
        nd = self._remaining_node_types[r]
        del (self._remaining_node_types[r])
        return globals()[nd]

    def _get_random_leaf(self) -> Leaf:
        """

        :return:
        """
        vs = ['BUY', 'HOLD', 'SELL']
        r = random.randint(0, 2)
        return Leaf(vs[r])

    def _get_random_child_node_by_depth(self, tree:Node, max_depth:int) -> (int, Node):
        """

        :param tree:
        :param max_depth:
        :return:
        """
        if tree.depth == 1:
            return tree
        applicable_nodes = self._get_child_nodes_by_depth(tree, max_depth)
        i = random.randint(0, len(applicable_nodes) - 1)
        return tree.find(i, 0)

    def _get_child_nodes_by_depth(self, tree:Node, max_depth:int)->list:
        """

        :param tree:
        :param max_depth:
        :return:
        """
        res = []
        for i in range(1, tree.size):
            b, n = tree.find(i, 0)
            if n.depth <= max_depth:
                res.append(b)
        return res

    @property
    def max_depth(self):
        """

        :return:
        """
        return self._max_depth

    @max_depth.setter
    def max_depth(self, mx_depth:int):
        """

        :param mx_depth:
        """
        self._max_depth = mx_depth

    @property
    def max_size(self):
        """

        :return:
        """
        return self._max_size

    @max_size.setter
    def max_size(self, mx_size:int):
        """

        :param mx_size:
        """
        self._max_size = mx_size