import history



hs = history.History('saves/History')
hs.setGame(hs.getGames()[-1][0])

hs.plot_average_error()
hs.plot_total_reward()