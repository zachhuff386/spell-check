import spell_check

spell_check = spell_check.SpellCheck()
spell_check.read_file()

while True:
    word = raw_input('> ')
    run_time, matches = spell_check.get_matches_timed(word)
    print 'run_time: %0.8f' % run_time
    print 'matches:', matches
