import os
import optuna


class Optimizer:
    def __init__(
        self,
        dir_db,
        name_db="optimization.db",
        name_study="optimization",
        n_trials=500,
    ):
        path_db = "sqlite:///%s" % os.path.join(dir_db, name_db)
        if not os.path.exists(dir_db):
            os.makedirs(dir_db)

        self.n_trials = n_trials
        self.study = optuna.create_study(
            storage=path_db,
            study_name=name_study,
            direction="minimize",
            load_if_exists=True,
        )

    def run(
        self,
        objective: callable,
    ):
        self.study.optimize(objective, n_trials=self.n_trials)
        return self.study.best_params, self.study.best_value
