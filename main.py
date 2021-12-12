import Battleship as bs

# [total, 1 turn, 2 completed_turns, 3 completed_turns...]
random_win_completed_turns = [0 for x in range(35)]
PDF_win_completed_turns = [0 for x in range(35)]
iterations = 1
random_win_completed_turns[0] = iterations
PDF_win_completed_turns[0] = iterations

for i in range(iterations):
    print(i)
    setup = bs.BattleshipSetup()
    board = setup.create_random_board()

    random_play = bs.RandomGuesser(board)
    random_play.finish_game()
    print("random: " + str(random_play.completed_turns))
    random_win_completed_turns[random_play.completed_turns] += 1

    heatmap_board = bs.PDFGuesser(board, setup.ship_lengths_grid, setup.ships_as_coordinate_lists)
    heatmap_board.play_game()
    print("PDF: " + str(heatmap_board.completed_turns))
    PDF_win_completed_turns[heatmap_board.completed_turns] += 1

print("random: " + str(random_win_completed_turns))
print("PDF: " + str(PDF_win_completed_turns))



