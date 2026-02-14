from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime, timedelta, UTC
import random
from config import (
    UserConfig, TaskTypeConfig, MetricConfig, CompetitionConfig as CompetitionConfigData,
    DatasetConfig, PrizeConfig, SubmissionConfig, KernelConfig, SeedConfig
)
from src.db_models import (
    engine, User, TaskType, Metric, Competition, CompetitionConfig as CompetitionConfigModel, Prize,
    Participation, Dataset, FileArtifact, Submission, Evaluation,
    LeaderboardRow, CodeKernel
)

Session = sessionmaker(bind=engine)

def random_date(days_back=365*10):
    return datetime.now(UTC) - timedelta(days=random.randint(0, days_back))

def random_choice(items):
    return random.choice(items) if items else None

def bulk_insert(session, objects):
    if objects:
        session.add_all(objects)
        session.commit()

def insert_users(session, num_users=50):
    config = UserConfig()
    users = []
    for i in range(num_users):
        username = random_choice(config.usernames) + f"_{i}"
        email = f"{username}@{random_choice(['gmail.com', 'yahoo.com', 'outlook.com'])}"
        bio = random_choice(config.bios) if random.random() > 0.3 else None
        created_at = random_date()
        user = User(username=username, email=email, bio=bio, created_at=created_at)
        users.append(user)
    bulk_insert(session, users)
    return users

def insert_task_types(session):
    config = TaskTypeConfig()
    task_types = []
    for i in range(10):
        idx = i % len(config.codes)
        task_types.append(TaskType(
            code=config.codes[idx] + f"_{i//len(config.codes)+1}" if i >= len(config.codes) else config.codes[idx],
            description=config.descriptions[idx],
            valid_response_format=config.response_formats[idx]
        ))
    bulk_insert(session, task_types)
    return task_types

def insert_metrics(session):
    config = MetricConfig()
    task_types = session.query(TaskType).all()
    metrics = [
        Metric(
            task_type_id=random_choice(task_types).task_type_id,
            name=name, formula=formula, optimization_direction=direction, description=desc
        ) for name, formula, direction, desc in zip(
            config.names, config.formulas, config.directions, config.descriptions
        )
    ]
    bulk_insert(session, metrics)
    return metrics

def insert_competitions(session, num_competitions=20):
    config = CompetitionConfigData()
    users = session.query(User).all()
    task_types = session.query(TaskType).all()
    competitions = []
    for i in range(num_competitions):
        start_at = random_date()
        competition = Competition(
            organizer_id=random_choice(users).user_id,
            task_type_id=random_choice(task_types).task_type_id,
            title=random_choice(config.titles) + f" {i+1}",
            description=random_choice(config.descriptions),
            start_at=start_at,
            end_at=start_at + timedelta(days=random.randint(30, 90)),
            status=random_choice(config.statuses)
        )
        competitions.append(competition)
    bulk_insert(session, competitions)
    return competitions

def insert_competition_configs(session):
    competitions = session.query(Competition).all()
    metrics = session.query(Metric).all()
    configs = []
    for comp in competitions:
        selected_metrics = random.sample(metrics, min(random.randint(1, 3), len(metrics)))
        for metric in selected_metrics:
            configs.append(CompetitionConfigModel(
                competition_id=comp.competition_id,
                metric_id=metric.metric_id,
                aggregation_rule=random_choice(['best', 'average', 'median']),
                max_daily_submissions=random.randint(1, 10)
            ))
    bulk_insert(session, configs)

def insert_prizes(session):
    competitions = session.query(Competition).all()
    config = PrizeConfig()
    prizes = []
    for comp in competitions:
        num_prizes = random.randint(1, 4)
        for rank in range(1, num_prizes + 1):
            prizes.append(Prize(
                competition_id=comp.competition_id,
                rank_position=rank,
                description=random_choice(config.descriptions),
                amount=random_choice(config.amounts),
                currency=random_choice(config.currencies)
            ))
    bulk_insert(session, prizes)

def insert_participations(session, num_participations=100):
    users = session.query(User).all()
    competitions = session.query(Competition).all()
    participations = [
        Participation(
            user_id=random_choice(users).user_id,
            competition_id=random_choice(competitions).competition_id,
            registered_at=random_date(),
            status=random_choice(['active', 'inactive', 'banned'])
        ) for _ in range(num_participations)
    ]
    bulk_insert(session, participations)
    return participations

def insert_datasets(session):
    competitions = session.query(Competition).all()
    config = DatasetConfig()
    datasets = []
    for comp in competitions:
        for _ in range(random.randint(1, 4)):
            datasets.append(Dataset(
                competition_id=comp.competition_id,
                name=random_choice(config.names),
                usage_type=random_choice(config.usage_types),
                is_hidden=random.choice([True, False]),
                created_at=random_date()
            ))
    bulk_insert(session, datasets)
    return datasets

def insert_file_artifacts(session):
    datasets = session.query(Dataset).all()
    artifacts = []
    for dataset in datasets:
        for i in range(random.randint(1, 5)):
            artifacts.append(FileArtifact(
                dataset_id=dataset.dataset_id,
                filename=f"data_{dataset.dataset_id}_{i}.csv",
                storage_path=f"/data/data_{dataset.dataset_id}_{i}.csv",
                checksum=f"checksum_{random.randint(1000, 9999)}",
                size_bytes=random.randint(1000, 1000000)
            ))
    bulk_insert(session, artifacts)

def insert_submissions(session, num_submissions=200):
    participations = session.query(Participation).all()
    config = SubmissionConfig()
    submissions = [
        Submission(
            participation_id=random_choice(participations).participation_id,
            file_path=f"/submissions/sub_{random.randint(1000, 9999)}.zip",
            submitted_at=random_date(),
            status=random_choice(config.statuses)
        ) for _ in range(num_submissions)
    ]
    bulk_insert(session, submissions)
    return submissions

def insert_evaluations(session):
    submissions = session.query(Submission).all()
    evaluations = [
        Evaluation(
            submission_id=submission.submission_id,
            metric_value=round(random.uniform(0.1, 1.0), 4),
            is_valid=random.choice([True, False]),
            computed_at=datetime.now(UTC) - timedelta(hours=random.randint(0, 24)),
            error_log="Sample error" if not random.choice([True, False]) and random.random() > 0.5 else None
        ) for submission in submissions
    ]
    bulk_insert(session, evaluations)
    return evaluations

def insert_leaderboard_rows(session):
    participations = session.query(Participation).all()
    evaluations = session.query(Evaluation).all()
    rows = [
        LeaderboardRow(
            participation_id=participation.participation_id,
            best_evaluation_id=random_choice(evaluations).evaluation_id if evaluations else None,
            score=round(random.uniform(0.1, 1.0), 4),
            rank=random.randint(1, 50),
            updated_at=datetime.now(UTC) - timedelta(hours=random.randint(0, 24))
        ) for participation in participations if evaluations
    ]
    bulk_insert(session, rows)

def insert_code_kernels(session):
    participations = session.query(Participation).all()
    evaluations = session.query(Evaluation).all()
    config = KernelConfig()
    kernels = []
    for participation in participations:
        if random.random() > 0.5:
            evaluation = random_choice(evaluations)
            kernels.append(CodeKernel(
                participation_id=participation.participation_id,
                evaluation_id=evaluation.evaluation_id if evaluation else None,
                title=random_choice(config.titles),
                source_code=f"# Sample code for {random_choice(config.titles)}\nprint('Hello World')",
                language=random_choice(config.languages),
                created_at=random_date()
            ))
    bulk_insert(session, kernels)

def seed_database():

    seed_config = SeedConfig()

    session = Session()
    try:
        print("Seeding database with synthetic data...")

        print("Clearing existing data...")
        tables_to_clear = [
            'CodeKernel', 'LeaderboardRow', 'Evaluation', 'Submission', 'FileArtifact',
            'Dataset', 'Participation', 'Prize', 'CompetitionConfig', 'Competition',
            'Metric', 'TaskType', 'User'
        ]
        for table in tables_to_clear:
            session.execute(text(f'TRUNCATE TABLE "{table}" CASCADE;'))
        session.commit()
        print("Existing data cleared.")

        insert_task_types(session)
        print("Task types inserted")

        insert_metrics(session)
        print("Metrics inserted")

        insert_users(session, seed_config.num_users)
        print("Users inserted")

        insert_competitions(session, seed_config.num_competitions)
        print("Competitions inserted")

        insert_competition_configs(session)
        print("Competition configs inserted")

        insert_prizes(session)
        print("Prizes inserted")

        insert_participations(session, seed_config.num_participations)
        print("Participations inserted")

        insert_datasets(session)
        print("Datasets inserted")

        insert_file_artifacts(session)
        print("File artifacts inserted")

        insert_submissions(session, seed_config.num_submissions)
        print("Submissions inserted")

        insert_evaluations(session)
        print("Evaluations inserted")

        insert_leaderboard_rows(session)
        print("Leaderboard rows inserted")

        insert_code_kernels(session)
        print("Code kernels inserted")

        session.commit()
        print("Database seeded successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()
