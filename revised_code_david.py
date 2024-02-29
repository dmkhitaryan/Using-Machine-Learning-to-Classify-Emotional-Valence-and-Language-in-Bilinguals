import os
import random
import ctypes
import pandas as pd
pd.set_option("display.max_colwidth", 10000)

from psychopy import visual, core, event, data, clock, gui

# Trigger codes.
TRIGGER_EXPERIMENT_START = 6
TRIGGER_ENGLISH_ONSET = 10
TRIGGER_DUTCH_ONSET = 11
TRIGGER_TRIAL_EN_END = 13
TRIGGER_TRIAL_NL_END = 14
TRIGGER_TRIVIA_QUESTION = 20
TRIGGER_RESPONSE_YES = 21
TRIGGER_RESPONSE_NO = 22
TRIGGER_BLOCK_START = 50
TRIGGER_BLOCK_END = 51
TRIGGER_EXPERIMENT_END = 66

stimuli_df = pd.read_excel('passages.xlsx')
subject_group = random.choice([1,2])
valence_groups = stimuli_df.groupby('VAL') 

# Initialize empty DataFrames for each subset.
EN_subset = pd.DataFrame()
NL_subset = pd.DataFrame()

# Distribute passages for each valence group to ensure balance.
for valence, group in valence_groups:
    # Shuffle the group to randomize distribution, then split in half.
    shuffled_group = group.sample(frac=1).reset_index(drop=True)
    midpoint = len(shuffled_group) // 2
    
    # One half will be used as ENG stimuli, the other: Dutch.
    EN_subset = pd.concat([EN_subset, shuffled_group[:midpoint]])
    NL_subset = pd.concat([NL_subset, shuffled_group[midpoint:]])

# One more reshuffle for good measure, then remove 2nd language from subsets.
EN_subset = EN_subset.sample(frac=1).reset_index(drop=True)
NL_subset = NL_subset.sample(frac=1).reset_index(drop=True)
EN_subset = EN_subset.drop(columns=["NLP", "NLT"], axis = 1)
NL_subset = NL_subset.drop(columns=["ENP", "ENT"], axis = 1)

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

# Algorithm that auto-breaks down a passage into four lines. The lines are
# roughly equal, works for both languages.
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

# The function that presents the trivia question to a participant.
def present_trivia(win, trivia_text, experiment_file, lang):
    lang_bool = "ENP" if lang == "EN" else "NLP"
    trivia_bool = "ENT" if lang == "EN" else "NLT"
    experiment_file.write("{}".format(trivia_text[lang_bool].to_string(index=False)) + "    ")
    experiment_file.write("{}".format(trivia_text[trivia_bool].to_string(index=False)) + "    ")
    experiment_file.write("{}".format(trivia_text["ANS"].to_string(index=False)) + "    ")
    
    trivia_window = visual.TextStim(win, text='', height=30)
    trivia_window.setText("Trivia question!")
    trivia_window.draw()
    win.flip()
    
    trivia_timer = core.Clock()
    trivia_timer.reset()
    while trivia_timer.getTime() < 1.5:
        pass
    
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
    experiment_file.write("{}".format(response[0].upper()) + "\n")
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
    
    line_timer = core.Clock()
    text = format_text_into_lines(text)
    stimulus = visual.TextStim(win, text='', height=30)
    for line in text.split('\n'):
        stimulus.setText(line)
        stimulus.draw()
        win.flip()
        line_timer.reset()
        while line_timer.getTime() < 3.5:
            pass
        
    if lang == "EN":
        send_trigger(TRIGGER_TRIAL_EN_END)
    else:
        send_trigger(TRIGGER_TRIAL_NL_END)    
    win.flip()  # Clear the screen after presenting all lines.
    

# Function for 14s fixation | Set to 4s for a shorter duration.
def present_fixation(win):
    fixation_text = visual.TextStim(win, text='+', height=40)
    fixation_text.draw()
    win.flip()
    fixation_timer = core.Clock()
    fixation_timer.reset()
    while fixation_timer.getTime() < 14:
        pass

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

    # A function to select a combination and remove it from the list.
    def select_and_remove_pattern(pattern_list):
        pattern = random.choice(pattern_list)
        pattern_list.remove(pattern)
        return pattern 
    
    # A function to select a stimulus and remove it from the data frame.
    def select_and_remove_df(stimuli_dataframe):
        stimulus = stimuli_dataframe.sample(n=1)
        stimuli_dataframe = stimuli_dataframe.drop(stimulus.index)
        stimuli_dataframe = stimuli_dataframe.reset_index(drop=True)
        return stimulus 

    # Add the first, middle, and the last trials for a total block sequence.
    trial_patterns = [random.choice(['E', 'D'])]
    trial_patterns += (select_and_remove_pattern(combinations))
    if trial_patterns[0] == 'E':
        trial_patterns.append("D")
    else:
        trial_patterns.append("E")

    # Populate the list with trials as per sequence.
    trials = []
    for trial_pattern in trial_patterns:
        if trial_pattern == 'E':
            trials.append(select_and_remove_df(english_stimuli))
        else:
            trials.append(select_and_remove_df(dutch_stimuli))
    
    return trials

def main():
    experiment_name = 'eeg_emotions'
    experiment_info = {'participant':'S'}

    _this_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(_this_directory)

    dlg = gui.DlgFromDict(dictionary=experiment_info, title=experiment_name)
    if dlg.OK == False: core.quit()
    experiment_info['date'] = data.getDateStr()
    experiment_info['expName'] = experiment_name
    file_name = _this_directory + os.sep + '%s_%s' %(experiment_info['participant'], experiment_info['date'])
    experiment_file = open("{}.txt".format(file_name), "w")

    # Create a window where the experiment will happen!
    win = visual.Window(size=(1024, 768), color='black', units='pix'	, fullscr=True)

    # The greeting window of the experiment. Send a trigger that it started.
    # Press "y" to proceed.
    send_trigger(TRIGGER_EXPERIMENT_START)
    instructions = visual.TextStim(win, text='''Welcome to the experiment. Please read the following instructions carefully. 
    During the experiment, you will be presented with emotion-laden passages (split into 4 parts) from Harry Potter book series. 
    Occasionally, after a passage you will also be asked a “yes/no” question regarding the contents of the passage. 
    Press “J” to answer “yes” and press “K” to answer “no” respectively. 
    The experiment itself consists of four blocks of 30 trials. Between blocks you can take short breaks 
    to make sure you feel comfortable throughout the experiment.
    Press 'Y' when you are ready to begin. The first block will be presented shortly after.''', wrapWidth=1000, height=20)
    instructions.draw()
    win.flip()
    event.waitKeys(keyList=['y'])
    event.clearEvents(eventType='keyboard')
    win.flip()
    core.wait(2)
        
    # The experimental loop itself.
    trivia_interval = 7 # Show trivia every 6 trials | 5 per block.
    number_of_blocks = 4
    wait_timer = core.Clock()
    for block in range(number_of_blocks):  # 4 blocks to mimic the intended experiment setup.
        trial_counter = 1  # Reset at the start of each block.
        last_trivia_shown = 0  # Tracks the last trial after which trivia was shown.
        
        if block != 0:
            block_window = visual.TextStim(win, text='', height=30)
            block_window.setText("Block {}/4 will begin shortly.".format(block+1))
            block_window.draw()
            wait_timer.reset()
            while wait_timer.getTime() < 2:
                pass
            win.flip()
        
        block_trials = create_block_trials(EN_subset, NL_subset)
        send_trigger(TRIGGER_BLOCK_START)

        for stim in block_trials:
            if 'ENP' in stim.columns:
                check_for_pause()
                send_trigger(TRIGGER_ENGLISH_ONSET)
                present_stimulus(win, stim, "EN")
            else:
                check_for_pause()
                send_trigger(TRIGGER_DUTCH_ONSET)
                present_stimulus(win, stim, "NL")
            trial_counter += 1
            
            wait_timer.reset()
            while wait_timer.getTime() < 0.5:
                pass
                
            if trial_counter - last_trivia_shown == trivia_interval:
                check_for_pause()
                if 'ENP' in stim.columns:
                    present_trivia(win, stim, experiment_file, lang = "EN")
                else:
                    present_trivia(win, stim, experiment_file, lang = "NL") # Present trivia related to the current stimulus.
                last_trivia_shown = trial_counter
            
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
    core.wait(10)  # Displays the message for 5 seconds or wait for a key press.

    win.close()
    core.quit()
    
main()
