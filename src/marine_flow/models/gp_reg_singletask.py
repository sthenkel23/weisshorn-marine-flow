import torch
import gpytorch

#
# MODEL CREATION
# more information -> http://www.gaussianprocess.org/gpml/chapters/RW2.pdf


class ExactGPModel(gpytorch.models.ExactGP):
    """ """

    def __init__(self, _batch_size, train_x, train_y, likelihood):
        super().__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.ConstantMean(batch_shape=_batch_size)
        self.covar_module = gpytorch.kernels.ScaleKernel(
            # gpytorch.kernels.MaternKernel(batch_shape=_batch_size),
            gpytorch.kernels.RBFKernel(batch_shape=_batch_size),
            batch_shape=_batch_size,
        )

    def forward(self, x):
        """

        :param x:

        """
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)


def prepare_model(train_x, train_y, seed, device_type):
    """

    :param train_x: param train_y:
    :param seed: param device_type:
    :param train_y: param device_type:
    :param device_type:

    """
    torch.manual_seed(seed)
    _batch_size = [train_y.shape[0]]
    # initialize likelihood and model
    likelihood = gpytorch.likelihoods.GaussianLikelihood(batch_shape=_batch_size).to(device_type)
    model = ExactGPModel(_batch_size, train_x, train_y, likelihood).to(device_type)
    return model, likelihood


def initialize_model_means(model, train_y):
    """

    :param model: param train_y:
    :param train_y:

    """
    means = torch.mean(train_y, 1)
    hypers = {
        # 'likelihood.noise_covar.noise': torch.tensor(1.),
        # 'covar_module.base_kernel.lengthscale': torch.tensor(0.5),
        # 'covar_module.outputscale': torch.tensor(2.),
        "mean_module.constant": means
    }
    return model.initialize(**hypers)


def train(model_in, n_iter, train_x, train_y):
    """

    :param model_in: param n_iter:
    :param train_x: param train_y:
xs    :param n_iter: param train_y:
    :param train_y:

    """
    model = model_in[0]
    likelihood = model_in[1]

    # Find optimal model hyperparameters
    model.train()
    likelihood.train()

    # Use the adam optimizer
    optimizer = torch.optim.Adam(
        [
            {"params": model.parameters()},  # Includes GaussianLikelihood parameters
        ],
        lr=0.1,
    )

    # "Loss" for GPs - the marginal log likelihood
    mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)

    for i in range(n_iter):
        # Zero gradients from previous iteration
        optimizer.zero_grad()
        # Output from model
        output = model(train_x)
        # Calc loss and backprop gradients
        loss = -mll(output, train_y).sum()
        loss.backward()
        # print('Iter %d/%d - Loss: %.3f' % (i + 1, n_iter, loss.item()))
        optimizer.step()

    return (model, likelihood)


def evaluate(model_in, test_x):
    """

    :param model_in: param test_x:
    :param test_x:

    """
    model = model_in[0]
    likelihood = model_in[1]

    model.eval()
    likelihood.eval()

    with torch.no_grad():  # , gpytorch.settings.fast_pred_var():
        posterior = model(test_x)
        y_preds = likelihood(model(test_x))
    return (y_preds, posterior)


def fill_response(df, eligible_features, model_response, MODEL_OUTPUT):
    """

    :param df: param eligible_features:
    :param model_response: param MODEL_OUTPUT:
    :param eligible_features: param MODEL_OUTPUT:
    :param MODEL_OUTPUT:

    """
    for i, feature in enumerate([i + "_{}".format(MODEL_OUTPUT) for i in eligible_features]):
        df[feature] = model_response.detach().cpu().numpy()[i, :]
    return df

