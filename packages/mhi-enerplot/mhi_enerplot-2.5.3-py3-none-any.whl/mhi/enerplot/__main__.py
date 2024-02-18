import mhi.common
from mhi.enerplot import VERSION
from mhi.enerplot.buildtime import BUILD_TIME


def main():    
    print("MHI Enerplot Library v{} ({})".format(VERSION, BUILD_TIME))
    print("(c) Manitoba Hydro International Ltd.")
    print()
    print(mhi.common.version_msg())
    
if __name__ == '__main__':
    main()
