import numpy as np
import pytest

import neuroboros as nb


class TestRidge:
    def test_ridge(self):
        linear_model = pytest.importorskip('sklearn.linear_model')

        rng = np.random.default_rng(0)
        X = rng.standard_normal((100, 10))
        y = rng.standard_normal((100,))
        X_test = rng.standard_normal((10, 10))

        for alpha in [1e-3, 1, 1e3]:
            for fit_intercept in [True, False]:
                model = linear_model.Ridge(alpha=alpha, fit_intercept=fit_intercept)
                model.fit(X, y)
                beta = model.coef_
                beta0 = model.intercept_

                beta2, yhat2 = nb.linalg.ridge(
                    X, y, alpha, npc=None, fit_intercept=fit_intercept, X_test=X_test
                )
                if fit_intercept:
                    np.testing.assert_allclose(beta, beta2[:-1], atol=1e-10)
                    np.testing.assert_allclose(beta0, beta2[-1], atol=1e-10)
                else:
                    np.testing.assert_allclose(beta, beta2, atol=1e-10)

                yhat = model.predict(X_test)
                np.testing.assert_allclose(yhat, yhat2, atol=1e-10)

    def test_ridge_mask(self):
        linear_model = pytest.importorskip('sklearn.linear_model')

        rng = np.random.default_rng(0)
        X = rng.standard_normal((200, 10))
        y = rng.standard_normal((100,))
        X_test = rng.standard_normal((10, 10))
        mask = np.zeros((200,), dtype=bool)
        mask[:100] = True
        rng.shuffle(mask)

        for alpha in [1e-3, 1, 1e3]:
            for fit_intercept in [True, False]:
                model = linear_model.Ridge(alpha=alpha, fit_intercept=fit_intercept)
                model.fit(X[mask], y)
                beta = model.coef_
                beta0 = model.intercept_

                beta2, yhat2 = nb.linalg.ridge(
                    X,
                    y,
                    alpha,
                    npc=None,
                    fit_intercept=fit_intercept,
                    X_test=X_test,
                    mask=mask,
                )
                if fit_intercept:
                    np.testing.assert_allclose(beta, beta2[:-1], atol=1e-10)
                    np.testing.assert_allclose(beta0, beta2[-1], atol=1e-10)
                else:
                    np.testing.assert_allclose(beta, beta2, atol=1e-10)

                yhat = model.predict(X_test)
                np.testing.assert_allclose(yhat, yhat2, atol=1e-10)

    def test_ridge_npcs(self):
        linear_model = pytest.importorskip('sklearn.linear_model')
        decomposition = pytest.importorskip('sklearn.decomposition')

        rng = np.random.default_rng(0)
        X = rng.standard_normal((100, 10))
        X -= X.mean(axis=0, keepdims=True)
        y = rng.standard_normal((100,))
        X_test = rng.standard_normal((10, 10))

        for alpha in [1e-3, 1, 1e3]:
            for fit_intercept in [True, False]:
                for npc in [1, 3, 10]:
                    pca = decomposition.PCA(n_components=npc)
                    model = linear_model.Ridge(alpha=alpha, fit_intercept=fit_intercept)
                    model.fit(pca.fit_transform(X), y)
                    yhat = model.predict(pca.transform(X_test))

                    yhat2 = nb.linalg.ridge(
                        X, y, alpha, npc=npc, fit_intercept=fit_intercept, X_test=X_test
                    )[1]

                    np.testing.assert_allclose(yhat, yhat2, atol=1e-10)

    def test_multiple_y(self):
        rng = np.random.default_rng(0)
        X = rng.standard_normal((100, 10))
        Y = rng.standard_normal((100, 3))
        X_test = rng.standard_normal((10, 10))

        for alpha in [1e-3, 1, 1e3]:
            for fit_intercept in [True, False]:
                for npc in [None, 1, 3, 10]:
                    beta, yhat = nb.linalg.ridge(
                        X, Y, alpha, npc=npc, fit_intercept=fit_intercept, X_test=X_test
                    )
                    for i in range(Y.shape[1]):
                        beta2, yhat2 = nb.linalg.ridge(
                            X,
                            Y[:, i],
                            alpha,
                            npc=npc,
                            fit_intercept=fit_intercept,
                            X_test=X_test,
                        )
                        np.testing.assert_allclose(beta[:, i], beta2, atol=1e-10)
                        np.testing.assert_allclose(yhat[:, i], yhat2, atol=1e-10)


class TestRidgeGrid:
    def test_ridge_grid(self):
        rng = np.random.default_rng(0)
        X = rng.standard_normal((100, 10))
        y = rng.standard_normal((100,))
        X_test = rng.standard_normal((10, 10))

        alphas = [1e-3, 1, 1e3]
        npcs = [1, 3, 5, 10]

        for fit_intercept in [True, False]:
            yhats = nb.linalg.ridge_grid(
                X, y, alphas, npcs, fit_intercept=fit_intercept, X_test=X_test
            )
            assert yhats.shape == (10, 3, 4)
            for i, alpha in enumerate(alphas):
                for j, npc in enumerate(npcs):
                    beta, yhat = nb.linalg.ridge(
                        X, y, alpha, npc=npc, fit_intercept=fit_intercept, X_test=X_test
                    )
                    np.testing.assert_allclose(yhat, yhats[:, i, j], atol=1e-10)

    def test_ridge_grid_mask(self):
        rng = np.random.default_rng(0)
        X = rng.standard_normal((200, 10))
        y = rng.standard_normal((100,))
        X_test = rng.standard_normal((10, 10))
        mask = np.zeros((200,), dtype=bool)
        mask[:100] = True
        rng.shuffle(mask)

        alphas = [1e-3, 1, 1e3]
        npcs = [1, 3, 5, 10]

        for fit_intercept in [True, False]:
            yhats = nb.linalg.ridge_grid(
                X,
                y,
                alphas,
                npcs,
                fit_intercept=fit_intercept,
                X_test=X_test,
                mask=mask,
            )
            assert yhats.shape == (10, 3, 4)
            for i, alpha in enumerate(alphas):
                for j, npc in enumerate(npcs):
                    beta, yhat = nb.linalg.ridge(
                        X,
                        y,
                        alpha,
                        npc=npc,
                        fit_intercept=fit_intercept,
                        X_test=X_test,
                        mask=mask,
                    )
                    np.testing.assert_allclose(yhat, yhats[:, i, j], atol=1e-10)

    def test_ridge_grid_mulptiple_y(self):
        rng = np.random.default_rng(0)
        X = rng.standard_normal((100, 10))
        Y = rng.standard_normal((100, 3))
        X_test = rng.standard_normal((10, 10))

        alphas = [1e-3, 1, 1e3]
        npcs = [1, 3, 5, 10]

        for fit_intercept in [True, False]:
            yhats = nb.linalg.ridge_grid(
                X, Y, alphas, npcs, fit_intercept=fit_intercept, X_test=X_test
            )
            assert yhats.shape == (10, 3, 3, 4)
            for i, alpha in enumerate(alphas):
                for j, npc in enumerate(npcs):
                    beta, yhat = nb.linalg.ridge(
                        X, Y, alpha, npc=npc, fit_intercept=fit_intercept, X_test=X_test
                    )
                    np.testing.assert_allclose(yhat, yhats[:, :, i, j], atol=1e-10)

    def test_ridge_grid_test_data(self):
        rng = np.random.default_rng(0)
        X = rng.standard_normal((100, 10))
        Y = rng.standard_normal((100, 3))

        alphas = [1e-3, 1, 1e3]
        npcs = [1, 3, 5, 10]

        for fit_intercept in [True, False]:
            yhats = nb.linalg.ridge_grid(
                X, Y, alphas, npcs, fit_intercept=fit_intercept, X_test=None
            )
            assert yhats.shape == (100, 3, 3, 4)
            yhats2 = nb.linalg.ridge_grid(
                X, Y, alphas, npcs, fit_intercept=fit_intercept, X_test=X
            )
            np.testing.assert_allclose(yhats, yhats2, atol=1e-10)

    def test_ridge_grid_test_mask(self):
        rng = np.random.default_rng(0)
        X = rng.standard_normal((100, 10))
        Y = rng.standard_normal((100, 3))
        X_test = rng.standard_normal((10, 10))

        alphas = [1e-3, 1, 1e3]
        npcs = [1, 3, 5, 10]

        test_mask = np.zeros((10,), dtype=bool)
        test_mask[:5] = True
        rng.shuffle(test_mask)
        for fit_intercept in [True, False]:
            yhats = nb.linalg.ridge_grid(
                X,
                Y,
                alphas,
                npcs,
                fit_intercept=fit_intercept,
                X_test=X_test,
                test_mask=test_mask,
            )
            assert yhats.shape == (5, 3, 3, 4)
            yhats2 = nb.linalg.ridge_grid(
                X, Y, alphas, npcs, fit_intercept=fit_intercept, X_test=X_test
            )
            np.testing.assert_allclose(yhats, yhats2[test_mask], atol=1e-10)

        test_mask = rng.choice(10, (10,), replace=True)
        for fit_intercept in [True, False]:
            yhats = nb.linalg.ridge_grid(
                X,
                Y,
                alphas,
                npcs,
                fit_intercept=fit_intercept,
                X_test=X_test,
                test_mask=test_mask,
            )
            assert yhats.shape == (10, 3, 3, 4)
            yhats2 = nb.linalg.ridge_grid(
                X, Y, alphas, npcs, fit_intercept=fit_intercept, X_test=X_test
            )
            np.testing.assert_allclose(yhats, yhats2[test_mask], atol=1e-10)
