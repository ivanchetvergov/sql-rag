from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
    bio = Column(Text)

    organized_competitions = relationship("Competition", back_populates="organizer")
    participations = relationship("Participation", back_populates="user")

class TaskType(Base):
    __tablename__ = 'TaskType'
    task_type_id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    valid_response_format = Column(Text)

    competitions = relationship("Competition", back_populates="task_type")
    metrics = relationship("Metric", back_populates="task_type")

class Metric(Base):
    __tablename__ = 'Metric'
    metric_id = Column(Integer, primary_key=True)
    task_type_id = Column(Integer, ForeignKey('TaskType.task_type_id'))
    name = Column(String(100), nullable=False)
    formula = Column(Text)
    optimization_direction = Column(String(10))
    description = Column(Text)

    task_type = relationship("TaskType", back_populates="metrics")
    competition_configs = relationship("CompetitionConfig", back_populates="metric")

class Competition(Base):
    __tablename__ = 'Competition'
    competition_id = Column(Integer, primary_key=True)
    organizer_id = Column(Integer, ForeignKey('User.user_id'))
    task_type_id = Column(Integer, ForeignKey('TaskType.task_type_id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    status = Column(String(20), default='draft')

    organizer = relationship("User", back_populates="organized_competitions")
    task_type = relationship("TaskType", back_populates="competitions")
    competition_configs = relationship("CompetitionConfig", back_populates="competition")
    prizes = relationship("Prize", back_populates="competition")
    participations = relationship("Participation", back_populates="competition")
    datasets = relationship("Dataset", back_populates="competition")

class CompetitionConfig(Base):
    __tablename__ = 'CompetitionConfig'
    config_id = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey('Competition.competition_id'))
    metric_id = Column(Integer, ForeignKey('Metric.metric_id'))
    aggregation_rule = Column(String(20), default='best')
    max_daily_submissions = Column(Integer, default=5)

    competition = relationship("Competition", back_populates="competition_configs")
    metric = relationship("Metric", back_populates="competition_configs")

class Prize(Base):
    __tablename__ = 'Prize'
    prize_id = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey('Competition.competition_id'))
    rank_position = Column(Integer)
    description = Column(Text)
    amount = Column(DECIMAL(15, 2))
    currency = Column(String(10), default='USD')

    competition = relationship("Competition", back_populates="prizes")

class Participation(Base):
    __tablename__ = 'Participation'
    participation_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.user_id'))
    competition_id = Column(Integer, ForeignKey('Competition.competition_id'))
    registered_at = Column(DateTime, default=datetime.now(UTC))
    status = Column(String(20), default='active')

    user = relationship("User", back_populates="participations")
    competition = relationship("Competition", back_populates="participations")
    submissions = relationship("Submission", back_populates="participation")
    leaderboard_rows = relationship("LeaderboardRow", back_populates="participation")
    code_kernels = relationship("CodeKernel", back_populates="participation")

class Dataset(Base):
    __tablename__ = 'Dataset'
    dataset_id = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey('Competition.competition_id'))
    name = Column(String(255), nullable=False)
    usage_type = Column(String(20))
    is_hidden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(UTC))

    competition = relationship("Competition", back_populates="datasets")
    file_artifacts = relationship("FileArtifact", back_populates="dataset")

class FileArtifact(Base):
    __tablename__ = 'FileArtifact'
    file_id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('Dataset.dataset_id'))
    filename = Column(String(255), nullable=False)
    storage_path = Column(Text)
    checksum = Column(String(64))
    size_bytes = Column(Integer)

    dataset = relationship("Dataset", back_populates="file_artifacts")

class Submission(Base):
    __tablename__ = 'Submission'
    submission_id = Column(Integer, primary_key=True)
    participation_id = Column(Integer, ForeignKey('Participation.participation_id'))
    file_path = Column(Text)
    submitted_at = Column(DateTime, default=datetime.now(UTC))
    status = Column(String(20), default='queued')

    participation = relationship("Participation", back_populates="submissions")
    evaluations = relationship("Evaluation", back_populates="submission")

class Evaluation(Base):
    __tablename__ = 'Evaluation'
    evaluation_id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey('Submission.submission_id'))
    metric_value = Column(DECIMAL(20, 10))
    is_valid = Column(Boolean, default=True)
    computed_at = Column(DateTime, default=datetime.now(UTC))
    error_log = Column(Text)

    submission = relationship("Submission", back_populates="evaluations")
    leaderboard_rows = relationship("LeaderboardRow", back_populates="best_evaluation")
    code_kernels = relationship("CodeKernel", back_populates="evaluation")

class LeaderboardRow(Base):
    __tablename__ = 'LeaderboardRow'
    row_id = Column(Integer, primary_key=True)
    participation_id = Column(Integer, ForeignKey('Participation.participation_id'))
    best_evaluation_id = Column(Integer, ForeignKey('Evaluation.evaluation_id'))
    score = Column(DECIMAL(20, 10))
    rank = Column(Integer)
    updated_at = Column(DateTime, default=datetime.now(UTC))

    participation = relationship("Participation", back_populates="leaderboard_rows")
    best_evaluation = relationship("Evaluation", back_populates="leaderboard_rows")

class CodeKernel(Base):
    __tablename__ = 'CodeKernel'
    kernel_id = Column(Integer, primary_key=True)
    participation_id = Column(Integer, ForeignKey('Participation.participation_id'))
    evaluation_id = Column(Integer, ForeignKey('Evaluation.evaluation_id'), nullable=True)
    title = Column(String(255))
    source_code = Column(Text)
    language = Column(String(50))
    created_at = Column(DateTime, default=datetime.now(UTC))

    participation = relationship("Participation", back_populates="code_kernels")
    evaluation = relationship("Evaluation", back_populates="code_kernels")


DATABASE_URL = "postgresql://user:password@localhost:5432/ml_comp"

engine = create_engine(DATABASE_URL, echo=False)

def create_tables():
    Base.metadata.create_all(bind=engine)
