import optuna
import os


class NicheOptimizer:
    def __init__(
        self,
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
        self.optimizer = study

    def optimize(
        self,
        objective: callable,
        n_trials: int = 500,
    ):
        self.optimizer.optimize(objective, n_trials=n_trials)


# def objective(trial, dataset):
#     # Suggest hyperparameter values using the trial object
#     learning_rate = trial.suggest_float("learning_rate", 1e-6, 1e-2, log=True)
#     batch_size = trial.suggest_categorical("batch_size", [4, 8, 16, 32, 64])
#     n_blocks = trial.suggest_int("n_blocks", 1, 6)
#     print("The parameters are: ", learning_rate, batch_size, n_blocks)

#     # Train the model with the given hyperparameters and return the validation loss
#     test_loss = sperm_teller(
#         dataset=dataset,
#         epochs=40,
#         lr=learning_rate,
#         batch=batch_size,
#         n_blocks=n_blocks,
#     )
#     return test_loss

# study.optimize(lambda trial: objective(trial, dataset), n_trials=500)
# study.optimize(objective, n_trials=50)
