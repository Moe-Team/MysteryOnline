import pstats


p = pstats.Stats('MysteryOnline.profile')
p.sort_stats('cumulative').print_stats()
