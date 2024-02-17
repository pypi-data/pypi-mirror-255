from typing import Any, Dict, Tuple

from openllm_core.utils import (
  DEBUG as DEBUG,
  DEBUG_ENV_VAR as DEBUG_ENV_VAR,
  DEV_DEBUG_VAR as DEV_DEBUG_VAR,
  ENV_VARS_TRUE_VALUES as ENV_VARS_TRUE_VALUES,
  MYPY as MYPY,
  OPTIONAL_DEPENDENCIES as OPTIONAL_DEPENDENCIES,
  QUIET_ENV_VAR as QUIET_ENV_VAR,
  SHOW_CODEGEN as SHOW_CODEGEN,
  LazyLoader as LazyLoader,
  LazyModule as LazyModule,
  ReprMixin as ReprMixin,
  VersionInfo as VersionInfo,
  analytics as analytics,
  calc_dir_size as calc_dir_size,
  check_bool_env as check_bool_env,
  codegen as codegen,
  configure_logging as configure_logging,
  dantic as dantic,
  field_env_key as field_env_key,
  first_not_none as first_not_none,
  flatten_attrs as flatten_attrs,
  gen_random_uuid as gen_random_uuid,
  generate_context as generate_context,
  generate_hash_from_file as generate_hash_from_file,
  get_debug_mode as get_debug_mode,
  get_disable_warnings as get_disable_warnings,
  get_quiet_mode as get_quiet_mode,
  getenv as getenv,
  in_notebook as in_notebook,
  is_autoawq_available as is_autoawq_available,
  is_autogptq_available as is_autogptq_available,
  is_bentoml_available as is_bentoml_available,
  is_bitsandbytes_available as is_bitsandbytes_available,
  is_ctranslate_available as is_ctranslate_available,
  is_flash_attn_2_available as is_flash_attn_2_available,
  is_grpc_available as is_grpc_available,
  is_jupyter_available as is_jupyter_available,
  is_jupytext_available as is_jupytext_available,
  is_notebook_available as is_notebook_available,
  is_peft_available as is_peft_available,
  is_torch_available as is_torch_available,
  is_triton_available as is_triton_available,
  is_transformers_available as is_transformers_available,
  is_vllm_available as is_vllm_available,
  lenient_issubclass as lenient_issubclass,
  resolve_filepath as resolve_filepath,
  resolve_user_filepath as resolve_user_filepath,
  serde as serde,
  set_debug_mode as set_debug_mode,
  set_disable_warnings as set_disable_warnings,
  set_quiet_mode as set_quiet_mode,
  validate_is_path as validate_is_path,
)
from openllm_core.utils.serde import converter as converter

from ._llm import LLM

def available_devices() -> Tuple[str, ...]: ...
def device_count() -> int: ...
def generate_labels(llm: LLM[Any, Any]) -> Dict[str, Any]: ...
