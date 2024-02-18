import numpy as np
from pydantic import BaseModel, validator

class Frame(BaseModel):
    data: np.ndarray
    pos_id: int
    
    class Config:
        arbitrary_types_allowed = True
        
    @validator('data')
    def check_data(cls, v):
        assert isinstance(v, np.ndarray), 'data must be a numpy array'
        return v

class Video(BaseModel):
    frames: list[Frame]
    fps: float
    total_frames: int
    duration: float
    
    @validator('frames')
    def check_frames(cls, v):
        assert len(v) > 0, 'frames must have at least one frame'
        return v
    
    @validator('fps')
    def check_fps(cls, v):
        assert v > 0, 'fps must be greater than 0'
        return v
    
    @validator('total_frames')
    def check_total_frames(cls, v):
        assert v > 0, 'total_frames must be greater than 0'
        return v
    
    @validator('duration')
    def check_duration(cls, v):
        assert v > 0, 'duration must be greater than 0'
        return v