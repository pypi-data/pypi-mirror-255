import os
import argparse
from pathlib import Path
import pathlib
import PhotonSimulator as sim
import functions.yaml.yaml_rw as write
import image_process.datacube_interface as Inter

def parse():

    parser = argparse.ArgumentParser(description='MKID phase simulation')
    parser.add_argument('--template', dest = 'save_link',help = 'Create a template of simulation data file')
    parser.add_argument('--yml', help ='Path to the simulation data file',dest ='yml')
    parser.add_argument('--output', help='Folder to store output', dest='output')
    parser.add_argument('--sim', help='Launch the simulation',dest = 'Launch')
    parser.add_argument('--image', help = 'Simulate an image', dest = 'Shape')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse()

    if args.save_link:
        link = args.save_link + '/template.yaml'
        write.write_template_image(link)

    if args.yml and args.output:
        print('yes')
    
    if args.Launch:
        print(sim.PhotonSimulator(args.Launch))
    
    if args.Shape:
        Inter.interface(int(eval(args.Shape)[0]),int(eval(args.Shape)[1]))