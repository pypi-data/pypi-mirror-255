import argparse


def main():
    parser = argparse.argumentParser(description="My data making program")
    parser.add_argument("-seg", type=str, help="An example argument")

    args = parser.parse_args()

    # Your code here
    print(args.seg)


if __name__ == "__main__":
    main()
