#!/usr/bin/env python3
import sys
import os
from music21 import converter

def convert_musicxml_to_midi(xml_file, midi_file):
    try:
        # Print absolute path for debugging
        print(f"Attempting to open MusicXML file: {os.path.abspath(xml_file)}")
        score = converter.parse(xml_file)
        score.write('midi', fp=midi_file)
        print(f"Successfully converted '{xml_file}' to '{midi_file}'")
    except Exception as e:
        print(f"Error converting file: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python xmltoMidi.py input_file.xml output_file.mid")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.isfile(input_file):
        print(f"Input file not found: {os.path.abspath(input_file)}")
        sys.exit(1)
    
    convert_musicxml_to_midi(input_file, output_file)