import pandas as pd
import numpy as np
import itertools
import warnings
from rpy2.robjects.packages import importr
from rpy2.robjects import FloatVector, numpy2ri, DataFrame

survival = importr('survival')
base = importr('base')
stats = importr('stats')

N_P = 20


def hermite(points, z):
    p1 = 1 / np.pi ** 0.4
    p2 = 0
    for j in range(1, points + 1):
        p3 = p2
        p2 = p1
        p1 = z * np.sqrt(2 / j) * p2 - np.sqrt((j - 1) / j) * p3
    pp = np.sqrt(2 * points) * p2
    return p1, pp


def gauss_hermite_calculation(n, iterlim=50):
    x = np.zeros(n)
    w = np.zeros(n)
    m = (n + 1) // 2
    z = 0
    for i in range(m):
        if i == 0:
            z = np.sqrt(2 * n + 1) - 2 * (2 * n + 1) ** (-1 / 6)
        elif i == 1:
            z = z - np.sqrt(n) / z
        elif i == 2 or i == 3:
            z = 1.9 * z - 0.9 * x[i - 2]
        else:
            z = 2 * z - x[i - 2]
        j = 0
        p = (0, 0)
        for j in range(1, iterlim + 1):
            z1 = z
            p = hermite(n, z)
            z = z1 - p[0] / p[1]
            if np.abs(z - z1) <= np.exp(-15):  # todo: make sure this is how to define the decimal
                break
        if j == iterlim:
            warnings.warn("iteration limit exceeded")
        x[i] = z
        x[n - 1 - i] = -(x[i])
        w[n - 1 - i] = 2 / p[1] ** 2
        w[i] = w[n - 1 - i]
    r = pd.DataFrame({"Points": x * np.sqrt(2), "Weights": w / sum(w)})
    return r


def get_pts_wts(competing_risks, gh, prune=None):
    dm = competing_risks
    pts = create_factor_matrix(dm, gh['Points'])
    wts = create_factor_matrix(dm, gh['Weights'])
    wts = np.prod(wts, axis=1)

    if prune:
        qwt = np.quantile(wts, q=prune)
        pts = pts[wts > qwt]
        wts = wts[wts > qwt]
    return pts, wts


def get_pts_wts2(competing_risks, gh, prune=0.2):
    dm = competing_risks
    pts = create_factor_matrix(dm, gh[0][::-1])
    wts = create_factor_matrix(dm, gh[1])
    wts = np.prod(wts, axis=1)

    if prune:
        qwt = np.quantile(wts, q=prune)
        pts = pts[wts > qwt]
        wts = wts[wts > qwt]
    return pts, wts


def multi_gauss_hermite_calculation(sigma, pts, wts):
    w, v = np.linalg.eig(sigma)
    rot = np.matmul(v, np.diag(np.sqrt(w)))
    pts3 = np.matmul(rot, pts.T).T
    return pts3, list(wts)


def create_factor_matrix(n, values):
    res = []
    someList = []
    for k in range(1, n + 1):
        someList.append(values)
    for elem in itertools.product(*someList):
        res.append(list(elem))
    return np.array([np.array(xi) for xi in res])


def flat_array(arr):
    n = len(arr)
    m = len(arr[0])
    res = np.zeros(n * m)
    for i in range(n):
        for j in range(m):
            res[i * m + j] = arr[i][j]
    return res

#todo: should also be used by Assaf's model
def get_estimators_convergence(old_betas, current_betas, old_frailty_covariance, cuurent_frailty_covariance):
    convergence_betas = np.sum(np.abs(old_betas - current_betas))
    convergence_frailty_covariance = np.sum(np.abs(old_frailty_covariance - cuurent_frailty_covariance))
    return convergence_betas + convergence_frailty_covariance

#todo: should also be used by Assaf's model
def get_hazard_at_event(X, times, cumulative_hazard):
    step_function = stats.stepfun(x=FloatVector(times), y=FloatVector([0] + cumulative_hazard))
    cur_hazard_at_event = numpy2ri.rpy2py(step_function(FloatVector(X)))
    return cur_hazard_at_event


#todo: this should also be used by Assaf's model
def parse_cox_estimators(formula, data, cox_weights):
    try:
        cox_res = survival.coxph(formula, data=DataFrame(data), weights=FloatVector(cox_weights), ties="breslow")
    except Exception as e:
        print("Failed in running survival.coxph, The error is: ", e)

    cur_beta_coefficients = list(cox_res[0])
    cox_fit_obj = survival.coxph_detail(cox_res)
    hazard = cox_fit_obj[4]
    times = cox_fit_obj[0]
    return cur_beta_coefficients, hazard, times


def calculate_conf_interval(estimators, n_competing_risks):
    confidence = (1 - 0.95) / 2
    dim = estimators.shape[2]
    confs = np.empty(shape=(n_competing_risks, dim, 2))
    for i in range(n_competing_risks):
        for j in range(dim):
            confs[i, j, :] = np.percentile(estimators[:, i, j], [100 * confidence, 100 * (1 - confidence)])
    return confs



# #todo: delete all from here after finish debugging
# def e_phase(rowSums, points, weights, hazared_at_event, beta_Z, N, N_Q, N_E, N_P):
#     ret = np.zeros((N_E, N_E))
#     rowSums = rowSums.astype(int)
#     for i in range(N):  # 100
#         devisor = 0
#         PU_varcov = np.zeros((N_E, N_E))
#         for k in range(N_P):
#             integrand = 0
#             for z in range(N_Q):  # 2
#                 in_exp = 0
#                 for j in range(N_E):  # 2
#                     ind = j * N * N_Q + i * N_Q + z
#                     in_exp += points[k * N_E + j] * rowSums[ind] - (hazared_at_event[ind] * np.exp(beta_Z[ind] + points[k * N_E + j]))
#                 integrand += in_exp
#             integrand = np.exp(integrand) * weights[k]
#             devisor += integrand
#             cur_points = points[k * N_E : (k+1) * N_E].reshape(N_E, 1)
#             PU_varcov = PU_varcov + np.dot(cur_points, cur_points.T) * integrand
#         ret = ret + (PU_varcov / devisor)
#     ret = ret/N
#     return ret
#
#
# def calculate_frailty_covariance_estimators_assaf(rowSums, points, weights, hazared_at_event, beta_Z, N, N_Q, N_E, N_P, ans, skip):
#     ret = np.zeros(N * N_E)
#     rowSums = flat_array(rowSums)
#     points = flat_array(points)
#     hazared_at_event = flat_array(hazared_at_event)
#     beta_Z = flat_array(beta_Z)
#     devisor = np.zeros(N)
#     for i in range(N):  # 200
#         for k in range(N_P):  # 8000
#             integrand_in = 0
#             for z in range(N_Q):  # 3
#                 in_exp = 0
#                 for j in range(N_E):  # 12
#                     ind = j * N * N_Q + i * N_Q + z
#                     in_exp += points[k * N_E + j] * rowSums[ind] - (hazared_at_event[ind] * np.exp(
#                         beta_Z[ind] + points[k * N_E + j]))
#                 integrand_in += in_exp
#             integrand = np.exp(integrand_in) * weights[k]
#             devisor[i] += integrand
#             for q in range(N_E):
#                 ret[i * N_E + q] += np.exp(points[k * N_E + q]) * integrand
#     for a in range(N):
#         for b in range(N_E):
#             ret[a * N_E + b] = ret[a * N_E + b] / devisor[a]
#
#     return ret.reshape((N, N_E))
#
#
# def count_type_events(delta):
#     sums = {"0": 0, "1": 0, "2": 0}
#     for twelve in delta:
#         zeros = 0
#         ones = 0
#         twos = 0
#         for three in twelve:
#             if three[0]:
#                 zeros += 1
#             if three[1]:
#                 ones += 1
#             if three[2]:
#                 twos += 1
#         sums["0"] += zeros
#         sums["1"] += ones
#         sums["2"] += twos
#     print(sums)
#     return sums
#
# def save_results_to_files(all_betas, all_sigmas, beta_hat_coef_df, omega_varcov_hat, cumulative_hazard_df):
#     print(f"average betas: {all_betas.mean(axis=0)}")
#     print(f"average sigmas: {all_sigmas.mean(axis=0)}")
#     # save to files:
#     if not os.path.exists('prints'):
#         os.makedirs('prints')
#     file_time = str(datetime.now().strftime("%d-%m__%H-%M"))
#     np.savetxt(f'prints/beta_hat_{file_time}.csv', beta_hat_coef_df, delimiter=', ')
#     np.savetxt(f'prints/omega_varcov_hat_{file_time}.csv', omega_varcov_hat, delimiter=', ')
#     pd.DataFrame(cumulative_hazard_df).to_csv(f'prints/cumulative_hazard_df_{file_time}.csv')
#     all_betas.to_csv(f'prints/all_betas_{file_time}.csv')
#     all_sigmas.to_csv(f'prints/all_sigmas_{file_time}.csv')
#
#
# #todo: delete after refactor of Assaf's model code
# def print_args(n_clusters=500, members=2, comp_risk=2, censoring=False, coefs=[0.5, 2.5],
#                cov=[[1, 0.5], [0.5, 1.5]], n_simulations=100):
#     print("n_simulations: ", n_simulations)
#     print("n_clusters: ", n_clusters)
#     print("members: ", members)
#     print("comp_risk: ", comp_risk)
#     print("censoring: ", censoring)
#     print("coefs: ", coefs)
#     print("cov: ", cov)
#
#
# def print_statistical_results1(beta_hats, sigmas, cums, n_simulations=1000, should_print=True):
#
#     mean_beta = beta_hats.mean(axis=2)
#     var_betas = np.array([np.power(beta_hats[:,:, i] - mean_beta, 2) for i in range(n_simulations)]).sum(axis=0) / (
#                 n_simulations - 1)
#     mean_cums = np.nanmean(cums, axis=3) ## todo - RuntimeWarning: Mean of empty slice
#     var_cums = np.nansum(np.array([np.power(cums[:, :, :, i] - mean_cums, 2) for i in range(n_simulations)]), axis=0) / (
#                 n_simulations - 1)
#
#     mean_sigma = sigmas.mean(axis=2)
#     var_sigmas = np.array([np.power(sigmas[:, :, i] - mean_sigma, 2) for i in range(n_simulations)]).sum(axis=0) / (n_simulations - 1)
#     if should_print:
#         print("mean betas: ", np.round(mean_beta, 4))
#         print("mean sigmas: ", np.round(mean_sigma, 4))
#         print("var_betas: ", np.round(var_betas, 4))
#         print("var_sigmas: ", np.round(var_sigmas, 4))
#
#         # print("CR beta 0: ", np.round(CR_0 / n_simulations, 2))
#         # print("CR beta 1: ", np.round(CR_1 / n_simulations, 2))
#     return mean_beta, mean_sigma, mean_cums, var_betas, var_sigmas, var_cums
