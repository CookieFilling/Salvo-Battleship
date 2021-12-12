import math
import random as rd

class BattleshipSetup:
    empty_water_symbol = "_"
    occupied_symbol = "T"
    num_shots = 3

    def __init__(self, grid_length=10, size_5_ships=1, size_4_ships=1, size_3_ships=2, size_2_ships=1):
        self.grid_length = grid_length
        self.ship_amounts = [size_5_ships, size_4_ships, size_3_ships,
                             size_2_ships]  # list of ship sizes in deploy_armada
        self.total_ship_tiles = 5 * size_5_ships + 4 * size_4_ships + 3 * size_3_ships + 2 * size_2_ships
        self.grid = []
        # same as the game board, except ships are represented by their lengths
        self.ship_lengths_grid = []
        self.ref_num = 0
        self.ref_row = 0
        self.ref_column = 0
        self.board_reference = [x for x in range(grid_length ** 2)]
        # each inner list represents the points of a ship
        # goes in descending order of ship sizes
        self.ships_as_coordinate_lists = []

    def create_random_board(self):
        # recompleted_turns a description
        self.create_empty_grid()
        self.deploy_armada()
        return self.grid, self.grid_length, self.ship_amounts, self.ships_as_coordinate_lists

    # region create_board helper functions
    def create_empty_grid(self):
        row = []
        for column in range(self.grid_length):
            row.append(BattleshipSetup.empty_water_symbol)
        for row1 in range(self.grid_length):
            self.grid.append(row.copy())
        self.ship_lengths_grid = [x.copy() for x in self.grid]

    def deploy_armada(self):
        # uses the place_ship function, which use find_ship_placement()
        for size in range(len(self.ship_amounts)):
            for amount in range(self.ship_amounts[size]):
                self.place_ship([5, 4, 3, 2][size])

    def place_ship(self, ship_length):
        # updates grid and ship_lengths_grid
        # uses the find_ship_placement function
        direction = self.find_ship_placement(ship_length)

        ship_coordinate_list = []
        for i in range(ship_length):
            row = self.ref_row - i * round(math.sin(direction * math.pi / 2))
            column = self.ref_column + i * round(math.cos(direction * math.pi / 2))

            self.grid[row][column] = BattleshipSetup.occupied_symbol
            self.ship_lengths_grid[row][column] = ship_length

            ref_num = row * self.grid_length + column
            self.board_reference.remove(ref_num)

            ship_coordinate_list.append([row, column])

        self.ships_as_coordinate_lists.append(ship_coordinate_list)

    def find_ship_placement(self, ship_length):
        # size_of_ship = 1 doesn't work

        valid_directions = []
        possible_indexes = [0, 1, 2, 3]

        # finds a start_point, then tests points from start to end of a ship

        self.choose_random_tile()

        for angle in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
            for dist_from_start in range(1, ship_length):

                # start + distance * (0 or 1)
                row_ship_part = self.ref_row + dist_from_start * -round(math.sin(angle))
                column_ship_part = self.ref_column + dist_from_start * round(math.cos(angle))

                # tests if a tile has a ship or is out of range (including -1)
                try:
                    is_out_of_range = row_ship_part < 0 or column_ship_part < 0
                    if self.grid[row_ship_part][column_ship_part] == BattleshipSetup.occupied_symbol or is_out_of_range:
                        valid_directions.append(False)
                        break
                    if dist_from_start == ship_length - 1:
                        valid_directions.append(True)
                except IndexError:
                    valid_directions.append(False)
                    break

        if valid_directions.count(True) == 0:
            return self.find_ship_placement(ship_length)
        else:
            # converts valid directions to indexes
            for i in range(4):
                if not valid_directions[i]:
                    possible_indexes.remove(i)

            direction = rd.choice(possible_indexes)
            return direction

    def choose_random_tile(self):
        # results in modified ref num
        while True:
            self.ref_num = rd.choice(self.board_reference)
            self.convert_reference_to_coordinates(self.ref_num)

            start_point = self.grid[self.ref_row][self.ref_column]

            if BattleshipSetup.empty_water_symbol == start_point:
                break
            else:
                self.board_reference.remove(self.ref_num)

    def convert_reference_to_coordinates(self, input_value):
        # expects an int
        # changes ref_row and ref_column
        self.board_reference.index(input_value)
        self.ref_row = input_value // self.grid_length
        self.ref_column = input_value % self.grid_length


class RandomGuesser(BattleshipSetup):

    def __init__(self, game_board_and_description):
        # the parameter format from the return of create_random_board()
        gb = game_board_and_description
        super().__init__(gb[1], gb[2][0], gb[2][1], gb[2][2], gb[2][3])
        self.game_board = gb[0]
        self.completed_turns = 0

        self.create_empty_grid()

    def finish_game(self):
        while self.total_ship_tiles > 0:
            self.play_a_turn()
            self.completed_turns += 1

        return self.completed_turns

    def play_a_turn(self):
        # updates the guessing board
        hits = 0
        shot_locations = []

        # run if the number of tiles left < num. of shots
        if len(self.board_reference) <= self.num_shots:
            for reference in self.board_reference:
                self.convert_reference_to_coordinates(reference)
                shot_locations.append((self.ref_row, self.ref_column))

                if self.game_board[self.ref_row][self.ref_column] == BattleshipSetup.occupied_symbol:
                    hits += 1

            self.total_ship_tiles = 0
        else:
            for i in range(self.num_shots):
                self.choose_random_tile()
                self.board_reference.remove(self.ref_num)
                shot_locations.append((self.ref_row, self.ref_column))

                if self.game_board[self.ref_row][self.ref_column] == BattleshipSetup.occupied_symbol:
                    hits += 1

            self.total_ship_tiles -= hits

        for coordinate in shot_locations:
            self.grid[coordinate[0]][coordinate[1]] = str(hits)


class PDFGuesser(BattleshipSetup):
    # what tiles to check from heat map: top 5
    top_ith_nums = 5

    def __init__(self, game_board_and_description, ship_lengths_grid, ships_as_coordinate_lists):
        # the 1st parameter format from the return of create_random_board()
        gb = game_board_and_description
        super().__init__(gb[1], gb[2][0], gb[2][1], gb[2][2], gb[2][3])
        self.game_board = gb[0]
        self.completed_turns = 0
        self.ship_listing = [5 for x in range(self.ship_amounts[0])] + [4 for x in range(self.ship_amounts[1])] + \
                            [3 for x in range(self.ship_amounts[2])] + [2 for x in range(self.ship_amounts[3])]

        self.create_empty_grid()
        self.ship_lengths_grid = ship_lengths_grid
        self.ships_as_coordinate_lists = ships_as_coordinate_lists
        self.player_grid = self.grid
        # actual heatmap with number of ship placements on each tile
        self.heatmap_grid = []
        # within identity_heatmap, each point has a list of ship identity nums
        # treat as a row and column grid, not reference num list
        self.identity_heatmap = []
        self.completed_turns = 0

    def play_game(self):
        current_ship_types_hit = set()
        current_total_hit_pts = []

        while self.total_ship_tiles > 0:
            # checks if it's on last turn where there aren't num_shots tiles (3 tiles) left
            final_complete_turn = self.grid_length**2 // BattleshipSetup.num_shots

            if self.completed_turns == final_complete_turn:
                for row in range(self.grid_length):
                    for column in range(self.grid_length):
                        if self.player_grid[row][column] == BattleshipSetup.empty_water_symbol:
                            self.player_grid[row][column] = self.total_ship_tiles
                            self.total_ship_tiles = 0
                            self.completed_turns += 1
                            break
                    if self.total_ship_tiles == 0:
                        break
                if self.total_ship_tiles == 0:
                    break
            
            # target mode
            if len(current_ship_types_hit) > 0 and self.completed_turns >= 1:
                self.create_heatmap(current_total_hit_pts, current_ship_types_hit)
            # hunt mode
            else:
                self.create_heatmap()

            highest_nums = self.find_highest_nums_from_heatmap()
            best_points = self.determine_best_choice(highest_nums)
            hits_and_ships = self.play_a_turn(best_points)
            current_ship_types_hit = current_ship_types_hit | set(hits_and_ships[1])
            for pt in hits_and_ships[2]:
                current_total_hit_pts.append(pt)

            # check if any ships are sunk, updates the present ships and the ship types hit list
            temp_ship_coordinate_lists = [x.copy() for x in self.ships_as_coordinate_lists]

            for ship in self.ships_as_coordinate_lists:
                ship_tiles_sunk = 0
                for pt in ship:
                    if self.player_grid[pt[0]][pt[1]] != BattleshipSetup.empty_water_symbol:
                        ship_tiles_sunk += 1

                if ship_tiles_sunk == len(ship):
                    # then ship length n has been sunk
                    current_ship_types_hit.remove(len(ship))
                    temp_ship_coordinate_lists.remove(ship)

                    # there's two 3-length ships, checks for a hit on 2nd one after the 1st ship is cleared from list
                    for ship_points in temp_ship_coordinate_lists:
                        if len(ship_points) == len(ship):
                            for point in ship_points:
                                if point in current_total_hit_pts:
                                    current_ship_types_hit = current_ship_types_hit | set([len(ship)])


            self.ships_as_coordinate_lists = [x.copy() for x in temp_ship_coordinate_lists]

            self.completed_turns += 1

        return self.completed_turns

    def create_heatmap(self, hit_points=[], ship_types_hit=[]):
        self.identity_heatmap = [[[] for x in range(self.grid_length)] for x in range(self.grid_length)]
        # updates self.heatmap_grid and self.identity_heatmap
        # distinguishes each ship placement by a unique identity num
        identity = 1

        # runs through each ship, then each tile of the game board
        for ship_length in self.ship_listing:

            # horizontal check
            for row in range(self.grid_length):
                for column in range(self.grid_length - ship_length + 1):
                    add_to_identity_heatmap = True
                    # actual checking: if fail, then don't add to heat_map
                    for i in range(ship_length):
                        if self.player_grid[row][
                            column + i] != BattleshipSetup.empty_water_symbol or column + i >= self.grid_length:
                            add_to_identity_heatmap = False

                    if add_to_identity_heatmap == True:
                        for j in range(ship_length):
                            identity += 1
                            self.identity_heatmap[row][column + j].append(identity)

            # vertical check
            for row in range(self.grid_length - ship_length + 1):
                for column in range(self.grid_length):
                    add_to_identity_heatmap = True
                    # actual checking: if fail, then don't add to heat_map
                    for i in range(ship_length):
                        if self.player_grid[row + i][
                            column] != BattleshipSetup.empty_water_symbol or row + i >= self.grid_length:
                            add_to_identity_heatmap = False

                    if add_to_identity_heatmap == True:
                        for j in range(ship_length):
                            identity += 1
                            self.identity_heatmap[row + j][column].append(identity)

        # identity after the loop is the total num of ship locations

        # ensures checked spots are the lowest value on the heat map
        self.heatmap_grid = [[len(self.identity_heatmap[row][column].copy()) for column in range(self.grid_length)] for
                             row in range(self.grid_length)]
        for row in range(self.grid_length):
            for column in range(self.grid_length):
                if self.player_grid[row][column] != BattleshipSetup.empty_water_symbol:
                    self.heatmap_grid[row][column] = -1

        # for target mode: adding extra weight to ship tiles that include the hit points
        if hit_points != []:
            for ship_type in ship_types_hit:
                for pt in hit_points:
                    for i in range(ship_type):
                        row = pt[0] + i
                        if row > -1 and row < self.grid_length:
                            if self.player_grid[row][pt[1]] == BattleshipSetup.empty_water_symbol:
                                self.heatmap_grid[row][pt[1]] += 100
                        row = pt[0] - i
                        if row > -1 and row < self.grid_length:
                            if self.player_grid[row][pt[1]] == BattleshipSetup.empty_water_symbol:
                                self.heatmap_grid[row][pt[1]] += 100
                        column = pt[1] + i
                        if column > -1 and column < self.grid_length:
                            if self.player_grid[pt[0]][column] == BattleshipSetup.empty_water_symbol:
                                self.heatmap_grid[pt[0]][column] += 100
                        column = pt[1] - i
                        if column > -1 and column < self.grid_length:
                            if self.player_grid[pt[0]][column] == BattleshipSetup.empty_water_symbol:
                                self.heatmap_grid[pt[0]][column] += 100

    def find_highest_nums_from_heatmap(self):
        # recompleted_turns the highest points
        highest_points = []

        temp_heatmap = [x.copy() for x in self.heatmap_grid]
        temp_point = []

        for i in range(PDFGuesser.top_ith_nums):
            temp_highest = -1
            for row in range(self.grid_length):
                for column in range(self.grid_length):
                    tile_value = temp_heatmap[row][column]
                    if temp_highest < tile_value:
                        temp_highest = tile_value
                        temp_point = [row, column]
            if temp_highest == -1:
                break
            else:
                highest_points.append(temp_point)

            temp_heatmap[temp_point[0]][temp_point[1]] = -1
        return highest_points

    def determine_best_choice(self, points_to_check):
        # works for num_shots = 3
        # recompleted_turns the points with the highest ship locations checked
        temp_points = []  # [1st point, 2nd, 3rd]
        highest_count = 0
        highest_points = []
        list_of_nonunique_ships = []

        for first in range(len(points_to_check) - 2):
            temp_points.append(points_to_check[first])
            for second in range(first + 1, len(points_to_check) - 1):
                temp_points.append(points_to_check[second])
                for third in range(second + 1, len(points_to_check)):
                    temp_points.append(points_to_check[third])

                    for pt in temp_points:
                        list_of_nonunique_ships.extend(self.identity_heatmap[pt[0]][pt[1]])
                    temp_count = len(set(list_of_nonunique_ships))
                    list_of_nonunique_ships.clear()

                    if highest_count < temp_count:
                        highest_count = temp_count
                        highest_points = [x.copy() for x in temp_points]

                    del temp_points[2]
                del temp_points[1]
            del temp_points[0]

        if highest_points == []:
            for i in range(BattleshipSetup.num_shots):
                highest_points.append(points_to_check[i])

        return highest_points

    def play_a_turn(self, best_points):
        hits = 0
        ship_types_hit = []

        for pt in best_points:
            if self.game_board[pt[0]][pt[1]] == BattleshipSetup.occupied_symbol:
                hits += 1
                ship_types_hit.append(self.ship_lengths_grid[pt[0]][pt[1]])
        for pt in best_points:
            self.player_grid[pt[0]][pt[1]] = str(hits)

        self.total_ship_tiles -= hits
        ship_types_hit = set(ship_types_hit)
        return hits, ship_types_hit, best_points
