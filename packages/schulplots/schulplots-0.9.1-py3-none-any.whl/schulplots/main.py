
from .converter import converter
from .figure_description import FigureDescription
import argparse
from os import path
from typing import Optional

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

def generate_plot(infile: str, outfile: Optional[str] = None):
    with open(infile, "r", encoding="utf-8") as f:
        fdsc = converter.loads(f.read(), FigureDescription)
        fdsc.figure.output_file = outfile
        fdsc.create_figure()
def main():
    parser = argparse.ArgumentParser(
        prog="schulplots.py", 
        description="Create function plots styled similar to the conventions used in German schools.\n"\
            "For documentation, see https://schulplots.hans-aschauer.de"
    )
    parser.add_argument("filename", help="Description of the figure, in YAML format")
    parser.add_argument("--output", "-o", 
                        help="Name out output file. If not provided (and --show is "\
                             "not given), store the figure in the current working "\
                             "directory.")
    parser.add_argument("--show", "-s", help="Show plot in interactive window. May not be used with --output.",
                        action="store_true", default=False)

    args = parser.parse_args()
    if args.output is not None and args.show:
        parser.print_help()
    elif args.output is not None and not args.show:
        generate_plot(args.filename, args.output)
        #fdsc.figure.output_file = args.output
    elif args.output is None and args.show:
        generate_plot(args.filename, None)
        #fdsc.figure.output_file = None
    elif args.output is None and not args.show:
        bname, _ = path.splitext(path.basename(args.filename))
        generate_plot(args.filename, bname + ".png")
        #fdsc.figure.output_file = bname + ".png"
        
    else:
        raise ValueError("Logic error: this should not happen")
    #fdsc.create_figure()
        
