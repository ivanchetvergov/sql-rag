from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime, timedelta, UTC
import random
from config import (
    UserConfig, TaskTypeConfig, MetricConfig, CompetitionConfig as CompetitionConfigData,
    DatasetConfig, PrizeConfig, SubmissionConfig, KernelConfig, SeedConfig
)
from src.db_models import (
    engine, create_tables, User, TaskType, Metric, Competition, CompetitionConfig as CompetitionConfigModel, Prize,
    Participation, Dataset, FileArtifact, Submission, Evaluation,
    LeaderboardRow, CodeKernel
)

Session = sessionmaker(bind=engine)

def insert_users(session, num_users=50):
    config = UserConfig()
    users = []
    for i in range(num_users):
        username = random.choice(config.usernames) + f"_{i}"
        email = f"{username}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}"
        bio = random.choice(config.bios) if random.random() > 0.3 else None
        created_at = datetime.now(UTC) - timedelta(days=random.randint(0, 365*10))
        user = User(username=username, email=email, bio=bio, created_at=created_at)
        users.append(user)
    session.add_all(users)
    session.commit()
    return users

def insert_task_types(session):
    config = TaskTypeConfig()
    task_types = []
    for code, desc, fmt in zip(config.codes, config.descriptions, config.response_formats):
        task_type = TaskType(code=code, description=desc, valid_response_format=fmt)
        task_types.append(task_type)
    session.add_all(task_types)
    session.commit()
    return task_types

def insert_metrics(session):
    config = MetricConfig()
    task_types = session.query(TaskType).all()
    metrics = []
    for name, formula, direction, desc in zip(config.names, config.formulas, config.directions, config.descriptions):
        task_type = random.choice(task_types)
        metric = Metric(
            task_type_id=task_type.task_type_id,
            name=name,
            formula=formula,
            optimization_direction=direction,
            description=desc
        )
        metrics.append(metric)
    session.add_all(metrics)
    session.commit()
    return metrics

def insert_competitions(session, num_competitions=20):
    config = CompetitionConfigData()
    users = session.query(User).all()
    task_types = session.query(TaskType).all()
    competitions = []
    for i in range(num_competitions):
        organizer = random.choice(users)
        task_type = random.choice(task_types)
        title = random.choice(config.titles) + f" {i+1}"
        description = random.choice(config.descriptions)
        start_at = datetime.now(UTC) - timedelta(days=random.randint(0, 365*10))
        end_at = start_at + timedelta(days=random.randint(30, 90))
        status = random.choice(config.statuses)
        competition = Competition(
            organizer_id=organizer.user_id,
            task_type_id=task_type.task_type_id,
            title=title,
            description=description,
            start_at=start_at,
            end_at=end_at,
            status=status
        )
        competitions.append(competition)
    session.add_all(competitions)
    session.commit()
    return competitions

def insert_competition_configs(session):
    competitions = session.query(Competition).all()
    metrics = session.query(Metric).all()
    configs = []
    for comp in competitions:
        num_configs = random.randint(1, 3)
        selected_metrics = random.sample(metrics, min(num_configs, len(metrics)))
        for metric in selected_metrics:
            aggregation_rule = random.choice(['best', 'average', 'median'])
            max_daily = random.randint(1, 10)
            config = CompetitionConfigModel(
                competition_id=comp.competition_id,
                metric_id=metric.metric_id,
                aggregation_rule=aggregation_rule,
                max_daily_submissions=max_daily
            )
            configs.append(config)
    session.add_all(configs)
    session.commit()

def insert_prizes(session):
    competitions = session.query(Competition).all()
    config = PrizeConfig()
    prizes = []
    for comp in competitions:
        num_prizes = random.randint(1, 4)
        for rank in range(1, num_prizes + 1):
            desc = random.choice(config.descriptions)
            amount = random.choice(config.amounts)
            currency = random.choice(config.currencies)
            prize = Prize(
                competition_id=comp.competition_id,
                rank_position=rank,
                description=desc,
                amount=amount,
                currency=currency
            )
            prizes.append(prize)
    session.add_all(prizes)
    session.commit()

def insert_participations(session, num_participations=100):
    users = session.query(User).all()
    competitions = session.query(Competition).all()
    participations = []
    for _ in range(num_participations):
        user = random.choice(users)
        competition = random.choice(competitions)
        registered_at = datetime.now(UTC) - timedelta(days=random.randint(0, 365*10))
        status = random.choice(['active', 'inactive', 'banned'])
        participation = Participation(
            user_id=user.user_id,
            competition_id=competition.competition_id,
            registered_at=registered_at,
            status=status
        )
        participations.append(participation)
    session.add_all(participations)
    session.commit()
    return participations

def insert_datasets(session):
    competitions = session.query(Competition).all()
    config = DatasetConfig()
    datasets = []
    for comp in competitions:
        num_datasets = random.randint(1, 4)
        for _ in range(num_datasets):
            name = random.choice(config.names)
            usage_type = random.choice(config.usage_types)
            is_hidden = random.choice([True, False])
            created_at = datetime.now(UTC) - timedelta(days=random.randint(0, 365*10))
            dataset = Dataset(
                competition_id=comp.competition_id,
                name=name,
                usage_type=usage_type,
                is_hidden=is_hidden,
                created_at=created_at
            )
            datasets.append(dataset)
    session.add_all(datasets)
    session.commit()
    return datasets

def insert_file_artifacts(session):
    datasets = session.query(Dataset).all()
    artifacts = []
    for dataset in datasets:
        num_files = random.randint(1, 5)
        for i in range(num_files):
            filename = f"data_{dataset.dataset_id}_{i}.csv"
            storage_path = f"/data/{filename}"
            checksum = f"checksum_{random.randint(1000, 9999)}"
            size_bytes = random.randint(1000, 1000000)
            artifact = FileArtifact(
                dataset_id=dataset.dataset_id,
                filename=filename,
                storage_path=storage_path,
                checksum=checksum,
                size_bytes=size_bytes
            )
            artifacts.append(artifact)
    session.add_all(artifacts)
    session.commit()

def insert_submissions(session, num_submissions=200):
    participations = session.query(Participation).all()
    config = SubmissionConfig()
    submissions = []
    for _ in range(num_submissions):
        participation = random.choice(participations)
        file_path = f"/submissions/sub_{random.randint(1000, 9999)}.zip"
        submitted_at = datetime.now(UTC) - timedelta(days=random.randint(0, 365*10))
        status = random.choice(config.statuses)
        submission = Submission(
            participation_id=participation.participation_id,
            file_path=file_path,
            submitted_at=submitted_at,
            status=status
        )
        submissions.append(submission)
    session.add_all(submissions)
    session.commit()
    return submissions

def insert_evaluations(session):
    submissions = session.query(Submission).all()
    evaluations = []
    for submission in submissions:
        metric_value = round(random.uniform(0.1, 1.0), 4)
        is_valid = random.choice([True, False])
        computed_at = datetime.now(UTC) - timedelta(hours=random.randint(0, 24))
        error_log = "Sample error" if not is_valid and random.random() > 0.5 else None
        evaluation = Evaluation(
            submission_id=submission.submission_id,
            metric_value=metric_value,
            is_valid=is_valid,
            computed_at=computed_at,
            error_log=error_log
        )
        evaluations.append(evaluation)
    session.add_all(evaluations)
    session.commit()
    return evaluations

def insert_leaderboard_rows(session):
    participations = session.query(Participation).all()
    evaluations = session.query(Evaluation).all()
    rows = []
    for participation in participations:
        if evaluations:
            best_evaluation = random.choice(evaluations)
            score = round(random.uniform(0.1, 1.0), 4)
            rank = random.randint(1, 50)
            updated_at = datetime.now(UTC) - timedelta(hours=random.randint(0, 24))
            row = LeaderboardRow(
                participation_id=participation.participation_id,
                best_evaluation_id=best_evaluation.evaluation_id,
                score=score,
                rank=rank,
                updated_at=updated_at
            )
            rows.append(row)
    session.add_all(rows)
    session.commit()

def insert_code_kernels(session):
    participations = session.query(Participation).all()
    evaluations = session.query(Evaluation).all()
    config = KernelConfig()
    kernels = []
    for participation in participations:
        if random.random() > 0.5:  # Not all participations have kernels
            evaluation = random.choice(evaluations) if evaluations else None
            title = random.choice(config.titles)
            source_code = f"# Sample code for {title}\nprint('Hello World')"
            language = random.choice(config.languages)
            created_at = datetime.now(UTC) - timedelta(days=random.randint(0, 365*10))
            kernel = CodeKernel(
                participation_id=participation.participation_id,
                evaluation_id=evaluation.evaluation_id if evaluation else None,
                title=title,
                source_code=source_code,
                language=language,
                created_at=created_at
            )
            kernels.append(kernel)
    session.add_all(kernels)
    session.commit()

def seed_database():
    # Tables are created by init.sql in Docker
    # create_tables()

    seed_config = SeedConfig()

    session = Session()
    try:
        print("Seeding database with synthetic data...")

        print("Clearing existing data...")
        # Clear tables in reverse dependency order
        tables_to_clear = [
            'CodeKernel', 'LeaderboardRow', 'Evaluation', 'Submission', 'FileArtifact',
            'Dataset', 'Participation', 'Prize', 'CompetitionConfig', 'Competition',
            'Metric', 'TaskType', 'User'
        ]
        for table in tables_to_clear:
            session.execute(text(f'TRUNCATE TABLE "{table}" CASCADE;'))
        session.commit()
        print("Existing data cleared.")

        # Insert base data
        insert_task_types(session)
        print("Task types inserted")

        insert_metrics(session)
        print("Metrics inserted")

        # Insert main data
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
