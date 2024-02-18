import argparse
from plx_false_positives.find_false_positives import print_false_positives


def main():
    parser = argparse.ArgumentParser(
        prog="plx_false_positives",
        description="Finds false positives.",
    )

    parser.add_argument('file', metavar ='file name', type = str, 
                        help ='Json file')
    # parser.add_argument('integers', metavar ='N', type = int, nargs ='+', 
    #                     help ='an integer for the accumulator') 
    # parser.add_argument('-greet', action ='store_const', const = True, 
    #                     default = False, dest ='greet', 
    #                     help ="Greet Message from Geeks For Geeks.") 
    # parser.add_argument('--sum', dest ='accumulate', action ='store_const', 
    #                     const = sum, default = max, 
    #                     help ='sum the integers (default: find the max)') 
  
    args = parser.parse_args()

    print_false_positives(args.file)
    