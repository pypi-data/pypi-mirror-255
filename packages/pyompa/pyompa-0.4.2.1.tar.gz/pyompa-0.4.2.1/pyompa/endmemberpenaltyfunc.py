from __future__ import division, print_function
import numpy as np
from .util import assert_in, assert_compatible_keys, assert_has_keys 


def get_linear_penalty_func(slope, intercept=0.0, lowerbound=-np.inf,
                            upperbound=np.inf, magnitudelimit=10000):
    assert upperbound > lowerbound, (upperbound, lowerbound)
    def func(x):
        transformed_x =\
            np.maximum(0, np.maximum(lowerbound-x, x-upperbound))
        constant = (transformed_x > 0.0)*intercept
        return np.minimum(magnitudelimit, constant + slope*transformed_x)
    return func


def get_default_density_linear_penalty_func(slope=100, **kwargs):
    return get_linear_penalty_func(slope=slope, **kwargs)


def get_default_latlon_linear_penalty_func(slope=10, **kwargs):
    return get_linear_penalty_func(slope=slope, **kwargs)


def get_default_depth_linear_penalty_func(slope=1, **kwargs):
    return get_linear_penalty_func(slope=slope, **kwargs)


def get_exp_penalty_func(alpha, beta, lowerbound=-np.inf,
                                 upperbound=np.inf, magnitudelimit=10000):
    #the magnitude limit is there to prevent problems with condition number
    # and optimization later on
    assert upperbound > lowerbound, (upperbound, lowerbound)
    def func(x):
        return np.minimum(magnitudelimit, beta*(np.exp(
         alpha*np.maximum(0, np.maximum(lowerbound-x, x-upperbound)))-1))
    return func
    #return lambda x: np.minimum(magnitudelimit, beta*(np.exp(
    #    alpha*np.maximum(0, np.maximum(lowerbound-x, x-upperbound)))-1))


#same as get_exp_penalty_func but with defaults for alpha and beta
def get_default_density_exp_penalty_func(alpha=0.5, beta=1000, **kwargs):
    return get_exp_penalty_func(
            alpha=alpha, beta=beta, **kwargs) 


#same as get_exp_penalty_func but with defaults for alpha and beta
def get_default_latlon_exp_penalty_func(alpha=0.05, beta=100, **kwargs):
    return get_exp_penalty_func(
            alpha=alpha, beta=beta, **kwargs) 


#same as get_exp_penalty_func but with defaults for alpha and beta
def get_default_depth_exp_penalty_func(alpha=0.001, beta=50, **kwargs):
    return get_exp_penalty_func(
            alpha=alpha, beta=beta, **kwargs) 


#Returns a penalty function that takes an observations data frame as input
# and outputs the total endmember usage penalty on each observation.
#colname_to_penaltyfunc is a mapping from a column in the observations data
# frame to the penalty function associated with that column
def get_combined_penalty_func(colname_to_penaltyfunc):
    def penalty_func(df):
        total_penalty = None
        for colname, penaltyfunc in colname_to_penaltyfunc.items():
            assert colname in df, ("An endmember penalty function specified "
               +str(colname)+" as a column, but no such column is present in"
               +" the observations data frame; the available column headers"
               +" in the observations data frame are "+str(df.columns))
            values = np.array(df[colname])
            penalty = penaltyfunc(values) 
            if (total_penalty is None):
                total_penalty = penalty
            else:
                total_penalty += penalty
        return total_penalty
    return penalty_func


class AbstractPenaltyFunc(object):

    def __init__(self, spec):
        self.spec = spec 
        self.validate_spec()
        self.process_spec()

    def validate_spec(self):
        for colname,spec_for_col in self.spec.items():
            assert_compatible_keys(
              the_dict=spec_for_col,
              allowed=['type', 'lowerbound', 'upperbound']+self.PARAMS,
              errorprefix="Problem with "+str(colname)+" penalty config: ") 
            assert_has_keys(the_dict=spec_for_col, required=["type"],
                            errorprefix="Problem with "+str(colname)
                                        +" penalty config: ")
            assert_in(
                value=spec_for_col['type'],
                allowed=list(self.SPECTYPE_TO_FACTORYFUNC.keys()),
                errorprefix="Problem with type for "
                            +str(colname)+" penalty config; ")

    def process_spec(self):
        colname_to_penaltyfunc = {}
        for colname, spec_for_col in self.spec.items(): 
            factory_func = self.SPECTYPE_TO_FACTORYFUNC[spec_for_col['type']] 
            #gather the arguments going into the factory function
            factory_func_keys = spec_for_col.copy() 
            del factory_func_keys['type']
            penalty_func = factory_func(**factory_func_keys)
            colname_to_penaltyfunc[colname] = penalty_func
        self.penalty_func = get_combined_penalty_func(colname_to_penaltyfunc)

    def __call__(self, *args, **kwargs):
        return self.penalty_func(*args, **kwargs)


class GeneralPenaltyFunc(AbstractPenaltyFunc):

    SPECTYPE_TO_FACTORYFUNC = {
        'linear_density_default': get_default_density_linear_penalty_func,
        'linear_latlon_default': get_default_latlon_linear_penalty_func,
        'linear_depth_default': get_default_depth_linear_penalty_func,
        'linear_other': get_linear_penalty_func,
        'exp_density_default': get_default_density_exp_penalty_func,
        'exp_latlon_default': get_default_latlon_exp_penalty_func,
        'exp_depth_default': get_default_depth_exp_penalty_func,
        'exp_other': get_exp_penalty_func
    }

    PARAMS = ['intercept', 'slope', 'alpha', 'beta']


class EndMemExpPenaltyFunc(AbstractPenaltyFunc):
    
    #mapping from spectype to factory functions that manufacture the
    # penalty functions
    SPECTYPE_TO_FACTORYFUNC = {
        'density_default': get_default_density_exp_penalty_func,
        'latlon_default': get_default_latlon_exp_penalty_func,
        'depth_default': get_default_depth_exp_penalty_func,
        'other': get_exp_penalty_func}

    PARAMS = ['alpha', 'beta']
