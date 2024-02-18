from pydantic import BaseModel
from scorer import ScoringMethod, SimilarityComparer
from model import Frame
from utils import Utils

class Config(BaseModel):
    interval: int = 10
    threshold: float = 1000.0
    score: ScoringMethod = "mse"
    
class Engine:
    def __init__(self, args: Config = Config()):
        self.args = args
        if self.args.score == "mse":
            self.score = SimilarityComparer.mse
        
    # def compare_frames_1(self, frame_a: Frame) -> float:
    #     """ 
    #     method 1: compare each frame with distinct frames that have been found ; slower
    #     """
    #     return [self.score(frame_a.data, frame_b.data) for frame_b in self.distinct_frames]
    
    def __call__(self, path: str) -> list[Frame]:
        """ 
        method 2: compare each frame with the previous frame ; faster
        """
        self.video = Utils.read_video(path, self.args.interval)
        self.distinct_frames = [self.video.frames[0]]
        for i in range(1, len(self.video.frames)):
            mse_value = self.score(self.video.frames[i].data, self.video.frames[i-1].data)
            if mse_value > self.args.threshold:
                self.distinct_frames.append(self.video.frames[i])
        
        return self.distinct_frames

class Utils(Utils):
    pass