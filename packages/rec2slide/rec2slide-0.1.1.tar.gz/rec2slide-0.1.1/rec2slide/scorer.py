import numpy as np
from enum import Enum
 
class ScoringMethod(str, Enum):
    mse = "mse"

class SimilarityComparer:
    def mse(img_a, img_b):
        err = np.sum((img_a.astype("float") - img_b.astype("float")) ** 2)
        err /= float(img_a.shape[0] * img_a.shape[1])
        return err
    
# TODO: Implement another method to compare images