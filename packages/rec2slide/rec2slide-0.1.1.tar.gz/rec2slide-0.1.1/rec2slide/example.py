from rec2slide import Engine, Config, Utils

def main():
    config = Config(
        interval=20,
        threshold=1000.0,
        score="mse"
    )
    
    engine = Engine(config)
    result = engine("./data/example.mp4")
    Utils.frames2pdf(result, "./data/example.pdf")
    
if __name__ == "__main__":
    main()