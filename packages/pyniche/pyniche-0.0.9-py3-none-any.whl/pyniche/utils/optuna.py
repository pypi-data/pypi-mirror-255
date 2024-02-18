import optuna
import os

def init_optimizer(
        dir_db: str,
        name_db: str = "optimization.db",
        name_study: str = "optimization",
    ):
        path_db = "sqlite:///%s" % os.path.join(dir_db, name_db)
        if not os.path.exists(dir_db):
            os.makedirs(dir_db)

        try:
            study = optuna.load_study(
                storage=path_db,
                study_name=name_study,
            )
        except KeyError:
            # if study does not exist, create it
            study = optuna.create_study(
                storage=path_db,
                study_name=name_study,
                direction="minimize",
            )
        return study