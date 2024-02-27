import random
import ctypes
import pandas as pd
pd.set_option("display.max_colwidth", 10000)

from psychopy import visual, core, event, data, clock

# Trigger codes
TRIGGER_EXPERIMENT_START = 6
TRIGGER_ENGLISH_ONSET = 10
TRIGGER_DUTCH_ONSET = 11
TRIGGER_TRIAL_END = 13
TRIGGER_TRIVIA_QUESTION = 20
TRIGGER_RESPONSE_YES = 21
TRIGGER_RESPONSE_NO = 22
TRIGGER_BLOCK_START = 50
TRIGGER_BLOCK_END = 51
TRIGGER_EXPERIMENT_END = 66

# Toy stimuli lists. They are enough to have "rogue" E/D trials 
# (first and last), as well as one of each combination:
# D-D, D-E, E-D, E-E. The order is shuffled.

stimuli_df = pd.read_excel('passages.xlsx')
subject_group = random.choice([1,2])

# Assuming stimuli_df is already loaded
# Group by valence
valence_groups = stimuli_df.groupby('VAL')

# Initialize empty DataFrames for each subset
EN_subset = pd.DataFrame()
NL_subset = pd.DataFrame()

# Distribute passages for each valence group to ensure balance
for valence, group in valence_groups:
    # Shuffle the group to randomize distribution
    shuffled_group = group.sample(frac=1).reset_index(drop=True)
    midpoint = len(shuffled_group) // 2  # Find the midpoint to split evenly
    
    # Distribute evenly between L1 and L2
    EN_subset = pd.concat([EN_subset, shuffled_group[:midpoint]])
    NL_subset = pd.concat([NL_subset, shuffled_group[midpoint:]])

# Shuffle the subsets to randomize the order after distribution
EN_subset = EN_subset.sample(frac=1).reset_index(drop=True)
NL_subset = NL_subset.sample(frac=1).reset_index(drop=True)

EN_subset = EN_subset.drop(columns=["NLP", "NLT"], axis = 1)
NL_subset = NL_subset.drop(columns=["ENP", "ENT"], axis = 1)

# english_stimuli = [
#     {"text": "This is English passage 1 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is the capital of France Paris?", "language": "EN"},
#     {"text": "This is English passage 2 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is the Earth the third planet from the Sun?", "language": "EN"},
#     {"text": "This is English passage 3 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is the chemical symbol for water H2O?", "language": "EN"},
#     {"text": "This is English passage 4 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is Mount Everest over 8,000 meters tall?", "language": "EN"},
#     {"text": "This is English passage 5 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Can humans breathe on Mars without assistance?", "language": "EN"},
#     {"text": "This is English passage 6 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is chocolate toxic to dogs?", "language": "EN"},
#     {"text": "This is English passage 7 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is the Atlantic Ocean the largest ocean on Earth?", "language": "EN"},
#     {"text": "This is English passage 8 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is a tomato considered a vegetable?", "language": "EN"},
#     {"text": "This is English passage 9 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Does the sun orbit the Earth?", "language": "EN"},
#     {"text": "This is English passage 10 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is the human body composed of over 60% water?", "language": "EN"},
#      {"text": "This is English passage 11 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#  "trivia": "Is the Nile the longest river in the world?", "language": "EN"},
#     {"text": "This is English passage 12 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Do penguins live in the Arctic?", "language": "EN"},
#     {"text": "This is English passage 13 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Can ostriches fly?", "language": "EN"},
#     {"text": "This is English passage 14 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is bamboo a type of grass?", "language": "EN"},
#     {"text": "This is English passage 15 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is Venus hotter than Mercury?", "language": "EN"},
#     {"text": "This is English passage 16 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Do honeybees sleep?", "language": "EN"},
#     {"text": "This is English passage 17 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is a shark a mammal?", "language": "EN"},
#     {"text": "This is English passage 18 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Can kangaroos walk backwards?", "language": "EN"},
#     {"text": "This is English passage 19 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is the skin the largest organ of the human body?", "language": "EN"},
#     {"text": "This is English passage 20 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Do all planets in our solar system rotate in the same direction?", "language": "EN"},
#     {"text": "This is English passage 21 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Is the Great Wall of China visible from space?", "language": "EN"},
#     {"text": "This is English passage 22 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Does the moon have its own light?", "language": "EN"},
#     {"text": "This is English passage 23 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Are bats blind?", "language": "EN"},
#     {"text": "This is English passage 24 line 1.\nThis is line 2.\nThis is line 3.\nThis is line 4.",
#      "trivia": "Can reindeer see ultraviolet light?", "language": "EN"}]

# dutch_stimuli = [
#     {"text": "Dit is Dutch passage 1 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is Amsterdam de hoofdstad van Nederland?", "language": "NL"},
#     {"text": "Dit is Dutch passage 2 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is waterstof het eerste element op het periodiek systeem?", "language": "NL"},
#     {"text": "Dit is Dutch passage 3 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is de zon een ster?", "language": "NL"},
#     {"text": "Dit is Dutch passage 4 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is de maan een planeet?", "language": "NL"},
#     {"text": "Dit is Dutch passage 5 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is de zwaartekracht op Mars sterker dan op Aarde?", "language": "NL"},
#     {"text": "Dit is Dutch passage 6 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Kunnen pinguïns vliegen?", "language": "NL"},
#     {"text": "Dit is Dutch passage 7 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is de Indische Oceaan de grootste oceaan op Aarde?", "language": "NL"},
#     {"text": "Dit is Dutch passage 8 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Worden er in Nederland meer fietsen dan auto's verkocht?", "language": "NL"},
#     {"text": "Dit is Dutch passage 9 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is Pluto nog steeds een planeet?", "language": "NL"},
#     {"text": "Dit is Dutch passage 10 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is het mogelijk om aan de Noordpool pinguïns in het wild te zien?", "language": "NL"},
#     {"text": "Dit is Dutch passage 11 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is de Amazonerivier de langste rivier ter wereld?", "language": "NL"},
#     {"text": "Dit is Dutch passage 12 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Leven er pinguïns op de Noordpool?", "language": "NL"},
#     {"text": "Dit is Dutch passage 13 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Kunnen struisvogels vliegen?", "language": "NL"},
#     {"text": "Dit is Dutch passage 14 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is bamboe een soort gras?", "language": "NL"},
#     {"text": "Dit is Dutch passage 15 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is Venus heter dan Mercurius?", "language": "NL"},
#     {"text": "Dit is Dutch passage 16 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Slapen honingbijen?", "language": "NL"},
#     {"text": "Dit is Dutch passage 17 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is een haai een zoogdier?", "language": "NL"},
#     {"text": "Dit is Dutch passage 18 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Kunnen kangoeroes achteruit lopen?", "language": "NL"},
#     {"text": "Dit is Dutch passage 19 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is de huid het grootste orgaan van het menselijk lichaam?", "language": "NL"},
#     {"text": "Dit is Dutch passage 20 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Draaien alle planeten in ons zonnestelsel in dezelfde richting?", "language": "NL"},
#     {"text": "Dit is Dutch passage 21 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Is de Chinese Muur zichtbaar vanuit de ruimte?", "language": "NL"},
#     {"text": "Dit is Dutch passage 22 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Heeft de maan zijn eigen licht?", "language": "NL"},
#     {"text": "Dit is Dutch passage 23 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Zijn vleermuizen blind?", "language": "NL"},
#     {"text": "Dit is Dutch passage 24 regel 1.\nDit is regel 2.\nDit is regel 3.\nDit is regel 4.",
#      "trivia": "Kunnen rendieren ultraviolet licht zien?", "language": "NL"}]

# Code also from FYRP that should send the trigger codes to EEG recording.
#def send_trigger(code):
#    trigger = int(code)
#    port.write(trigger.to_bytes(1,'big'))
#    print("Code {} has been sent to the recorder.".format(code))
#import serial #pyserial
#port = serial.Serial('COM4', baudrate = 115200)
#port.flush()
#port.reset_input_buffer()
#port.reset_output_buffer()

def send_trigger(code):
    print("Trigger {} sent.".format(code))


send_trigger(0)

def format_text_into_lines(text, num_lines=4):
    words = text.split()
    total_words = len(words)
    words_per_line = total_words // num_lines
    extra_words = total_words % num_lines
    
    lines = []
    start_index = 0

    for i in range(num_lines):
        end_index = start_index + words_per_line + (1 if i < extra_words else 0)
        line = " ".join(words[start_index:end_index])
        lines.append(line)
        start_index = end_index

    return "\n".join(lines)
    
def present_trivia(win, trivia_text, lang):
    # Short gap after the last line of the stimulus before the trivia is
    # shown. Should I add a window pop-up maybe?
    core.wait(1)
    send_trigger(TRIGGER_TRIVIA_QUESTION)
    if lang == "EN":
        text = trivia_text["ENT"].to_string(index=False)
    else:
        text = trivia_text["NLT"].to_string(index=False)
        

    # Present the trivia question itself, wait for a response.
    # "J" = "yes", "K" = "no". Send triggers acordingly.
    trivia = visual.TextStim(win, text=text, height=30)
    trivia.draw()
    win.flip()

    response = event.waitKeys(keyList=['j','k'])
    if response[0] == 'j':
        send_trigger(TRIGGER_RESPONSE_YES)
    else:
        send_trigger(TRIGGER_RESPONSE_NO)


# Function to present stimulus for 4 lines (3.5 seconds each), replicating the
# original experimental setup.
def present_stimulus(win, stimulus, lang):
    if lang == "EN":
        text, trivia = stimulus["ENP"].to_string(index=False), stimulus["ENT"].to_string(index=False)
    else: 
        text, trivia = stimulus["NLP"].to_string(index=False), stimulus["NLT"].to_string(index=False)
        #text = text.replace('\\n', '\n')
    
    text = format_text_into_lines(text)
    stimulus = visual.TextStim(win, text='', height=30)
    for line in text.split('\n'):
        stimulus.setText(line)
        stimulus.draw()
        win.flip()
        core.wait(3.5)
    win.flip()  # Clear the screen after presenting all lines.

# Function for 14s fixation | Set to 4s for a shorter duration.
def present_fixation(win):
    fixation_text = visual.TextStim(win, text='+', height=40)
    fixation_text.draw()
    win.flip()
    core.wait(4)

# Create a window where the experiment will happen!
win = visual.Window(size=(1024, 768), color='black', units='pix')

# The greeting window of the experiment. Send a trigger that it started.
# Press "y" to proceed.
send_trigger(TRIGGER_EXPERIMENT_START)
instructions = visual.TextStim(win, text="Welcome to the experiment. Please read the following instructions carefully. Press 'Y' when you are ready to begin.", wrapWidth=800, height=20)
instructions.draw()
win.flip()
event.waitKeys(keyList=['y'])

# Function to check for pause, can be triggered either before or after fixation.
def check_for_pause():
    if 'v' in event.getKeys():
        pause_text = visual.TextStim(win, text="Experiment paused. Press 'V' to continue.", wrapWidth=800, height=20)
        pause_text.draw()
        win.flip()
        key = event.waitKeys(keyList=['v'])  # Wait for 'V' to be pressed again.
        if key:
            win.flip()  # Clear the pause message.

# Pseudo-randomise the trials in a block, but also remove the stimuli that
# were picked to eliminate possibilities of repeating same stimuli.
def create_block_trials(english_stimuli, dutch_stimuli):
    combinations = [['E', 'D', 'E', 'D', 'E', 'D', 'D', 'D', 'D', 'E', 'E', 'E', 'D', 'D', 'D', 'E', 'E', 'D', 'D', 'D', 'E', 'E', 'D', 'E', 'D', 'E', 'E', 'E'],
     ['D', 'E', 'D', 'D', 'D', 'D', 'E', 'D', 'D', 'E', 'E', 'E', 'E', 'D', 'E', 'E', 'D', 'E', 'E', 'E', 'D', 'D', 'E', 'D', 'E', 'E', 'D', 'D'],
     ['D', 'E', 'D', 'E', 'D', 'E', 'E', 'D', 'D', 'D', 'D', 'D', 'D', 'E', 'D', 'E', 'D', 'D', 'E', 'E', 'E', 'E', 'D', 'D', 'E', 'E', 'E', 'E'],
     ['E', 'D', 'E', 'D', 'E', 'E', 'D', 'D', 'D', 'D', 'E', 'E', 'E', 'D', 'D', 'D', 'E', 'D', 'D', 'E', 'E', 'E', 'D', 'D', 'E', 'E', 'E', 'D']]

    # Function to select and remove a stimulus from the pool
    def select_and_remove_pattern(pattern_list):
        pattern = random.choice(pattern_list)
        pattern_list.remove(pattern)
        return pattern 

    def select_and_remove_df(stimuli_dataframe):
        stimulus = stimuli_dataframe.sample(n=1)
        stimuli_dataframe = stimuli_dataframe.drop(stimulus.index)
        stimuli_dataframe = stimuli_dataframe.reset_index(drop=True)
        return stimulus 

    trial_patterns = [random.choice(['E', 'D'])]
    trial_patterns += (select_and_remove_pattern(combinations))

     # Add the first trial, whichever language wasn't used for the first trial.
    if trial_patterns[0] == 'E':
        trial_patterns.append("D")
    else:
        trial_patterns.append("E")

    trials = []
    
    print("Trial patterns: ", trial_patterns)
    # Add pseudo-random trials based on combinations from earlier.
    for trial_pattern in trial_patterns:
        if trial_pattern == 'E':
            trials.append(select_and_remove_df(english_stimuli))
        else:
            trials.append(select_and_remove_df(dutch_stimuli))
    
    return trials

# The experimental loop itself.
trivia_interval = 6
number_of_blocks = 4
for block in range(number_of_blocks):  # 4 blocks to mimic the intended experiment setup.
    send_trigger(TRIGGER_BLOCK_START)
    trial_counter = 1  # Reset at the start of each block.
    last_trivia_shown = 0  # Tracks the last trial after which trivia was shown.
    block_trials = create_block_trials(EN_subset, NL_subset)
    core.wait(2)
    
    for stim in block_trials:
        if 'ENP' in stim.columns:
            send_trigger(TRIGGER_ENGLISH_ONSET)
            present_stimulus(win, stim, "EN")
        else:
            send_trigger(TRIGGER_DUTCH_ONSET)
            present_stimulus(win, stim, "NL")
        trial_counter += 1
        
        send_trigger(TRIGGER_TRIAL_END)
        if trial_counter - last_trivia_shown == trivia_interval:
            if 'ENP' in stim.columns:
                present_trivia(win, stim, lang = "EN")
            else:
                present_trivia(win, stim, lang = "NL") # Present trivia related to the current stimulus.
            last_trivia_shown = trial_counter
        
        check_for_pause()
        present_fixation(win)
        check_for_pause()
    send_trigger(TRIGGER_BLOCK_END)

    # Break window at the end of each block, if it's not the last block yet.
    if block < 3:
        break_message = visual.TextStim(win, text="Take a short break. Press 'Y' when you are ready to continue.", wrapWidth=800, height=20)
        break_message.draw()
        win.flip()
        event.waitKeys(keyList=['y'])

# The ending of the experiment, with a window to thank participants.
send_trigger(TRIGGER_EXPERIMENT_END)
thank_you = visual.TextStim(win, text="The experiment is now concluded.\nThank you for your participation.", wrapWidth=800, height=20)
thank_you.draw()
win.flip()
core.wait(5)  # Displays the message for 5 seconds or wait for a key press.

win.close()
core.quit()

# TODO: 
# 1. Replace dicts with data from a .csv/Excel sheet(?). Keep the concept the same, but
# add more relevant fields, such as "correct answer key".
# Additionally, replace with the actual HP stimuli.

# 2. Add behavioral data hooks to output. What do we wanna get (if anything)
# besides the accuracy?
