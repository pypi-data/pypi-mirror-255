# from typing import Dict
# from evofr.models.model_spec import ModelSpec
#
#
# class BlackJaxPyMc:
#     @staticmethod
#     def init(key, model: ModelSpec, data: Dict):
#         if not hasattr(model, "pymc_model"):
#             return None, lambda _: None
#         pymc_model = model.pymc_model
#         logdensity_fn = get_jaxified_logp(pymc_model)
#         rvs = [rv.name for rv in pymc_model.value_vars]
#         init_position_dict = pymc_model.initial_point()
#         init_position = [init_position_dict[rv] for rv in rvs]
#         return init_position, logdensity_fn
#
#
# class BlackJaxAesara:
#     @staticmethod
#     def init(key, model: ModelSpec, data: Dict):
#         if hasattr(model, "logprob"):
#
#             def logdensity_fn(position):
#                 flat_position = tuple(position.values())
#                 return model.logprob(*flat_position, **data)
#
#         else:
#
#             def logdensity_fn(position):
#                 return None
#
#         if hasattr(model, "initial_position_fn"):
#             init_position = model.initial_position_fn(key)
#         else:
#             init_position = None
#         return init_position, logdensity_fn
