from decimal import *
import midi
import argparse

argsp = argparse.ArgumentParser()
argsp.add_argument('-o', '--output', type=str, help='output g-code file to generate (Default: song.gcode)', required=False, default="song.gcode")

requiredNamed = argsp.add_argument_group('required arguments')
requiredNamed.add_argument('-i', '--input', type=str, help='input midi file to convert', required=True)

args = argsp.parse_args()

# This lets us convert from Midi # to frequency
MIDI_NUMBERS = {
    0 : 8.1757989156,
    1 : 8.6619572180,
    2 : 9.1770239974,
    3 : 9.7227182413,
    4 : 10.3008611535,
    5 : 10.9133822323,
    6 : 11.5623257097,
    7 : 12.2498573744,
    8 : 12.9782717994,
    9 : 13.7500000000,
    10 : 14.5676175474,
    11 : 15.4338531643,
    12 : 16.3515978313,
    13 : 17.3239144361,
    14 : 18.3540479948,
    15 : 19.4454364826,
    16 : 20.6017223071,
    17 : 21.8267644646,
    18 : 23.1246514195,
    19 : 24.4997147489,
    20 : 25.9565435987,
    21 : 27.5000000000,
    22 : 29.1352350949,
    23 : 30.8677063285,
    24 : 32.7031956626,
    25 : 34.6478288721,
    26 : 36.7080959897,
    27 : 38.8908729653,
    28 : 41.2034446141,
    29 : 43.6535289291,
    30 : 46.2493028390,
    31 : 48.9994294977,
    32 : 51.9130871975,
    33 : 55.0000000000,
    34 : 58.2704701898,
    35 : 61.7354126570,
    36 : 65.4063913251,
    37 : 69.2956577442,
    38 : 73.4161919794,
    39 : 77.7817459305,
    40 : 82.4068892282,
    41 : 87.3070578583,
    42 : 92.4986056779,
    43 : 97.9988589954,
    44 : 103.8261743950,
    45 : 110.0000000000,
    46 : 116.5409403795,
    47 : 123.4708253140,
    48 : 130.8127826503,
    49 : 138.5913154884,
    50 : 146.8323839587,
    51 : 155.5634918610,
    52 : 164.8137784564,
    53 : 174.6141157165,
    54 : 184.9972113558,
    55 : 195.9977179909,
    56 : 207.6523487900,
    57 : 220.0000000000,
    58 : 233.0818807590,
    59 : 246.9416506281,
    60 : 261.6255653006,
    61 : 277.1826309769,
    62 : 293.6647679174,
    63 : 311.1269837221,
    64 : 329.6275569129,
    65 : 349.2282314330,
    66 : 369.9944227116,
    67 : 391.9954359817,
    68 : 415.3046975799,
    69 : 440.0000000000,
    70 : 466.1637615181,
    71 : 493.8833012561,
    72 : 523.2511306012,
    73 : 554.3652619537,
    74 : 587.3295358348,
    75 : 622.2539674442,
    76 : 659.2551138257,
    77 : 698.4564628660,
    78 : 739.9888454233,
    79 : 783.9908719635,
    80 : 830.6093951599,
    81 : 880.0000000000,
    82 : 932.3275230362,
    83 : 987.7666025122,
    84 : 1046.5022612024,
    85 : 1108.7305239075,
    86 : 1174.6590716696,
    87 : 1244.5079348883,
    88 : 1318.5102276515,
    89 : 1396.9129257320,
    90 : 1479.9776908465,
    91 : 1567.9817439270,
    92 : 1661.2187903198,
    93 : 1760.0000000000,
    94 : 1864.6550460724,
    95 : 1975.5332050245,
    96 : 2093.0045224048,
    97 : 2217.4610478150,
    98 : 2349.3181433393,
    99 : 2489.0158697766,
    100 : 2637.0204553030,
    101 : 2793.8258514640,
    102 : 2959.9553816931,
    103 : 3135.9634878540,
    104 : 3322.4375806396,
    105 : 3520.0000000000,
    106 : 3729.3100921447,
    107 : 3951.0664100490,
    108 : 4186.009044809,
    109 : 4434.922095630,
    110 : 4698.636286678,
    111 : 4978.031739553,
    112 : 5274.040910605,
    113 : 5587.651702928,
    114 : 5919.910763386,
    115 : 6271.926975708,
    116 : 6644.875161279,
    117 : 7040.000000000,
    118 : 7458.620234756,
    119 : 7902.132834658,
    120 : 8372.0180896192,
    121 : 8869.8441912599,
    122 : 9397.2725733570,
    123 : 9956.0634791066,
    124 : 10548.0818212118,
    125 : 11175.3034058561,
    126 : 11839.8215267723,
    127 : 12543.8539514160
    }

tempo = 120 # Default tempo for midi is 120 bpm

gcode = []
currentCode = None

pattern = midi.read_midifile(args.input)


for track in pattern[:]:
    # Some patterns have multiple tracks. These tracks
    # can sometimes be stuff like resolution and tempo
    # For now this is gonna stay simple, and only deal
    # with single track data (type 0)
    for event in track[:]:
        # We care about:
        #   TimeSignatureEvent (But not right now)
        #   SetTempoEvent (But not right now)
        #   NoteOnEvent
        #   NoteOffEvent
        
        # Note that we can only convert midis that don't have overlapping
        # notes!
        
        #now we find each NoteOnEvent, and convert it to gcode       
       
        if event.name == "Note On" and event.velocity != 0:
            # First convert Midi number to frequency
            currentCode = "M300 S" + str(MIDI_NUMBERS[event.get_pitch()]) + " P"

        #Some midi files give note offs, some give Note Ons with a velocity of 0 to denote the end of a note
        if (event.name == "Note Off" or (event.name == "Note On" and event.velocity == 0)) and currentCode != None:
            #add the delay 
            delay = event.tick * 0.001
            currentCode = currentCode + str((delay * 1000)) # Need to convert seconds to millis for Marlin
            gcode.append(currentCode)
            currentCode = None

#print gcode

#Export gcode to a file:
with open(args.output, 'w') as theFile:
    for item in gcode:
        theFile.write("%s\n" % item)

