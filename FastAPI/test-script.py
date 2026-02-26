import sys

def main():
    input_data = sys.argv[1] if len(sys.argv) > 1 else "No input provided"
    print(f"Received input: {input_data}")

if __name__ == "__main__":
    main()