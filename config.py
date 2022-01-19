wordpath = "wordlist.csv"
proportion_to_rank_up = 0.8
expected_headers = ['word','answer','rank']

# must be in ascending order
mastery_levels = [{'level': 'beginner', 'lower': 0, 'upper': 2, 'seconds': 120},
                  {'level': 'intermediate', 'lower': 3, 'upper': 5, 'seconds': 600},
                  {'level': 'advanced', 'lower': 6, 'upper': 8, 'seconds': 3600},
                  {'level': 'master', 'lower': 9, 'upper': 11, 'seconds': 86400}]

# must be in alphanumeric order that they're expected
all_ranks = ['1','2','3','4']
