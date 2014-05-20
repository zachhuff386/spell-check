import spell_check
import requests

spell_check = spell_check.SpellCheck()
spell_check.read_file()

def google_check(word):
    word = word.lower()
    response = requests.get('http://www.google.com/search', params={
        'q': 'definition ' + word,
    })
    response = response.text.encode('utf-8')

    start_index = response.find('<span class="spell">Showing results for')
    if start_index == -1:
        return word
    start_index = response.find('definition', start_index)
    if start_index == -1:
        return word
    start_index = response.find('<b><i>', start_index)
    if start_index == -1:
        return word
    start_index += 6
    end_index = response.find('</i></b>', start_index)
    if end_index == -1:
        return word
    return response[start_index:end_index]

while True:
    word = raw_input('> ')
    run_time, matches = spell_check.get_matches_timed(word)
    print 'run_time: %0.8f' % run_time
    print 'matches:', matches
    print 'google_match:', google_check(word)
