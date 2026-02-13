from pydantic import BaseModel
from typing import List

class UserConfig(BaseModel):
    usernames: List[str] = [
        "alex_tech", "maria_data", "john_ml", "sara_ai", "david_dev",
        "emma_analyst", "ryan_engineer", "lisa_research", "mike_coder", "anna_sci"
    ]
    emails: List[str] = [
        "alex@tech.com", "maria@data.com", "john@ml.com", "sara@ai.com", "david@dev.com",
        "emma@analyst.com", "ryan@engineer.com", "lisa@research.com", "mike@coder.com", "anna@sci.com"
    ]
    bios: List[str] = [
        "Passionate about machine learning and data science.",
        "Data analyst with 5 years of experience.",
        "ML engineer specializing in NLP.",
        "AI researcher focused on computer vision.",
        "Software developer with ML background.",
        "Data scientist at tech startup.",
        "Research engineer in deep learning.",
        "Coder and ML enthusiast.",
        "Scientist working on AI ethics.",
        "Analyst in predictive modeling."
    ]

class TaskTypeConfig(BaseModel):
    codes: List[str] = ["classification", "regression", "nlp", "cv", "ranking"]
    descriptions: List[str] = [
        "Binary or multi-class classification task.",
        "Predicting continuous numerical values.",
        "Natural language processing tasks.",
        "Computer vision and image analysis.",
        "Ranking and recommendation tasks."
    ]
    response_formats: List[str] = [
        "JSON with class probabilities",
        "CSV with predicted values",
        "Text file with processed output",
        "Image annotations",
        "Time series predictions"
    ]

class MetricConfig(BaseModel):
    names: List[str] = ["accuracy", "f1_score", "mae", "rmse", "bleu", "iou"]
    formulas: List[str] = [
        "correct_predictions / total_predictions",
        "2 * (precision * recall) / (precision + recall)",
        "mean(|predicted - actual|)",
        "sqrt(mean((predicted - actual)^2))",
        "BLEU score calculation",
        "intersection / union"
    ]
    directions: List[str] = ["maximize", "maximize", "minimize", "minimize", "maximize", "maximize"]
    descriptions: List[str] = [
        "Percentage of correct predictions.",
        "Harmonic mean of precision and recall.",
        "Mean absolute error.",
        "Root mean squared error.",
        "BLEU score for text generation.",
        "Intersection over union for object detection."
    ]

class CompetitionConfig(BaseModel):
    titles: List[str] = [
        "Image Classification Challenge",
        "Sentiment Analysis Competition",
        "House Price Prediction",
        "Time Series Forecasting",
        "Object Detection Contest"
    ]
    descriptions: List[str] = [
        "Classify images into predefined categories.",
        "Analyze sentiment in text reviews.",
        "Predict house prices based on features.",
        "Forecast future values in time series data.",
        "Detect and localize objects in images."
    ]
    statuses: List[str] = ["draft", "active", "completed", "cancelled"]

class DatasetConfig(BaseModel):
    names: List[str] = ["train_data", "test_data", "validation_data", "sample_data"]
    usage_types: List[str] = ["train", "test", "validation", "sample"]

class PrizeConfig(BaseModel):
    descriptions: List[str] = [
        "First place prize",
        "Second place prize",
        "Third place prize",
        "Participation certificate"
    ]
    amounts: List[float] = [10000.0, 5000.0, 2500.0, 0.0]
    currencies: List[str] = ["USD", "EUR", "USD", "USD"]

class SubmissionConfig(BaseModel):
    statuses: List[str] = ["queued", "processing", "completed", "failed"]

class KernelConfig(BaseModel):
    titles: List[str] = [
        "Baseline Model",
        "Advanced Neural Network",
        "Ensemble Approach",
        "Feature Engineering Script"
    ]
    languages: List[str] = ["python", "r", "julia", "cpp"]

class SeedConfig(BaseModel):
    num_users: int = 50
    num_competitions: int = 20
    num_participations: int = 100
    num_submissions: int = 200
