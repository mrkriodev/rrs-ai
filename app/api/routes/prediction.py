
from fastapi import APIRouter

from app.models.payloads import RequestPayload
from app.models.prediction import PredictionResult
#from app.conf.config import MODEL_PATH
from os import getenv
from ultralytics import YOLO

router = APIRouter()
MODEL_PATH = getenv("MODEL_PATH", "")
model = YOLO(MODEL_PATH)

#{"videos": ["Ford", "BMW", "Fiat"]}


def predict(video):
   
   results = model.predict(
      source=video,
      conf=0.85
   )

   class_probabilities ={}
   for r in results:
      for c in r.boxes.cls:
         for p in r.boxes.conf.tolist():
            if model.names[int(c)] in class_probabilities:
               class_probabilities[model.names[int(c)]].append(p)
            else:
               class_probabilities[model.names[int(c)]] = [p]
   max_prob_class = max(class_probabilities, key=lambda k: max(class_probabilities[k], default=0.0))
   max_probability = max(class_probabilities[max_prob_class], default=0.0)
   return max_prob_class, max_probability, None


@router.post("/predict", response_model=list[PredictionResult], name="predict")
def post_predict(payload: RequestPayload = None) -> list[PredictionResult]:

    if payload is None:
        raise ValueError("Invalid payload")
    
    vid = payload.videos
    ans = []

    for x in vid:
        with open(x, "wb") as file:
            ftp_server.retrbinary(f"RETR {x}", file.write)

        res = predict()

        #preproccess
        res = PredictionResult(category=0,probability=0, fccc_code=0)
        ans.res(res)

    return ans
        
    '''x = [[payload.feature1, payload.feature2]]

    y = clf.predict(x)[0]
    prob = clf.predict_proba(x)[0].tolist()

    pred = PredictionResult(label=y, probability=prob)

    return pred'''